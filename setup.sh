#!/bin/bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e .
python -m unittest discover -s tests
pip freeze > requirements.txt
python src/app/cli.py
