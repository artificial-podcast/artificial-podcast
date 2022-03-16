#!/bin/bash

# Usage: ./bin/generate.sh prompt.yaml

PROMPT=$1

python -m trainer.generate \
    --prompt $PROMPT \
    --disable-download True