#!/bin/bash
trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT

python -c 'from neira_flask import worker; worker.listen_for_jobs()' &

gunicorn --config gunicorn.conf.py neira_flask.main:app

