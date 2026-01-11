FROM python:3.11-slim AS builder

WORKDIR /app

RUN ln -s /usr/local/bin/python3 /usr/bin/python3 && \
    /usr/bin/python3 -m venv /app/venv

COPY requirements.txt .

RUN /app/venv/bin/pip install --no-cache-dir -r requirements.txt

FROM gcr.io/distroless/python3-debian12:debug

WORKDIR /

COPY --from=builder /app/venv /app/venv

# make venv python binary first in path
ENV PATH="/app/venv/bin:$PATH"

# resolves to /app/venv/bin/python => /usr/bin/python3
ENTRYPOINT ["python3"]

COPY .env .env

COPY ./app/ /app/

CMD ["/app/venv/bin/uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]