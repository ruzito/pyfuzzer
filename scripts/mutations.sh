#!/bin/bash
export PYTHONPATH=`pwd`/src:`pwd`/tests
mutmut run --runner="pytest tests/ --hypothesis-profile cover"