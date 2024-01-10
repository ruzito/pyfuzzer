#!/bin/bash

export PYTHONPATH=`pwd`/src:`pwd`/tests
python src/fuzzer.py $@