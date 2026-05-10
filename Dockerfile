FROM python:3.12-slim

WORKDIR /app

# Копируем зависимости отдельно — кэширование слоёв
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код
COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]