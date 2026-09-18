import asyncio
import json
import logging
import random
import sys
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stdout)
logger = logging.getLogger("llm-api-sim")

REQUESTS_TOTAL = Counter("llm_requests_total", "Всего запросов к симулированному LLM API", ["status"])
ERRORS_TOTAL = Counter("llm_errors_total", "Ошибки по типу", ["error_type"])
REQUEST_DURATION = Histogram(
    "llm_request_duration_seconds",
    "Длительность запроса к симулированному LLM API",
    buckets=(0.1, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 5.0, 8.0),
)

# Глобальный флаг "идёт инцидент" — фоновая задача переключает его по таймеру
_incident_mode = {"active": False}

BASE_ERROR_RATE = 0.03  # 3% ошибок в норме
INCIDENT_ERROR_RATE = 0.45  # 45% ошибок во время инцидента

BASE_LATENCY_RANGE = (0.15, 0.9)
INCIDENT_LATENCY_RANGE = (2.0, 6.0)


def _log(event: dict):
    logger.info(json.dumps(event, ensure_ascii=False))


async def simulate_request() -> dict:
    """Один симулированный вызов LLM API — с реалистичным распределением задержки и ошибок."""
    request_id = str(uuid.uuid4())[:8]
    incident = _incident_mode["active"]

    error_rate = INCIDENT_ERROR_RATE if incident else BASE_ERROR_RATE
    latency_range = INCIDENT_LATENCY_RANGE if incident else BASE_LATENCY_RANGE

    duration = random.uniform(*latency_range)
    await asyncio.sleep(duration)

    is_error = random.random() < error_rate
    error_type = None

    if is_error:
        error_type = random.choices(
            ["rate_limit", "timeout", "server_error"],
            weights=[0.5, 0.3, 0.2],
        )[0]
        REQUESTS_TOTAL.labels(status="error").inc()
        ERRORS_TOTAL.labels(error_type=error_type).inc()
    else:
        REQUESTS_TOTAL.labels(status="success").inc()

    REQUEST_DURATION.observe(duration)

    event = {
        "request_id": request_id,
        "status": "error" if is_error else "success",
        "duration_ms": round(duration * 1000),
        "incident_mode": incident,
    }
    if error_type:
        event["error_type"] = error_type

    _log(event)
    return event


async def traffic_generator():
    """Фоновая задача — имитирует постоянный поток запросов к API от разных клиентов."""
    while True:
        await simulate_request()
        await asyncio.sleep(random.uniform(0.3, 1.2))


async def incident_scheduler():
    """Раз в 3-5 минут включает 'режим инцидента' на 20-30 секунд."""
    while True:
        await asyncio.sleep(random.uniform(180, 300))
        _incident_mode["active"] = True
        _log({"event": "incident_started"})

        await asyncio.sleep(random.uniform(20, 30))
        _incident_mode["active"] = False
        _log({"event": "incident_resolved"})


@asynccontextmanager
async def lifespan(app: FastAPI):
    traffic_task = asyncio.create_task(traffic_generator())
    incident_task = asyncio.create_task(incident_scheduler())
    yield
    traffic_task.cancel()
    incident_task.cancel()


app = FastAPI(lifespan=lifespan)


@app.post("/v1/complete")
async def complete():
    result = await simulate_request()
    status_code = 200 if result["status"] == "success" else (429 if result.get("error_type") == "rate_limit" else 500)
    return Response(content=json.dumps(result), status_code=status_code, media_type="application/json")


@app.get("/metrics")
async def metrics():
    content_type = CONTENT_TYPE_LATEST.split(";")[0].strip()
    return Response(content=generate_latest(), media_type=content_type)
