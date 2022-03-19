#!/usr/bin/env python

import argparse
import logging
import sys
import os
from .model import generate

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

    # generation
    parser.add_argument(
        '--prompt',
        required=True
    )

    return parser.parse_args()


if __name__ == '__main__':

    # parse the command line parameters first
    args = setup()

    print('')
    print(f" --> Generating text from model {args.prompt}")
    print(f" --> Configuration: {args}")

    generate(args)

    print(" --> DONE.")
