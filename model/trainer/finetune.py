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

bucket = 'gs://pretrained-model'
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
        default=50
    )
    parser.add_argument(
        '--block-size',
        type=int,
        default=64
    )

    parser.add_argument(
        '--training_file',
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

    return parser.parse_args()


def download_training_file(source, location):
    local_location = source
    if source.startswith('gs://'):
        local_location = location + "/training.txt"
        gsync.download_file(source, local_location)


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

    # download the training file
    local_path = os.path.join(args.cache_dir, 'input.txt')
    gsync.download_file(args.training_file, local_path)

    # parse the training file
    tokenizer.train_tokenizer(local_path, save_path=args.cache_dir)

    # training job configuration
    config = build_gpt2_config(
        vocab_size=args.vocab_size, max_length=args.block_size, dropout=args.dropout, n_embd=args.n_embd, n_layer=args.n_layer, n_head=args.n_head)
    data = TokenDataset(
        local_path, tokenizer_file=tokenizer_file, block_size=args.block_size)

    # Instantiate aitextgen using the created tokenizer and config
    ai = aitextgen(tokenizer_file=tokenizer_file, config=config)

    # training job
    ai.train(data, output_dir=args.cache_dir, batch_size=args.batch_size,
             num_steps=args.num_steps, generate_every=5000, save_every=5000)

    # upload to the cloud storage
    remote = bucket + "/" + prefix
    gsync.sync_from_local(args.cache_dir, remote, args.model)
