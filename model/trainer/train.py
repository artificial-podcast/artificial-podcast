#!/usr/bin/env python

import os
import sys
import logging
import argparse
from .model import training

# https://stackoverflow.com/questions/35911252/disable-tensorflow-debugging-information
# 0 = all messages are logged (default behavior)
# 1 = INFO messages are not printed
# 2 = INFO and WARNING messages are not printed
# 3 = INFO, WARNING, and ERROR messages are not printed
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'


def setup():

    parser = argparse.ArgumentParser()

    # environment
    parser.add_argument(
        '--cache-dir',
        default='cache'
    )

    # job
    parser.add_argument(
        '--id',         # a unique id for the job
        default='id'
    )
    parser.add_argument(
        '--job-dir',    # a working dir for training on the AI platform
        default='job'
    )

    # model
    parser.add_argument(
        '--gpt2',       # 124M, 355M
        default='124M'
    )
    parser.add_argument(
        '--training-file',  # the file to train the model with
        required=True
    )
    parser.add_argument(
        '--model',      # name of the model
        required=True
    )
    parser.add_argument(
        '--version',  # version -> v1
        type=int,
        default=1
    )
    parser.add_argument(
        '--upgrade',  # increase the version number after the training
        type=bool,
        default=False
    )
    parser.add_argument(
        '--checkpoints',  # set to true to continue training
        type=bool,
        default=True
    )
    parser.add_argument(
        '--num-steps',  # number of training steps
        type=int,
        default=20
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=1
    )

    return parser.parse_args()


if __name__ == '__main__':

    # parse the command line parameters first
    args = setup()

    print('')
    print(f" --> Training model {args.model}")
    print(f" --> Training configuration: {args}")

    training(args)

    print(" --> DONE.")
