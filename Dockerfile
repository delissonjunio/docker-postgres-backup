FROM postgres:10-alpine
MAINTAINER Delisson Silva <delisson@gmail.com>

# Install dependencies
RUN apk update && apk add --no-cache --virtual .build-deps && apk add \
    bash make curl openssh git && apk -Uuv add groff less python3 \
    && python3 -m pip install boto3 awscli && rm /var/cache/apk/*

RUN mkdir /var/app
COPY main.py entry.sh /var/app/

RUN chmod +x /var/app/entry.sh

ENTRYPOINT ["/var/app/entry.sh"]
CMD ["backup"]