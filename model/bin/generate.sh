#!/bin/bash

# Usage: ./bin/generate.sh prompt.yaml

PROMPT=$1

python -m trainer.textgen \
    --prompt $PROMPT

