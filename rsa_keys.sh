#!/bin/sh

mkdir src/core/certs && \
openssl genrsa -out src/core/certs/jwt-private.pem 2048 && \
openssl rsa -in src/core/certs/jwt-private.pem -pubout -out src/core/certs/jwt-public.pem