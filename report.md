## 4 балла: Один контейнер

**Команда сборки:**
```bash
docker build -t counter-app .
```

**Команда запуска:**
```bash
docker run -d -p 8080:8000 -e GREETING="Привет, Docker!" --name my-counter counter-app
```

**Проверка работы:**
```bash
$ curl -fsS http://127.0.0.1:8080/
{"greeting": "Привет, Docker!", "count": 0, "hostname": "8dd44d6a43f2", "storage": "sqlite"}
```

**Увеличение счетчика**
```bash
$ curl -fsS -X POST http://127.0.0.1:8080/increment
{"greeting": "Привет, Docker!", "count": 1, "hostname": "8dd44d6a43f2", "storage": "sqlite"}
```

**Проверка готовности хранилища**
```bash
$ curl -fsS http://127.0.0.1:8080/readyz
{"status": "ready", "storage": "sqlite"}
```


**Логи контейнера:**
```text
$ docker logs my-counter
2026-11-19 20:19:21,888 listening port=8000 storage=sqlite
2026-11-19 20:20:01,128 http 172.17.0.1 "GET / HTTP/1.1" 200 -
2026-11-19 20:20:29,142 http 172.17.0.1 "POST / HTTP/1.1" 404 -
2026-11-19 20:20:36,814 http 172.17.0.1 "POST /increment HTTP/1.1" 200 -
```

## 6 баллов: Compose и данные

**Команда запуска:**
```bash
docker compose up -d --build
```

**Проверка исходного состояния:**
```bash
$ curl -fsS http://127.0.0.1:8080/
{"greeting": "Hello, Docker!", "count": 0, "hostname": "503ebaadb67b", "storage": "sqlite"}
```

**Проверка готовности хранилища:**
```bash
$ curl -fsS http://127.0.0.1:8080/readyz
{"status": "ready", "storage": "sqlite"}
```

**Увеличение счётчика 3 раза:**
```bash
$ curl -fsS -X POST http://127.0.0.1:8080/increment
$ curl -fsS -X POST http://127.0.0.1:8080/increment
$ curl -fsS -X POST http://127.0.0.1:8080/increment
```

**Проверка значения после увеличения:**
```bash
$ curl -fsS http://127.0.0.1:8080/
{"greeting": "Hello, Docker!", "count": 3, "hostname": "503ebaadb67b", "storage": "sqlite"}
```

**Остановка и удаление контейнера (без флага -v, чтобы сохранить volume):**
```bash
$ docker compose down
[+] down 2/2
 ✔ Container hw_3_template-app-1  Removed
 ✔ Network hw_3_template_default  Removed
```

**Повторный запуск:**
```bash
$ docker compose up -d
[+] up 2/2
 ✔ Network hw_3_template_default  Created
 ✔ Container hw_3_template-app-1  Started
```

**Проверка значения после перезапуска:**
```bash
$ curl -fsS http://127.0.0.1:8080/
{"greeting": "Hello, Docker!", "count": 3, "hostname": "f293728e10a3", "storage": "sqlite"}
```

## 8 баллов: Отдельное хранилище

**Увеличение счётчика до 4:**
```bash
$ curl -fsS -X POST http://127.0.0.1:8080/increment
{"greeting": "Hello, Docker!", "count": 1, "hostname": "73a4c8e0f06b", "storage": "redis"}

$ curl -fsS -X POST http://127.0.0.1:8080/increment
{"greeting": "Hello, Docker!", "count": 2, "hostname": "73a4c8e0f06b", "storage": "redis"}

$ curl -fsS -X POST http://127.0.0.1:8080/increment
{"greeting": "Hello, Docker!", "count": 3, "hostname": "73a4c8e0f06b", "storage": "redis"}

$ curl -fsS -X POST http://127.0.0.1:8080/increment
{"greeting": "Hello, Docker!", "count": 4, "hostname": "73a4c8e0f06b", "storage": "redis"}
```

**Проверка сохранения данных после пересоздания контейнеров:**
```bash
$ docker compose down
$ docker compose up -d

$ curl -fsS http://127.0.0.1:8080/
{"greeting": "Hello, Docker!", "count": 4, "hostname": "37288f8bed90", "storage": "redis"}
```

**Проверка работы приложения при остановленном Redis:**
```bash
$ docker compose stop redis

$ curl -fsS http://127.0.0.1:8080/healthz
{"status": "alive"}

$ curl -fsS http://127.0.0.1:8080/readyz
curl: (22) The requested URL returned error: 503

$ curl -fsS -X POST http://127.0.0.1:8080/increment
curl: (22) The requested URL returned error: 503
```

**Проверка восстановления Redis без перезапуска приложения:**
```bash
$ docker compose start redis

$ curl -fsS http://127.0.0.1:8080/
{"greeting": "Hello, Docker!", "count": 4, "hostname": "37288f8bed90", "storage": "redis"}

$ curl -fsS -X POST http://127.0.0.1:8080/increment
{"greeting": "Hello, Docker!", "count": 5, "hostname": "37288f8bed90", "storage": "redis"}
```

## 10 баллов: Проверка восстановления

**Два запуска скрипта подряд:**

```text
$ python scripts/check.py
[+] up 5/5
 ✔ Volume check-2380819459_redis_data Created
 ✔ Container check-2380819459-redis-1 Healthy
 ✔ Container check-2380819459-app-1 Healthy
[+] stop 1/1
 ✔ Container check-2380819459-app-1 Stopped
[+] remove 1/1
 ✔ Container check-2380819459-app-1 Removed
[+] up 1/1
 ✔ Container check-2380819459-app-1 Healthy
[+] stop 1/1
 ✔ Container check-2380819459-redis-1 Stopped
[+] start 1/1
 ✔ Container check-2380819459-redis-1 Healthy
OK
[+] copy 1/1
 ✔ check-2380819459-redis-1 Copied check-2380819459-redis-1:/data/dump.rdb to backup-check-2380819459.rdb
Резервная копия: backup-check-2380819459.rdb
[+] down 4/4
 ✔ Volume check-2380819459_redis_data Removed

$ python scripts/check.py
[+] up 5/5
 ✔ Volume check-1509241858_redis_data Created
 ✔ Container check-1509241858-redis-1 Healthy
 ✔ Container check-1509241858-app-1 Healthy
[+] stop 1/1
 ✔ Container check-1509241858-app-1 Stopped
[+] remove 1/1
 ✔ Container check-1509241858-app-1 Removed
[+] up 1/1
 ✔ Container check-1509241858-app-1 Healthy
[+] stop 1/1
 ✔ Container check-1509241858-redis-1 Stopped
[+] start 1/1
 ✔ Container check-1509241858-redis-1 Healthy
OK
[+] copy 1/1
 ✔ check-1509241858-redis-1 Copied check-1509241858-redis-1:/data/dump.rdb to backup-check-1509241858.rdb
Резервная копия: backup-check-1509241858.rdb
[+] down 4/4
 ✔ Volume check-1509241858_redis_data Removed
```