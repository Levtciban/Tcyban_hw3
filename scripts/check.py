import subprocess
import random
import http.client
import json
import os

def request(port, method, path):
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
    try:
        connection.request(method, path)
        responce = connection.getresponse()

        http_code = responce.status
        data = json.loads(responce.read())

        return http_code, data
    finally:
        connection.close()

def check_count(port, expected_n=0, expected_http_code=200):
    http_code, data = request(port, "GET", "/")

    if http_code != expected_http_code:
        raise RuntimeError(f"HTTP request returned {http_code} but {expected_http_code} expected")

    if data["count"] != expected_n:
        raise RuntimeError(f"Count equals to {data['count']} but {expected_n} expected")

def check_code(port, path, method, expected_http_code=200):
    http_code, data = request(port, method, path)

    if http_code != expected_http_code:
        raise RuntimeError(f"HTTP request returned {http_code} but {expected_http_code} expected, path={path}, method={method}")

try:
    stage="создание проекта"

    port = random.randint(20000, 60000)
    os.environ["HOST_PORT"] = str(port)
    os.environ["STORAGE"] = "redis"

    project = f"check-{random.randint(10 ** 9, 10 ** 10 - 1)}" 

    subprocess.run(["docker", "compose", "-p", project, "up", "-d", "--wait", "--wait-timeout", "30"], check=True)

    stage = "проверка POST /increment"

    check_count(port)

    N = 5

    for i in range(N):
        request(port, "POST", "/increment")

    check_count(port, N)

    stage = "пересоздание проекта"

    subprocess.run(["docker", "compose", "-p", project, "stop", "app"], check=True)
    subprocess.run(["docker", "compose", "-p", project, "rm", "-f", "app"], check=True)
    subprocess.run(["docker", "compose", "-p", project, "up", "-d", "--no-deps", "--wait", "--wait-timeout", "30", "app"], check=True)

    check_count(port, N)

    stage = "выключение redis"

    subprocess.run(["docker", "compose", "-p", project, "stop", "redis"], check=True)

    stage = "проверка после выключения redis"

    check_code(port, "/healthz", "GET")
    check_code(port, "/readyz", "GET", 503)
    check_code(port, "/increment", "POST", 503)

    stage = "перезапуск redis"

    subprocess.run(["docker", "compose", "-p", project, "start", "redis", "--wait", "--wait-timeout", "30"], check=True)

    stage = "проверка после перезапуска redis"

    check_count(port, N)
    check_code(port, "/increment", "POST", 200)
    check_count(port, N + 1)

    stage = "резервная копия"

    subprocess.run(
        ["docker", "compose", "-p", project, "exec", "-T", "redis", "redis-cli", "SAVE"],
        check=True
    )

    backup_file = "backup-" + project + ".rdb"

    subprocess.run(
        ["docker", "compose", "-p", project, "cp", "redis:/data/dump.rdb", backup_file],
        check=True
    )

    print("Резервная копия:", backup_file)
except:
    raise RuntimeError(f"скрипт завершился с ошибкой на этапе {stage}")
finally:
    subprocess.run(["docker", "compose", "-p", project, "down", "-v"], check=True)
