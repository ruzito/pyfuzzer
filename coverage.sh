#!/bin/bash
export PYTHONPATH=`pwd`/src:`pwd`/tests
# pytest --cov=src tests/
coverage run -m pytest tests/ --hypothesis-profile cover
coverage html --omit="tests/*" > /dev/null
coverage xml > /dev/null
coverage json > /dev/null
coverage report --omit="tests/*"