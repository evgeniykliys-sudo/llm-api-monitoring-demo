# TODO: llm-api-monitoring-demo

- [x] Написать simulator.py — эндпоинт, метрики, фоновый трафик, имитация инцидентов, JSON-логи
- [x] Настроить Prometheus (scrape config)
- [x] Настроить Grafana (datasource + dashboard provisioning)
- [x] docker-compose up, проверить что все 3 сервиса поднялись
- [x] Проверить дашборд глазами — живые графики подтверждены (RPS, error rate, латентность, ошибки по типу), нашли и починили баг с charset в /metrics
- [ ] Дождаться имитации инцидента на дашборде (~3-5 мин после старта) — визуальное подтверждение скачка
- [x] Залить на GitHub, добавить в FREELANCE.md и резюме
