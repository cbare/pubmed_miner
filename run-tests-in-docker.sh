#!/bin/bash

docker run --rm -it \
    -e PYTHONPATH=/app/src \
    --name pubmed_miner \
    christopherbare/pubmed_miner:latest \
    test "${@:2}"
