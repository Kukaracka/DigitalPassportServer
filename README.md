# Электронная сервисная книга "DigitalPassport" — Серверная часть

Бэкенд-приложение на **FastAPI**, обеспечивающее работу API, интеграцию с базой данных PostgreSQL и объектным хранилищем MinIO. Полностью упаковано в Docker и настроено для автоматического деплоя через CI/CD.

## 🚀 Быстрый старт (Разработка)

1. **Создайте виртуальное окружение:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # для Linux/macOS
   venv\Scripts\activate     # для Windows
   ```

2. **Установите зависимости:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Запустите проект локально:**
   ```bash
   uvicorn src.main:app --reload
   ```

---

## 🏗 Развертывание на сервере (Production)

Для работы используется связка **Docker Compose** и образы из **GitHub Container Registry (GHCR)**.

### 1. Требования
*   Docker и Docker Compose
*   Наличие SSL-сертификатов (папка `./ssl`)
*   Настроенные секреты в GitHub Actions для автодеплоя

### 2. Подготовка окружения
Создайте в корне проекта файл `.env` (на основе `src/.env`). Этот файл содержит чувствительные данные и **не попадает** в репозиторий:

*   `DB_USER`, `DB_PASSWORD`, `DB_NAME` — доступы к PostgreSQL.
*   `MINIO_ACCESS_KEY`, `MINIO_SECRET_KEY` — ключи доступа к MinIO.
*   `SECRET_KEY` — секретный ключ для JWT-авторизации.

### 3. Запуск стека
Если вы разворачиваете проект вручную:

```bash
# Авторизация в реестре GitHub
echo \$YOUR_TOKEN | docker login ghcr.io -u YOUR_USERNAME --password-stdin

# Запуск всех сервисов (Бэкенд, БД, MinIO)
docker compose up -d
```

---

## 📁 Структура проекта

*   `/src` — исходный код (FastAPI, SQLAlchemy модели, бизнес-логика).
*   `/ssl` — директория с сертификатами `key.pem` и `cert.pem` для HTTPS.
*   `.env` — файл с переменными окружения (игнорируется Git).
*   `.github/workflows` — конфигурация CI/CD пайплайна (сборка и деплой).
*   `docker-compose.yml` — описание контейнеров и связей между ними.

---

## 🛠 Полезные команды

*   **Посмотреть логи бэкенда:** `docker compose logs -f backend`
*   **Проверить статус контейнеров:** `docker compose ps`
*   **Принудительно обновить только бэкенд:** 
    ```bash
    docker compose pull backend && docker compose up -d backend
    ```
*   **Очистить систему от старых образов:** `docker image prune -f`

---
📦 *Сборка и пуш образов происходят автоматически при каждом коммите в ветку `main`.*
