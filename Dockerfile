FROM python:3.8

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y tcpdump tshark

RUN pip install ipython flask pyshark inotify

RUN mkdir /app
WORKDIR /app

COPY netcap.py .
COPY server.py .
COPY templates templates
COPY static static

ENTRYPOINT /app/netcap.py
