#!/bin/bash

# Usage: ./bin/train.sh shakespeare.txt shakespeare 20

TRAINING_FILE=$1
MODEL=$2
STEPS=$3

python -m trainer.train \
    --model $MODEL \
    --training-file $TRAINING_FILE \
    --num-steps $STEPS \
    --checkpoints True
