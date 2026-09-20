FROM python:3.13-slim

WORKDIR /app

RUN python -m pip install --no-cache-dir "psycopg[binary]>=3.2,<4" "PyJWT[crypto]>=2.10,<3"

COPY pro_beta /app/pro_beta

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

EXPOSE 8080

CMD ["python", "-m", "pro_beta.http_server"]
