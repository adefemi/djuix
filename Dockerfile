FROM ubuntu:20.04

# Install unzip
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    python3.9 \
    python3-pip \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    build-essential \
    libpython3.9-dev \
    unzip \
    ssh

# Create a symbolic link from python to python3
RUN ln -s /usr/bin/python3 /usr/bin/python
RUN pip install virtualenv

RUN mkdir /djuix

WORKDIR /djuix

COPY . /djuix/

COPY ./djuix /root/.ssh/id_rsa

RUN pip install --upgrade pip && pip install pip-tools && pip install -r requirements.txt 