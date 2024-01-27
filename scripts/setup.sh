#!/bin/bash

chmod +x ./run
chmod +x ./scripts/*.sh
curl -sSL https://install.python-poetry.org | POETRY_HOME="`pwd`/.poetry" python3 -

./.poetry/bin/poetry install --no-root

# pip install -r requirements.txt