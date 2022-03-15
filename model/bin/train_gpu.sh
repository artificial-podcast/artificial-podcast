#!/bin/bash

# Usage: ./bin/train.sh draco draco.txt

BUCKET=ap-trained-models
PACKAGE_NAME=trainer-1
REGION=europe-west4

DATE=`date '+%Y%m%d_%H%M%S'`

MODEL=$1
TRAINING=$2

JOB_NAME=$1_train_
JOB_ID=$JOB_NAME$DATE

TRAINING_FILE=gs://$BUCKET/datasets/$TRAINING
PACKAGE_PATH=gs://$BUCKET/packages/$PACKAGE_NAME.tar.gz
JOB_DIR=gs://$BUCKET/jobs/$JOB_ID


# launch the job
gcloud ai-platform jobs submit training $JOB_ID \
    --job-dir $JOB_DIR \
    --region $REGION \
    --python-version '3.7' \
    --runtime-version '2.8' \
    --packages $PACKAGE_PATH \
    --module-name 'trainer.finetune' \
    --config bin/train_gpu.yaml \
    -- \
    --model $MODEL \
    --training-file $TRAINING_FILE \
    --strategy dp \
    --batch-size 1 \
    --num-steps 50000
