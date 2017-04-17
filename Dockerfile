FROM ubuntu:latest

COPY ./server.conf .
COPY ./occur ./occur

RUN \
apt-get update && \
apt-get install -y python3-cherrypy3 && \
apt-get install -y python3-requests 

CMD python3 ./occur/main.py

