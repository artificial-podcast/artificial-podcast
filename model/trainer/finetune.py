#!/usr/bin/env python

import argparse
import os
import sys
import logging

from . import gsync, tokenizer

from aitextgen.TokenDataset import TokenDataset
#from aitextgen.tokenizers import train_tokenizer
from aitextgen.utils import GPT2ConfigCPU, build_gpt2_config
from aitextgen import aitextgen

bucket = 'gs://ap-trained-models'
prefix = 'models'


def setup(parser):

    parser.add_argument(
        '--vocab-size',
        type=int,
        default=5000
    )
    parser.add_argument(
        '--n-embd',
        type=int,
        default=256
    )
    parser.add_argument(
        '--n-layer',
        type=int,
        default=8
    )
    parser.add_argument(
        '--n-head',
        type=int,
        default=8
    )
    parser.add_argument(
        '--dropout',
        type=float,
        default=0.0
    )

    parser.add_argument(
        '--batch-size',
        type=int,
        default=16
    )
    parser.add_argument(
        '--num-steps',
        type=int,
        default=2000
    )
    parser.add_argument(
        '--generate-every',
        type=int,
        default=1000
    )
    parser.add_argument(
        '--save-every',
        type=int,
        default=1000
    )
    parser.add_argument(
        '--block-size',
        type=int,
        default=64
    )

    parser.add_argument(
        '--training-file',
        required=True
    )
    parser.add_argument(
        '--model',
        required=True
    )
    parser.add_argument(
        '--cache-dir',
        default='cache'
    )
    parser.add_argument(
        '--job-dir',
        default='job'
    )
    parser.add_argument(
        '--disable-upload',
        type=bool,
        default=False
    )

    return parser.parse_args()


if __name__ == '__main__':

    # parse the command line parameters first
    parser = argparse.ArgumentParser()
    args = setup(parser)

    print(" --> PARAMS")
    print(args)
    print('')

    # all other defaults

    #tokenizer_file = "aitextgen.tokenizer.json"
    tokenizer_file = os.path.join(args.cache_dir, 'aitextgen.tokenizer.json')

    print(" --> Downloading the training file")

    # download the training file
    local_training_file = os.path.join(args.cache_dir, 'input.txt')
    gsync.download_file(args.training_file, local_training_file)

    print(" --> Preparing the tokenizer")

    # parse the training file
    tokenizer.train_tokenizer(local_training_file, save_path=args.cache_dir)

    data = TokenDataset(
        local_training_file, tokenizer_file=tokenizer_file, block_size=args.block_size)

    print(" --> Initializing the trainer")

    # training job configuration
    config = build_gpt2_config(
        vocab_size=args.vocab_size, max_length=args.block_size, dropout=args.dropout, n_embd=args.n_embd, n_layer=args.n_layer, n_head=args.n_head)

    print(" --> CONFIG")
    print(config)
    print('')

    # Instantiate aitextgen using the created tokenizer and config
    ai = aitextgen(tokenizer_file=tokenizer_file, config=config)

    print(" --> Start the training")

    # training job
    ai.train(data, output_dir=args.cache_dir, batch_size=args.batch_size,
             num_steps=args.num_steps, generate_every=args.generate_every, save_every=args.save_every)

    print(" --> Uploading the pre-trained model")

    # upload to the cloud storage
    if not args.disable_upload:
        remote = bucket + "/" + prefix + "/" + args.model
        gsync.sync_from_local(args.cache_dir, remote, args.model)

    print(" --> DONE.")
