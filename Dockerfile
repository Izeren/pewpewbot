FROM python:3.8-alpine
LABEL maintainer="Alex <izeren.ml@gmail.com>" \
      description="Dozor aiogram Telegram bot"

RUN apk add --update alpine-sdk && \
    python -mpip install aiogram marshmallow python-json-logger decorator

ENV PYTHONPATH "${PYTHONPATH}:/usr/bin/python:/app"

EXPOSE 4545
WORKDIR /app

CMD ["tail", "-f", "/dev/null"]