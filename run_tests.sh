#!/bin/bash
export PYTHONPATH=$PYTHONPATH:$(pwd):$(pwd)/shared/shared
export TESTING=True
export RABBITMQ_URL="amqp://guest:guest@localhost:5672/"
export REDIS_HOST="localhost"
export REDIS_PORT="6379"
python -m pytest --cov=. --cov-report=xml
python -m unittest processing_service/core/test_card_data_fetcher.py
