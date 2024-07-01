FROM python:3.8-slim-buster
WORKDIR /app
COPY requirements.txt requirements.txt
COPY entrypoint.py entrypoint.py
RUN pip3 install -r requirements.txt
ENTRYPOINT ["python3", "/app/entrypoint.py"]