#!/bin/bash
trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT

python neira_flask/worker.py &

gunicorn --config gunicorn.conf.py neira_flask.main:app

