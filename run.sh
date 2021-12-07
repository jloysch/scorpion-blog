#!/bin/sh
python3 -m venv ENVIRONMENT
. ENVIRONMENT/bin/activate
export FLASK_APP=base.py
flask run
