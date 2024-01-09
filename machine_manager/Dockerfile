FROM ubuntu:latest

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    docker.io

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY src /app/src
COPY config.json /app/config.json

CMD ["python3", "src/machine_manager.py", "/app/config.json"]