#!/bin/bash
export PYTHONPATH=`pwd`/src:`pwd`/tests

pytest -v tests/ --hypothesis-profile explain