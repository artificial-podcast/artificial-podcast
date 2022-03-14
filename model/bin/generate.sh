#!/bin/bash

# Usage: ./bin/generate.sh shakespeare 100 "ROMEO:"

MODEL=$1
MAXLENGTH=$2
PROMPT=$3
BUCKET=ap-pretrained-model
MODEL_BUCKET=gs://$BUCKET/model/$MODEL

python -m trainer.generate \
    --model $MODEL_BUCKET \
    --max-length $MAXLENGTH \
    --prompt "$PROMPT" 
