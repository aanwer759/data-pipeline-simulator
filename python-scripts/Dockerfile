FROM python:3.12.12

COPY . /app

WORKDIR /app

RUN pip3 install kafka-python

CMD python3 device-simulator.py