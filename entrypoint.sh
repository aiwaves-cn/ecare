#!/bin/bash

echo "start service ai_character"

PID_FILE="/var/run/gunicorn.pid"
echo "Running app ai_character..."
rm -f $PID_FILE
gunicorn -p $PID_FILE