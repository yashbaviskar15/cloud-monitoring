FROM python:3.10-slim

WORKDIR /app

# Copy demo-app source code
COPY demo-app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY demo-app/app.py .

# Copy dashboard directory for the /dashboard route
COPY dashboard/ ./dashboard/

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]
