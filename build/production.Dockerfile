# syntax=docker/dockerfile:1
FROM python:3.8-slim-buster
WORKDIR /app
COPY build/requirements.txt build/requirements.txt
RUN pip3 install -r build/requirements.txt
COPY . .
CMD [ "python", "-m", "roguebot" ]