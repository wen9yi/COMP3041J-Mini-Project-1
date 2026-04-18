# Data Service Dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app
ENV FLASK_APP=api.py
EXPOSE 5002
CMD ["python", "api.py"]
