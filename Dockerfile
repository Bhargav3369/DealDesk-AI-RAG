FROM python:3.11-slim
WORKDIR /app

# Ensure we have our pip dependencies built
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Bring over root RAG scripts and the backend code
COPY . .

# Run the API locally over port 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
