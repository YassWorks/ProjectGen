FROM python:3.13-alpine

# no pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# no buffering stdout and stderr
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apk add --no-cache \
    build-base \
    && rm -rf /var/cache/apk/*

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

# this is purely for testing purposes
# no non-privileged user cuz i wanna check stuff out inside the container

COPY app/ ./app/

EXPOSE 8000

CMD ["sudo", "python", "main.py"]