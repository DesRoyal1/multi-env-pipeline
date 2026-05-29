FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

ENV DYNAMODB_TABLE=products-prod

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
