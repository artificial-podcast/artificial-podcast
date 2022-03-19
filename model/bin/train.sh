#!/bin/bash

# Usage: ./bin/train.sh granger_nsfw_v2.txt granger_nsfw_124_v2 10

rm -rf ./cache/checkpoint

TRAINING_FILE=$1
MODEL=$2
STEPS=$3

DATE=`date '+%Y%m%d_%H%M%S'`

python -m trainer.train \
    --model $MODEL \
    --training-file $TRAINING_FILE \
    --num-steps $STEPS \
    --id $DATE \
    --checkpoints True \
    --version 1 \
    --upgrade False
