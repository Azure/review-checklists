FROM ubuntu:18.04
MAINTAINER Jose Moreno "jose.moreno@microsoft.com"

RUN apt-get update -y && apt-get install -y python3-pip python3-dev build-essential curl libssl1.0.0 libssl-dev libpq-dev
COPY . /app
WORKDIR /app
RUN pip3 install -r requirements.txt
CMD ["sh", "-c", "python3 ./app.py"]

EXPOSE 5000