#!/bin/bash
trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT

#python -c 'from neira_flask import worker; worker.listen_for_jobs()' &
python neira_flask/worker.py &

gunicorn --config gunicorn.conf.py neira_flask.main:app

