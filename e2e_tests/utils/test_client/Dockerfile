FROM ubuntu:latest

# Install python and pip using apt

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-setuptools \
    python3-venv \
    && apt-get clean

# Install docker and requests  using pip

RUN pip3 install docker requests pytest