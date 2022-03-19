#!/bin/bash

# Usage: ./bin/generate.sh prompt.yaml

rm -rf ./cache/checkpoint

PROMPT=$1

DATE=`date '+%Y%m%d_%H%M%S'`

python -m trainer.textgen \
    --prompt $PROMPT \
    --id $DATE
