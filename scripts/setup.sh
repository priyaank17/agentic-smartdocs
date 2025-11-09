#!/bin/bash
npm install
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install pipenv
python -m pipenv install --dev --pre
