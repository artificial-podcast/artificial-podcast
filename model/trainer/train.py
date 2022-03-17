#!/usr/bin/env python

from . import model
from . import gsync
import gpt_2_simple as gpt2
import os
import sys
import logging
import argparse

# https://stackoverflow.com/questions/35911252/disable-tensorflow-debugging-information
# 0 = all messages are logged (default behavior)
# 1 = INFO messages are not printed
# 2 = INFO and WARNING messages are not printed
# 3 = INFO, WARNING, and ERROR messages are not printed
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'


# finetuning configuration

checkpoint_dir = 'checkpoint'  # location of the checkpoints
checkpoint_fresh = 'fresh'
checkpoint_latest = 'latest'

training_sample_every = 100
training_sample_length = 50


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


def do_training(args):
    # prepare other vars
    overwrite_checkpoints = True
    checkpoint_label = checkpoint_latest
    checkpoint_location = os.path.join(args.cache_dir, checkpoint_dir)

    #model.upload_model(args.model, args.cache_dir, checkpoint_location)
    # sys.exit(1)

    # import training file
    local_training_file = model.download_training_file(
        args.training_file, args.cache_dir)

    # import model
    if not os.path.isdir(os.path.join(args.cache_dir, args.gpt2)):
        print(f" --> Downloading {args.gpt2} model...")
        gpt2.download_gpt2(model_dir=args.cache_dir, model_name=args.gpt2)
        checkpoint_label = checkpoint_fresh
        overwrite_checkpoints = False

    # fine-tuning
    sess = gpt2.start_tf_sess()
    gpt2.finetune(sess,
                  local_training_file,
                  model_name=args.gpt2,
                  restore_from=checkpoint_label,
                  model_dir=args.cache_dir,
                  checkpoint_dir=checkpoint_location,
                  batch_size=1,
                  sample_every=training_sample_every,
                  sample_length=training_sample_length,
                  save_every=10,
                  steps=args.num_steps,
                  overwrite=overwrite_checkpoints)

    # upload model
    model.upload_model(args.model, args.cache_dir, checkpoint_location)


if __name__ == '__main__':

    # parse the command line parameters first
    parser = argparse.ArgumentParser()
    args = setup(parser)

    print('')
    print(f" --> Training model {args.model}")
    print(f" --> Training configuration: {args}")

    do_training(args)

    print(" --> DONE.")
