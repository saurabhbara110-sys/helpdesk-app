FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt .

#executes while building the image
RUN pip install --no-cache-dir -r requirements.txt

#executes once the container start
COPY app.py db.py ./

COPY frontend/ ./frontend

COPY templates/ ./templates

EXPOSE 5000

CMD ["python","app.py"]
