#!/bin/bash

# Usage: ./bin/train.sh shakespeare.txt shakespeare 20

TRAINING_FILE=$1
MODEL=$2
STEPS=$3

DATE=`date '+%Y%m%d_%H%M%S'`

python -m trainer.train \
    --model $MODEL \
    --training-file $TRAINING_FILE \
    --num-steps $STEPS \
    --id $DATE \
    --checkpoints True
