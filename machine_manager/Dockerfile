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
COPY linters.json /app/linters.json

CMD ["python3", "src/app.py", "/app/config.json", "/app/linters.json"]