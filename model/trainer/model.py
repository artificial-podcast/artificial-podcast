import os
import yaml
import time
import datetime

try:
    # notebook
    from gsync import download_file, upload_file, sync_from_local, sync_from_remote
except:
    # ml platform
    from .gsync import download_file, upload_file, sync_from_local, sync_from_remote

import gpt_2_simple as gpt2

run_name = 'run1'
model_prefix = 'model'
training_file_name = 'input.txt'

bucket = 'gs://ap-trained-models'  # the storage location

checkpoint_dir = 'checkpoint'  # location of the checkpoints
checkpoint_fresh = 'fresh'
checkpoint_latest = 'latest'

training_sample_every = 100
training_save_every = 500
training_sample_length = 50

PROMPT_LENGTH = 12
MIN_SEQUENCE_LENGTH = 100


def download_training_file(training_file, dest):
    print(f" --> Downloading the training file ({training_file})")

    remote_training_file = f"{bucket}/datasets/{training_file}"

    # download the training file
    local_training_file = os.path.join(dest, training_file_name)
    download_file(remote_training_file, local_training_file)

    return local_training_file


def download_config_file(prompt_file, cache_dir):
    config = {}

    config_file = f"{cache_dir}/generate.yaml"
    remote_prompt_file = f"{bucket}/generated/{prompt_file}"

    print(f" --> Downloading config from '{remote_prompt_file}'")

    # download and parse the config file
    download_file(remote_prompt_file, config_file)

    with open(config_file, 'r') as cf:
        try:
            config = yaml.safe_load(cf)
        except yaml.YAMLError as exc:
            pass

    return config


def upload_model(model, cache_dir, checkpoint_dir):
    remote_base_dir = f"{bucket}/models/{model}"

    print(f" --> Uploading training assets to '{remote_base_dir}'")

    # training input file
    local_training_file = os.path.join(cache_dir, training_file_name)
    remote_training_file = f"{remote_base_dir}/{training_file_name}"

    upload_file(local_training_file, remote_training_file)

    # model checkpoints
    local_checkpoint_location = f"{checkpoint_dir}/{run_name}"
    remote_checkpoint_location = f"{remote_base_dir}/{model_prefix}"
    sync_prefix = f"models/{model}/{model_prefix}"

    sync_from_local(local_checkpoint_location,
                    remote_checkpoint_location, sync_prefix, True)


def download_model(model, cache_dir, checkpoint_dir):
    remote_base_dir = f"{bucket}/models/{model}"

    print(f" --> Downloading model from '{remote_base_dir}'")

    # model checkpoints
    local_checkpoint_location = f"{checkpoint_dir}/{run_name}"
    remote_checkpoint_location = f"{remote_base_dir}/{model_prefix}"
    sync_prefix = f"models/{model}/{model_prefix}/"

    sync_from_remote(remote_checkpoint_location,
                     local_checkpoint_location, sync_prefix)


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

            txt2 = txt_generated[len(tokens):]

            if len(txt2) > MIN_WORDS_GEN:
                txt = txt + txt2
                repeat = False

    return txt


def generate_text_file(tf_sess, job_id, checkpoint_location, namespace, model_name, prompt, texts_to_generate=1, temperature=0.75, min_words=500, working_dir='.'):
    i = 0

    while i < texts_to_generate:
        i = i + 1

        ts = datetime.datetime.fromtimestamp(time.time()).strftime('%H%M%S')
        file_name = f"{namespace}_{job_id}_{ts}.md"

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

        # generate the text
        gen_txt = generate_text(
            tf_sess, checkpoint_location, prompt, temperature, min_words, MIN_SEQUENCE_LENGTH, PROMPT_LENGTH)
        joint_txt = " ".join(gen_txt)

        # write the text and close the file
        tf.write(joint_txt.replace('@', '\n\n'))
        tf.close()

        # upload to cloud storage
        target = f"{bucket}/generated/{namespace}/{file_name}"
        upload_file(file_path, target)

        print(f" --> Uploaded text to '{target}'")


def generate_single_text(job_id, namespace, model_name, prompt, temperature=0.75, num_words=500, texts_to_generate=1, checkpoint_location=checkpoint_dir, checkpoint_label=checkpoint_latest, temp_location='cache'):
    # load the model
    sess = gpt2.start_tf_sess()
    gpt2.load_gpt2(sess, checkpoint=checkpoint_label,
                   checkpoint_dir=checkpoint_location)

    # generate the text
    generate_text_file(sess, job_id, checkpoint_location,
                       namespace, model_name,
                       prompt, texts_to_generate, temperature, num_words,
                       working_dir=temp_location)

    # reset tf in order to avoid OOMs
    gpt2.reset_session(sess)


def generate(args):

    checkpoint_location = os.path.join(args.cache_dir, checkpoint_dir)
    config = download_config_file(args.prompt, args.cache_dir)

    # extract config params
    namespace = config['namespace'].strip()
    model_name = config['model'].strip()
    texts_to_generate = config['generate']['texts']
    temperature = config['generate']['temperature']
    num_words = config['generate']['words']

    print(f" --> Prompts: {config}")

    # download model
    download_model(model_name, args.cache_dir, checkpoint_location)

    # generate texts
    print(f" --> Generating texts")

    prompts = config['prompts'].split("\n")
    for p in prompts:
        if len(p) > 0:
            # generate the text
            prompt = p.strip()

            generate_single_text(args.id, namespace, model_name,
                                 prompt,
                                 temperature=temperature, num_words=num_words, texts_to_generate=texts_to_generate,
                                 checkpoint_location=checkpoint_location, checkpoint_label=checkpoint_latest, temp_location=args.cache_dir)


def training(args):
    # prepare vars
    overwrite_checkpoints = True
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
        overwrite_checkpoints = False

    # import checkpoints to continue training from there
    if args.checkpoints == True:
        checkpoint_location = os.path.join(args.cache_dir, checkpoint_dir)
        download_model(args.model, args.cache_dir, checkpoint_location)
        checkpoint_label = checkpoint_latest

    # training
    sess = gpt2.start_tf_sess()
    gpt2.finetune(sess,
                  local_training_file,
                  model_name=args.gpt2,
                  restore_from=checkpoint_label,
                  model_dir=args.cache_dir,
                  checkpoint_dir=checkpoint_location,
                  batch_size=args.batch_size,
                  sample_every=training_sample_every,
                  sample_length=training_sample_length,
                  save_every=training_save_every,
                  steps=args.num_steps,
                  overwrite=overwrite_checkpoints)

    # upload the model
    upload_model(args.model, args.cache_dir, checkpoint_location)
