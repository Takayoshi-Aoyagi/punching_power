#!/bin/bash

#PYTHON=/usr/bin/python
PYTHON=/home/pi/.pyenv/versions/3.7.10/bin/python

cd $(dirname "$0")

$PYTHON main.py
