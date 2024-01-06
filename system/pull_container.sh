#!/bin/bash
cd ..
docker image build -t alemosk/gnucash-web --build-arg VERSION=0.1.0 .
docker image tag alemosk/gnucash-web alemosk/gnucash-web:latest
docker image push alemosk/gnucash-web:latest
