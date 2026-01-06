FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["streamlit", "run", "app_day3.py", "--server.port=8501", "--server.address=0.0.0.0"]
EXPOSE 8501