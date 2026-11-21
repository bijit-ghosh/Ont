FROM python:3.12-slim
WORKDIR /app
COPY requirements.lock.txt .
RUN pip install --no-cache-dir -r requirements.lock.txt && useradd --uid 10001 --create-home ont
COPY ont ./ont
COPY web ./web
RUN chmod -R a+rX /app/ont /app/web && mkdir /app/data && chown ont:ont /app/data
USER ont
EXPOSE 3000
CMD ["python", "-m", "uvicorn", "ont.app:app", "--host", "0.0.0.0", "--port", "3000"]
