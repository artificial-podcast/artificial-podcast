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
#os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'


def setup():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--job-dir',    # a working dir for training on the AI platform
        default='job'
    )
    parser.add_argument(
        '--id',         # a unique id for the job
        default='id'
    )
    parser.add_argument(
        '--cache-dir',
        default='cache'
    )
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
