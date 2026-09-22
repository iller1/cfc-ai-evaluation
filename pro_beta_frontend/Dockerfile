FROM python:3.13-slim
WORKDIR /app
COPY pro_beta_frontend /app/pro_beta_frontend
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080
EXPOSE 8080
CMD ["python","-m","pro_beta_frontend.server"]
