FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install flask pytest gunicorn

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
