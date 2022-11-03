#!/bin/bash
source ./venv/bin/activate
env $(cat .env | xargs) python3 nsx-3.py