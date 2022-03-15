#!/usr/bin/env python

import argparse
import os
import sys
import logging
import yaml
import datetime
import time
from textwrap import wrap

from . import gsync
from aitextgen import aitextgen

MIN_WORDS_GEN = 20
PROMPT_LENGTH = 12
GEN_BATCH = 300

bucket = 'gs://ap-trained-models'
prefix = 'models'
tokenizer_file_name = 'aitextgen.tokenizer.json'


def setup(parser):

    parser.add_argument(
        '--prompt',
        required=True
    )
    parser.add_argument(
        '--cache-dir',
        default='cache'
    )
    parser.add_argument(
        '--disable-download',
        type=bool,
        default=False
    )
    parser.add_argument(
        '--disable-upload',
        type=bool,
        default=False
    )

    return parser.parse_args()


def generate_sequence(prompt, temperature, max_length):
    gen1 = ai_model.generate(n=1, prompt=prompt, max_length=max_length,
                             temperature=temperature, return_as_list=True)[0]
    gen2 = gen1.replace('\n', ' @ ')
    return gen2.split()


def generate_text(prompt, temperature, min_words, prompt_length, gen_batch):
    i = 1

    print(f"Iteration {i}")

    repeat = True
    while repeat:
        txt_generated = generate_sequence(prompt, temperature, gen_batch)

        if len(txt_generated) > MIN_WORDS_GEN:
            txt = txt_generated
            repeat = False

    while len(txt) < min_words:
        i += 1
        n = len(txt_generated) - prompt_length
        tokens = txt_generated[n:]
        prompts = ' '.join(tokens)

        print(f"Iteration {i}. Word count={len(txt)}")

        repeat = True
        while repeat:
            txt_generated = generate_sequence(prompts, temperature, gen_batch)
            txt2 = txt_generated[len(tokens):]

            if len(txt2) > MIN_WORDS_GEN:
                txt = txt + txt2
                repeat = False

    return txt


def create_text_file(job_id, namespace, model_name, prompt, texts_to_generate=1, temperature=0.75, min_words=500):
    i = 0

    while i < texts_to_generate:
        i = i + 1

        file_name = job_id + "_" + \
            datetime.datetime.fromtimestamp(
                time.time()).strftime('%H%M%S') + f"_{i}.md"
        
        file_path = f"{args.cache_dir}/" + file_name
        print(f"Generating '{file_name}'")

        # open the file and create the frontmatter
        tf = open(file_path, "w")
        tf.write("---\n")
        tf.write(f"model: {model_name}\n")
        tf.write(f"prompt: '{prompt}'\n")
        tf.write("fandom:\n")
        tf.write("labels:\n")
        tf.write("---\n\n")

        # generate the text
        txt = generate_text(prompt, temperature, min_words,
                            PROMPT_LENGTH, GEN_BATCH)
        ftxt = " ".join(txt)

        # write the and close the file
        tf.write(ftxt.replace('@', '\n\n'))
        tf.close()

        # upload to Cloud Storage
        target = f"gs://ap-trained-models/generated/{namespace}/{file_name}"
        gsync.upload_file(file_path, target)

        print(f"Uploaded text to '{target}'")


if __name__ == '__main__':

    # parse the command line parameters first
    parser = argparse.ArgumentParser()
    args = setup(parser)

    print(" --> PARAMS")
    print(args)
    print('')

    config = {}
    config_file = f"{args.cache_dir}/generate.yaml"
    remote_prompt = bucket + "/generated/" + args.prompt

    # download and parse the config file
    gsync.download_file(remote_prompt, config_file)

    with open(config_file, 'r') as cf:
        try:
            config = yaml.safe_load(cf)
        except yaml.YAMLError as exc:
            sys.exit(1)

    # extract config params
    namespace = config['namespace'].strip()
    model = config['model'].strip()
    texts_to_generate = config['generate']['texts']
    temperature = config['generate']['temperature']
    words = config['generate']['words']

    print(f" --> Job configuration: {config}")

    if not args.disable_download:
        print(" --> Downloading the pre-trained model")

        remote = bucket + "/" + prefix + "/" + model
        gsync.sync_from_remote(remote, args.cache_dir, model)

    print(" --> Load the model")

    global ai_model
    tokenizer_file = os.path.join(args.cache_dir, tokenizer_file_name)
    ai_model = aitextgen(model_folder=args.cache_dir,
                         tokenizer_file=tokenizer_file)

    # generate texts
    prompts = config['prompts'].split("\n")
    for p in prompts:
        if len(p) > 0:
            prompt = p.strip()
            print(prompt)
            create_text_file('gen', namespace, model, prompt,
                             texts_to_generate, temperature, words)
