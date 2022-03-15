#!/bin/bash

MODEL_NAME=trainer
MODEL_VERSION=1

BUCKET=ap-trained-models

source ../env/bin/activate

function package_and_upload {
  MODEL=$1
  VERSION=$2
  BUCKET=$3

  PACKAGE_NAME=$MODEL-$VERSION

  cwd=$(pwd)

  echo " --> Packaging model '$PACKAGE_NAME'"

  python setup.py sdist > /dev/null

  PACKAGE="$PACKAGE_NAME".tar.gz
  UPLOAD_LOCATION="gs://$BUCKET/packages/"

  echo " --> Uploading model '$PACKAGE_NAME'"
  gsutil cp dist/$PACKAGE $UPLOAD_LOCATION

  echo " --> Cleanup"

  rm -rf dist
  rm -rf $MODEL.egg-info

  cd $cwd
}

echo " --> Package and upload the model"
echo ""

# Package the models
package_and_upload $MODEL_NAME $MODEL_VERSION $BUCKET