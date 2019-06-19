#!/bin/bash
CMND=$1
if [ -z $CMND ]; then CMND="run"; fi

if [ $CMND = "run" ]; then
    PYTHONPATH=`pwd`/src python src/abstracts.py "${@:2}"
fi

if [ $CMND = "test" ]; then
    PYTHONPATH=`pwd`/src py.test -v -Wignore::DeprecationWarning "${@:2}"
fi
