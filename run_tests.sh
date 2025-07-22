#!/bin/bash
export PYTHONPATH=$PYTHONPATH:$(pwd):$(pwd)/shared/shared
export TESTING=True
python -m pytest job_service/test_jobs.py
python -m pytest processing_service/test_core_image_processing.py
python -m pytest processing_service/test_image_processing.py
python -m pytest processing_service/test_image_processing_logic.py
python -m pytest auth_service/test_auth.py
