#!/bin/bash

if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <email_subject> <email_body> <email_receiver>"
    exit 1
fi

SUBJECT=$1
BODY=$2
RECEIVER=$3

python3 sendmail.py -c mail-config.json -s "$SUBJECT" -m "$BODY" "$RECEIVER"
