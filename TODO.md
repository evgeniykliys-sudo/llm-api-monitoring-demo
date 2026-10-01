# TODO: llm-api-monitoring-demo

- [x] Написать simulator.py — эндпоинт, метрики, фоновый трафик, имитация инцидентов, JSON-логи
- [x] Настроить Prometheus (scrape config)
- [x] Настроить Grafana (datasource + dashboard provisioning)
- [x] docker-compose up, проверить что все 3 сервиса поднялись
- [x] Проверить дашборд глазами — живые графики подтверждены (RPS, error rate, латентность, ошибки по типу), нашли и починили баг с charset в /metrics
- [x] Дождаться имитации инцидента на дашборде (~3-5 мин после старта) — подтверждено 2026-10-01: в логах симулятора появились записи incident_mode:true с латентностью 2.8-5.5с (норма 150-800мс), llm_errors_total выросли (timeout 1→4, rate_limit 0→5), Prometheus rate(...) посчитал error rate ~4.3% за эти 2 минуты — вся цепочка simulator → Prometheus подтверждена живыми данными
- [x] Залить на GitHub, добавить в FREELANCE.md и резюме
