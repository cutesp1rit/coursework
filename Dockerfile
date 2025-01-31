FROM python:3.10

RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
    
RUN pip install --upgrade pip

ENV BOT_NAME=tg_bot

WORKDIR /usr/src/app/tg_bot
COPY requirements.txt /usr/src/app/tg_bot
RUN pip install -r /usr/src/app/tg_bot/requirements.txt
COPY . /usr/src/app/tg_bot