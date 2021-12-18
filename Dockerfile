FROM ubuntu:20.04

RUN apt-get update
RUN apt-get install -y python3 python3-pip
RUN apt-get install -y git
RUN apt-get install -y mecab

RUN git clone --depth 1 https://github.com/aozorahack/aozorabunko_text.git

RUN pip3 install fugashi[unidic]
RUN python3 -m unidic download

COPY main_simple.py .
COPY phonemes.txt .
RUN python3 main_simple.py