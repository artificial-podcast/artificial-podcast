#!/bin/bash

# Usage: ./bin/local.sh shakespeare shakespeare.txt

MODEL=$1
TRAINING=$2
BUCKET=ap-trained-models
TRAINING_FILE=gs://$BUCKET/datasets/$TRAINING

python -m trainer.finetune \
    --model $MODEL \
    --training-file $TRAINING_FILE \
    --num-steps 1000
