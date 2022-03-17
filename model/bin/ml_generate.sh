#!/bin/bash

# Usage: ./bin/ml_generate.sh granger_test.yaml

PROMPT=$1

BUCKET=ap-trained-models
PACKAGE_NAME=trainer-2
REGION=europe-west4

DATE=`date '+%Y%m%d_%H%M%S'`
JOB_NAME=gen_
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
    --module-name 'trainer.textgen' \
    --config bin/infra_gpu.yaml \
    -- \
    --prompt $PROMPT
