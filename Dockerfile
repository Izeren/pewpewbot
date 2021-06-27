FROM python:3.8-alpine
LABEL maintainer="Alex <izeren.ml@gmail.com>" \
      description="Dozor aiogram Telegram bot"

COPY requirements.txt /requirements.txt
RUN apk add --update alpine-sdk && \
    python -m pip install -r /requirements.txt

WORKDIR /app
ENV PYTHONPATH "/app"
COPY ./pewpewbot /app/pewpewbot

CMD ["python", "pewpewbot/bot.py"]