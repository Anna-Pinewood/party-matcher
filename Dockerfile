FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

COPY .env .env

# Запустите приложение
CMD ["python", "-u", "src/main.py"]