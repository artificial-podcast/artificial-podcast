#!/usr/bin/env python

from . import model
from . import gsync
import gpt_2_simple as gpt2
import os
import sys
import time
import logging
import argparse
import datetime

# https://stackoverflow.com/questions/35911252/disable-tensorflow-debugging-information
# 0 = all messages are logged (default behavior)
# 1 = INFO messages are not printed
# 2 = INFO and WARNING messages are not printed
# 3 = INFO, WARNING, and ERROR messages are not printed
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'


# textgen configuration

checkpoint_latest = 'latest'
checkpoint_dir = 'checkpoint'
bucket = 'gs://ap-trained-models'  # the storage location

PROMPT_LENGTH = 12
MIN_SEQUENCE_LENGTH = 100


def setup(parser):

    parser.add_argument(
        '--job-dir',    # a working dir for training on the AI platform
        default='job'
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


def generate_text(tf_sess, checkpoint_location, initial_prompt, temperature, min_words, seq_length, prompt_length):

    def generate_sequence(sess, checkpoint_location, prompt, temperature, seq_length):
        tokens = gpt2.generate(
            sess, checkpoint_dir=checkpoint_location,
            prefix=prompt,
            length=seq_length,
            return_as_list=True,
            include_prefix=False)

        gen = tokens[0].replace('\n', ' @ ')
        return gen.split()

    i = 1
    MIN_WORDS_GEN = 3 * prompt_length

    print(f"Iteration {i}")

    repeat = True
    while repeat:
        txt_generated = generate_sequence(
            tf_sess, checkpoint_location, initial_prompt, temperature, seq_length)
        #print(f"txt1: l={len(txt_generated)} {txt_generated}")

        if len(txt_generated) > MIN_WORDS_GEN:
            txt = txt_generated
            repeat = False

    while len(txt) < min_words:
        i += 1
        n = len(txt_generated) - prompt_length
        tokens = txt_generated[n:]
        prompt = ' '.join(tokens)

        print(f"Iteration {i}. Word count={len(txt)}. Prompt={prompt}")

        repeat = True
        while repeat:
            txt_generated = generate_sequence(
                tf_sess, checkpoint_location, prompt, temperature, seq_length)
            #print(f"txt2: l={len(txt_generated)} {txt_generated}")
            txt2 = txt_generated[len(tokens):]

            if len(txt2) > MIN_WORDS_GEN:
                txt = txt + txt2
                repeat = False

    return txt


def create_text_file(tf_sess, checkpoint_location, namespace, model_name, prompt, texts_to_generate=1, temperature=0.75, min_words=500, working_dir='.'):
    i = 0

    while i < texts_to_generate:
        i = i + 1

        ts = datetime.datetime.fromtimestamp(time.time()).strftime('%H%M%S')
        file_name = f"{namespace}_{ts}_{i}.md"

        file_path = f"{working_dir}/" + file_name
        print(f" --> Generating '{file_name}'")

        # open the file and create the frontmatter
        tf = open(file_path, "w")
        tf.write("---\n")
        tf.write(f"prompt: '{prompt}'\n")
        tf.write(f"model: {model_name}\n")
        tf.write("\tfandom:\n")
        tf.write("\tlabels:\n")
        tf.write("---\n\n")

        gen_txt = generate_text(
            tf_sess, checkpoint_location, prompt, temperature, min_words, MIN_SEQUENCE_LENGTH, PROMPT_LENGTH)
        joint_txt = " ".join(gen_txt)

        # write the and close the file
        tf.write(joint_txt.replace('@', '\n\n'))
        tf.close()

        target = f"{bucket}/generated/{namespace}/{file_name}"
        gsync.upload_file(file_path, target)

        print(f" --> Uploaded text to '{target}'")


def do_textgen(args):

    checkpoint_location = os.path.join(args.cache_dir, checkpoint_dir)
    config = model.load_generation_config(args.prompt, args.cache_dir)

    # extract config params
    namespace = config['namespace'].strip()
    model_name = config['model'].strip()
    texts_to_generate = config['generate']['texts']
    temperature = config['generate']['temperature']
    num_words = config['generate']['words']

    print(f" --> Prompts: {config}")

    # download model
    model.download_model(model_name, args.cache_dir, checkpoint_location)

    # load the model
    sess = gpt2.start_tf_sess()
    gpt2.load_gpt2(sess,
                   checkpoint=checkpoint_latest,
                   checkpoint_dir=checkpoint_location)

    # generate texts
    print(f" --> Generating texts")

    prompts = config['prompts'].split("\n")
    for p in prompts:
        if len(p) > 0:
            prompt = p.strip()
            create_text_file(sess, checkpoint_location, namespace, model_name, prompt,
                             texts_to_generate, temperature, num_words,
                             working_dir=args.cache_dir)


if __name__ == '__main__':

    # parse the command line parameters first
    parser = argparse.ArgumentParser()
    args = setup(parser)

    print('')
    print(f" --> Generating text from model {args.prompt}")
    print(f" --> Configuration: {args}")

    do_textgen(args)

    print(" --> DONE.")
