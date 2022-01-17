FROM ubuntu:xenial-20210114

RUN apt-get update \
	&&  apt-get -y install postgresql

WORKDIR /usr/src/app
COPY . .
