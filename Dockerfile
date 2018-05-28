FROM python:2.7.15-alpine

MAINTAINER Sreejith Kesavan <sreejithemk@gmail.com>

RUN apk add --update build-base python-dev libev-dev \
	&& wget -c https://github.com/semk/wsnotifier/archive/master.zip \
	&& pip install master.zip \
	&& rm -rf master.zip \
	&& apk del build-base python-dev libev-dev \
	&& rm -rf /var/cache/apk/*

CMD ["wsnotifier"]