#!/bin/bash

docker run --rm \
    -e PYTHONPATH=/app/src \
    --name pubmed_miner \
    christopherbare/pubmed_miner:latest \
    run "$@"
