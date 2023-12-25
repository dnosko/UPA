#!/bin/bash

PWD=`pwd`
VENV="venv"
PYTHON=$VENV/bin/python3
PIP=$VENV/bin/pip

python3 -m venv $VENV
source $PWD/$VENV/bin/activate
pip install -r requirements.txt