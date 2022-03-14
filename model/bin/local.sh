#!/bin/bash

# Usage: ./bin/local.sh model shakespeare.txt

MODEL=$1
TRAINING=$2
BUCKET=ap-pretrained-model
TRAINING_FILE=gs://$BUCKET/datasets/$TRAINING

python -m trainer.finetune \
    --model $MODEL \
    --training-file $TRAINING_FILE 
