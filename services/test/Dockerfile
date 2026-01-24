# Test Dockerfile for CI verification
FROM python:latest

# This should trigger DL3045 (COPY with --chmod requires BuildKit)
COPY . /app

WORKDIR /app

# Using shell form instead of exec form - should trigger DL3025
CMD python app.py
