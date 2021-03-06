#!/bin/bash

# Usage: ./bin/ml_train.sh granger_nsfw_v2.txt granger_nsfw_124_v2 10

TRAINING_FILE=$1
MODEL=$2
STEPS=$3

BUCKET=ap-trained-models
PACKAGE_NAME=trainer-2
REGION=europe-west4

DATE=`date '+%Y%m%d_%H%M%S'`
JOB_NAME=train_$2_
JOB_ID=$JOB_NAME$DATE
PACKAGE_PATH=gs://$BUCKET/packages/$PACKAGE_NAME.tar.gz
JOB_DIR=gs://$BUCKET/jobs/$JOB_ID

# launch the job
gcloud ai-platform jobs submit training $JOB_ID \
    --job-dir $JOB_DIR \
    --region $REGION \
    --python-version '3.7' \
    --runtime-version '2.8' \
    --packages $PACKAGE_PATH \
    --module-name 'trainer.train' \
    --config bin/cloud_train_infra.yaml \
    -- \
    --model $MODEL \
    --training-file $TRAINING_FILE \
    --num-steps $STEPS \
    --id $DATE \
    --batch-size 1 \
    --checkpoints True \
    --version 1 \
    --upgrade False
