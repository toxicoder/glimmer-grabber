#!/bin/bash
export PYTHONPATH=$PYTHONPATH:$(pwd)
export TESTING=True
python -m pytest job_service/test_jobs.py
