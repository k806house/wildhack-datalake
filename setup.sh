#!/bin/bash

pip3 install -r requirements.txt
crontab -l | { cat; echo "0 0 * * * /usr/bin/python3 ${PWD}/kam24.py > /tmp/kam24.log 2>&1"; } | crontab -
crontab -l | { cat; echo "0 0 * * * /usr/bin/python3 ${PWD}/kamtoday.py > /tmp/kamtoday.log 2>&1"; } | crontab -
crontab -l | { cat; echo "30 0 * * * /usr/bin/python3 ${PWD}/merge.py > /tmp/merge.log 2>&1"; } | crontab -