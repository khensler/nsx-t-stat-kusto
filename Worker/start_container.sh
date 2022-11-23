#!/bin/bash
sed -i "s~##CLOUDID##~$AVS_CLOUD_ID~" /etc/systemd/system/nsx-stat.service
systemctl daemon-reload
source ./venv/bin/activate
python3 main.py
#env $(cat .env | xargs) python3 main.py