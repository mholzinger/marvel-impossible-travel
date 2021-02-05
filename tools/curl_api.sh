#!/bin/bash

source .apikeys

ts=$(date +%s)
hash=$(md5 -q -s "$ts""$MARVEL_PRIVKEY""$MARVEL_PUBKEY")

REST_ENDPOINT="$1"

curl -sGH \"Accept: application/json\" \
 "$REST_ENDPOINT" \
 -d apikey=$MARVEL_PUBKEY \
 -d ts=$ts \
 -d hash=$hash
