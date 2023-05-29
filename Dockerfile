FROM python:3.11-alpine3.18
LABEL Description="DSK Telegram Bot" Vendor="K.I."

COPY dskbot dskbot
COPY requirements.txt ./

RUN apk update && apk upgrade -f && \
    addgroup -S app && adduser -S -D -G app app && \
    pip install --no-cache-dir --upgrade pip wheel && \
    pip install --no-cache-dir --requirement requirements.txt

USER app

CMD ["python3", "-m", "dskbot"]
