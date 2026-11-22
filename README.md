# ДЗ по Docker

## Запуск через Compose

**Настройки:**

```bash
cp .env.example .env
```

В `.env` можно изменить `HOST_PORT` (порт на компьютере), `PORT` (порт приложения) и `GREETING` (приветствие). По умолчанию приложение доступно на порту `8080`.

**Сборка и запуск:**

```bash
docker compose up -d --build
```

**Проверка:**

```bash
curl -fsS http://127.0.0.1:8080/
curl -fsS -X POST http://127.0.0.1:8080/increment
docker compose logs app
```

**Автоматическая проверка для 10 баллов:**

```bash
python scripts/check.py
```

Команды и результаты проверок, включая два запуска скрипта подряд, приведены в [отчёте](report.md).

**Остановка:**

```bash
docker compose down
```