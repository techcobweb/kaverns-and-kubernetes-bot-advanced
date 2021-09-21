# syntax=docker/dockerfile:1
FROM python:3.8-slim-buster
WORKDIR /app

# ARG USER_ID
# ARG GROUP_ID
# RUN addgroup --gid $GROUP_ID user
# RUN adduser --disabled-password --gecos '' --uid $USER_ID --gid $GROUP_ID user
# USER user

COPY build/ build 
COPY . .
RUN ./setup.sh

CMD [ "test.sh" ]