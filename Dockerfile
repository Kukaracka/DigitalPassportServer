# --------BUILD-----------

FROM python:3.13-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

WORKDIR /app

RUN uv venv /.venv

ENV PATH="/.venv/bin:$PATH"

COPY requirements.txt .

RUN uv pip install --no-cache-dir -r requirements.txt

# --------FINAL-----------

FROM python:3.13-slim AS runner

WORKDIR /app

COPY --from=builder /.venv /.venv

ENV PATH="/.venv/bin:$PATH"

COPY src ./src
COPY pytest.ini ./

WORKDIR /app/src

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
