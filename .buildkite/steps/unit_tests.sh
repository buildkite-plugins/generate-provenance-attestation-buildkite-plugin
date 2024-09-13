#!/bin/sh

apk add openssl

python3 -m unittest tests/*.py
