#!/bin/bash

export PYTHONPATH=`pwd`/src:`pwd`/tests
# pytest --cov=src tests/
./.poetry/bin/poetry run coverage run -p -m pytest tests/ --hypothesis-profile cover
# Add test suites here to increase coverage
# ./.poetry/bin/poetry run coverage run -p -m pytest tests/ --hypothesis-profile cover
# ./.poetry/bin/poetry run coverage run -p -m pytest tests/ --hypothesis-profile cover
# ./.poetry/bin/poetry run coverage run -p -m pytest tests/ --hypothesis-profile cover
./.poetry/bin/poetry run coverage combine
./.poetry/bin/poetry run coverage html --omit="tests/*" > /dev/null
./.poetry/bin/poetry run coverage xml > /dev/null
./.poetry/bin/poetry run coverage json > /dev/null
./.poetry/bin/poetry run coverage report --omit="tests/*"