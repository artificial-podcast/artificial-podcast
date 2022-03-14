#!/usr/bin/env python

import argparse
import os
import sys
import logging

from aitextgen import aitextgen

def setup(parser):

    parser.add_argument(
        '--model',
        required=True
    )
    parser.add_argument(
        '--prompt',
        required=True
    )
    parser.add_argument(
        '--max-length',
        type=int,
        default=200
    )
    parser.add_argument(
        '--cache-dir',
        default='cache'
    )
    parser.add_argument(
        '--disable-upload',
        type=bool,
        default='False'
    )

    return parser.parse_args()


if __name__ == '__main__':

    # parse the command line parameters first
    parser = argparse.ArgumentParser()
    args = setup(parser)

    print(" --> PARAMS")
    print(args)
    print('')

    tokenizer_file = os.path.join(args.cache_dir, 'aitextgen.tokenizer.json')
    ai = aitextgen(model_folder=args.cache_dir, tokenizer_file=tokenizer_file)
    
    ai.generate(n=1, prompt=args.prompt, max_length=args.max_length)