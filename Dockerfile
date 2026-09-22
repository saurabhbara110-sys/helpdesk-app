FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt .

#executes while building the image
RUN pip install -r requirements.txt

#executes once the container start
COPY app.py db.py ./

COPY frontend/ ./frontend

EXPOSE 5000

CMD ["python","app.py"]
