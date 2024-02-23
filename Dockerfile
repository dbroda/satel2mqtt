FROM ubuntu:22.04

WORKDIR /app


RUN apt update
RUN apt upgrade -y
RUN apt install -y python3-paho-mqtt python3-serial

COPY satel.py /app


CMD ["python3", "-u", "./satel.py"]
