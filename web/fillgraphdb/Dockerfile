FROM ubuntu:18.04
MAINTAINER Jose Moreno "jose.moreno@microsoft.com"

RUN apt-get update -y && apt-get install -y python3-pip python3-dev build-essential curl libssl1.0.0 libssl-dev libpq-dev gir1.2-secret-1
COPY . /app
WORKDIR /app
RUN pip3 install -r requirements.txt
CMD ["sh", "-c", "python3 graph_db.py"]
