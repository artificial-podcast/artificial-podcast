#!/usr/bin/env python

import os
import sys
import logging
import argparse

from . import gsync
import gpt_2_simple as gpt2

# global configuration: know what you are doing when you change it !
bucket = 'gs://ap-trained-models'  # the storage location
training_file_name = 'input.txt'

# finetuning configuration
#gpt2_model = "124M"
#num_finetune_steps = 20

#training_file_url = "https://raw.githubusercontent.com/artificial-podcast/datasets/c1dfbfe59c9dcebe3d9cf1c62b1a71cd95b71f3f/examples/granger_external_v2.txt"
#training_file_name = "granger_external_v2.txt"

model_location = 'models'  # location of the model

checkpoint_dir = 'checkpoint'  # location of the checkpoints
checkpoint_fresh = 'fresh'
checkpoint_latest = 'latest'


def setup(parser):

    parser.add_argument(
        '--cache-dir',
        default='cache'
    )
    parser.add_argument(
        '--job-dir',    # a working dir for training on the AI platform
        default='job'
    )
    parser.add_argument(
        '--gpt2',       # 124M, 355M
        default='124M'
    )
    parser.add_argument(
        '--num-steps',  # number of training steps
        type=int,
        default=20
    )
    parser.add_argument(
        '--training-file',  # the file to train the model with
        required=True
    )
    parser.add_argument(
        '--model',      # name of the model
        required=True
    )

    return parser.parse_args()


def download_training_file(training_file, dest):
    print(f" --> Downloading the training file ({training_file})")

    remote_training_file = f"{bucket}/datasets/{training_file}"

    # download the training file
    local_training_file = os.path.join(dest, training_file_name)
    gsync.download_file(remote_training_file, local_training_file)

    return local_training_file


if __name__ == '__main__':

    # parse the command line parameters first
    parser = argparse.ArgumentParser()
    args = setup(parser)

    print(" --> PARAMS")
    print(args)
    print('')

    # prepare other vars
    checkpoint_label = checkpoint_latest
    checkpoint_location = os.path.join(args.cache_dir, checkpoint_dir)

    # import training file
    local_training_file = download_training_file(
        args.training_file, args.cache_dir)

    # import model
    if not os.path.isdir(os.path.join(args.cache_dir, args.gpt2)):
        print(f" --> Downloading {args.gpt2} model...")
        gpt2.download_gpt2(model_dir=args.cache_dir, model_name=args.gpt2)
        checkpoint_label = checkpoint_fresh

    # fine-tuning
    sess = gpt2.start_tf_sess()
    gpt2.finetune(sess, local_training_file, model_name=args.gpt2, restore_from=checkpoint_label,
                  model_dir=args.cache_dir, checkpoint_dir=checkpoint_location, steps=args.num_steps)
