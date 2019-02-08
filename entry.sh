#!/bin/bash

MODE_ARG=''

if [ "$1" = "backup" ]; then
    MODE_ARG='-b'
elif [ "$1" = "restore" ]; then
    MODE_ARG='-r'
fi

S3_ARGS=''
if [ ! -z "$S3_PREFIX" ]; then
    S3_ARGS="--s3-prefix '$S3_PREFIX'"
elif [ ! -z "$S3_KEY" ]; then
    S3_ARGS="--s3-key '$S3_KEY'"
fi

COMPRESSED=''
if [ ! -z "$COMPRESSED" ]; then
    COMPRESSED='--compressed'
fi

python3 /var/app/main.py "$MODE_ARG" --database "$DB_NAME" --user "$DB_USER" --host "$DB_HOST" --s3-bucket "$S3_BUCKET" $S3_ARGS $COMPRESSED