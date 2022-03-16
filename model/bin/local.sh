#!/bin/bash

# Usage: ./bin/local.sh shakespeare.txt shakespeare 20

TRAINING=$1
MODEL=$2
STEPS=$3

BUCKET=ap-trained-models
#TRAINING_FILE=gs://$BUCKET/datasets/$TRAINING

python -m trainer.train \
    --model $MODEL \
    --training-file $TRAINING \
    --num-steps $STEPS
