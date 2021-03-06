import gpt_2_simple as gpt2
import os
import yaml
import time
import datetime
import requests
import psutil

import logging
logging.basicConfig(format="%(asctime)s — %(levelname)s — %(name)s — %(message)s",
                    datefmt="%d-%m-%Y %H:%M:%S", level=logging.INFO)

try:
    # notebook
    from gsync import download_file, upload_file, sync_from_local, sync_from_remote
except:
    # ml platform
    from .gsync import download_file, upload_file, sync_from_local, sync_from_remote


run_name = 'run1'
model_prefix = 'model'
training_file_name = 'input.txt'

model_bucket = 'gs://ap-trained-models'  # the storage location
text_bucket = 'gs://ap-generated-texts'  # the storage location

checkpoint_dir = 'checkpoint'  # location of the checkpoints
checkpoint_fresh = 'fresh'
checkpoint_latest = 'latest'

training_sample_every = 100
training_save_every = 500
training_sample_length = 50

PROMPT_LENGTH = 12
MIN_SEQUENCE_LENGTH = 150

# free TF every 2 or 3 runs depending on how much memory is available
purge_interval = 1
if psutil.virtual_memory().total / (1024*1024) > 16384:
    purge_interval = 3


def download_training_file(training_file, cache_dir):
    local_training_file = os.path.join(cache_dir, training_file_name)

    if training_file.find('http') > -1:
        # download the training file from the provided URL

        # make sure path to local_training_file exists
        path = os.path.dirname(local_training_file)
        if not os.path.isdir(path):
            os.makedirs(path)

        data = requests.get(training_file)
        with open(local_training_file, 'w') as f:
            f.write(data.text)
    else:
        # download the training file from a bucket
        remote_training_file = f"{model_bucket}/datasets/{training_file}"
        download_file(remote_training_file, local_training_file)

    print(f" --> Downloaded training file '{training_file}'")
    return local_training_file


def download_config_file(prompt_file, cache_dir):
    config = {}
    config_file = f"{cache_dir}/generate.yaml"

    if prompt_file.find('http') > -1:
        # download the config file from the provided URL
        remote_prompt_file = prompt_file # because print statement !

        # make sure path to config_file exists
        path = os.path.dirname(config_file)
        if not os.path.isdir(path):
            os.makedirs(path)
        
        data = requests.get(remote_prompt_file)
        with open(config_file, 'w') as f:
            f.write(data.text)

    else:
        # download the config file from a bucket
        remote_prompt_file = f"{text_bucket}/prompts/{prompt_file}"
        download_file(remote_prompt_file, config_file)

    with open(config_file, 'r') as cf:
        try:
            config = yaml.safe_load(cf)
        except yaml.YAMLError as exc:
            pass

    print(f" --> Downloaded config from '{remote_prompt_file}'")
    return config


def download_model(model, cache_dir, checkpoint_dir, version=1):
    remote_base_dir = f"{model_bucket}/models/{model}/v{version}"

    print(f" --> Downloading model from '{remote_base_dir}'")

    # model checkpoints
    local_checkpoint_location = f"{checkpoint_dir}/{run_name}"
    remote_checkpoint_location = f"{remote_base_dir}/{model_prefix}"
    # sync_prefix needs a trailing / !!!
    sync_prefix = f"models/{model}/v{version}/{model_prefix}/"

    sync_from_remote(remote_checkpoint_location,
                     local_checkpoint_location, sync_prefix)


def upload_model(model, cache_dir, checkpoint_dir, version=1):
    remote_base_dir = f"{model_bucket}/models/{model}/v{version}"

    print(f" --> Uploading training assets to '{remote_base_dir}'")

    # training input file
    local_training_file = os.path.join(cache_dir, training_file_name)
    remote_training_file = f"{remote_base_dir}/{training_file_name}"

    upload_file(local_training_file, remote_training_file)

    # model checkpoints
    local_checkpoint_location = f"{checkpoint_dir}/{run_name}"
    remote_checkpoint_location = f"{remote_base_dir}/{model_prefix}"
    sync_prefix = f"models/{model}/v{version}/{model_prefix}"

    sync_from_local(local_checkpoint_location,
                    remote_checkpoint_location, sync_prefix, True)


def clean_text(txt):

    # step 1: normalize the quotation marks
    step1 = txt.replace('”', '"').replace('“', '"')

    # step 2: break-up continous text into paragraphs
    step2 = step1.replace('" "', '"\n\n"').replace('""', '"\n\n"')
    step2 = step2.replace('"."', '"\n\n"').replace(
        '. "', '.\n\n"')
    step2 = step2.replace('@@', '\n')

    # step 3: remove unwanted chars
    final = step2.replace('…', '... ').replace('�', '')

    # close the text properly
    last = final.rfind('.')
    if last == -1:
        return final
    return final[:last+1]


def generate_text(tf_sess, checkpoint_location, initial_prompt, temperature, num_words, seq_length, prompt_length):

    def generate_sequence(sess, checkpoint_location, prompt, temperature, seq_length):
        tokens = None
        if prompt == 'RANDOM':
            tokens = gpt2.generate(
                sess, checkpoint_dir=checkpoint_location,
                length=seq_length,
                return_as_list=True)
        else:
            tokens = gpt2.generate(
                sess, checkpoint_dir=checkpoint_location,
                prefix=prompt,
                length=seq_length,
                return_as_list=True,
                include_prefix=False)

        gen = tokens[0].replace('\n', '@@')
        return gen.split()

    i = 1
    MIN_WORDS_GEN = 3 * prompt_length

    print(f" --> Initial prompt: '{initial_prompt}'")

    repeat = True
    while repeat:
        txt_generated = generate_sequence(
            tf_sess, checkpoint_location, initial_prompt, temperature, seq_length)

        if len(txt_generated) > MIN_WORDS_GEN:
            txt = txt_generated
            repeat = False

    while len(txt) < num_words:
        n = len(txt_generated) - prompt_length
        tokens = txt_generated[n:]
        prompt = ' '.join(tokens)

        repeat = True
        repeat_count = 0
        while repeat:
            txt_generated = generate_sequence(
                tf_sess, checkpoint_location, prompt, temperature, seq_length)

            txt2 = txt_generated[len(tokens):]

            if len(txt2) > MIN_WORDS_GEN:
                txt = txt + txt2
                repeat = False

            repeat_count = repeat_count + 1

        print(
            f" --> Iteration {i}: R={repeat_count}, W={len(txt)}, P='{prompt}'")
        i += 1

    return txt


def generate_text_file(tf_sess, job_id, namespace, model_name, prompt, labels, temperature=0.75, num_words=500, texts_to_generate=1, checkpoint_location=checkpoint_dir, working_dir='.'):
    i = 0

    while i < texts_to_generate:
        i = i + 1

        ts = datetime.datetime.fromtimestamp(time.time()).strftime('%H%M%S')
        file_name = f"{namespace}_{job_id}_{ts}.md"

        file_path = f"{working_dir}/" + file_name
        print(f" --> Generating '{file_name}'")

        # generate the text
        gen_txt = generate_text(
            tf_sess, checkpoint_location, prompt, temperature, num_words, MIN_SEQUENCE_LENGTH, PROMPT_LENGTH)
        joint_txt = " ".join(gen_txt)

        # open the file and create the frontmatter
        tf = open(file_path, "w")
        tf.write("---\n")
        tf.write(f"prompt: '{prompt}'\n")
        tf.write("generate:\n")
        tf.write(f"\tlabels: '{labels}'\n")
        tf.write(f"\tmodel: {model_name}\n")
        tf.write(f"\twords: {len(gen_txt)}\n")
        tf.write(f"\ttemperature: {temperature}\n")
        tf.write("---\n\n")

        # clean and write the text then close the file
        tf.write(clean_text(joint_txt))
        tf.close()

        # upload to cloud storage
        target = f"{text_bucket}/generated/{namespace}/{file_name}"
        upload_file(file_path, target)

        print(f" --> Uploaded text to '{target}'")


def generate_single_text(job_id, namespace, model_name, prompt, labels='none', temperature=0.75, num_words=500, texts_to_generate=1, checkpoint_location=checkpoint_dir, checkpoint_label=checkpoint_latest, temp_location='cache'):
    # load the model
    sess = gpt2.start_tf_sess()
    gpt2.load_gpt2(sess, checkpoint=checkpoint_label,
                   checkpoint_dir=checkpoint_location)

    # generate the text
    generate_text_file(sess, job_id,
                       namespace, model_name,
                       prompt, labels,
                       temperature, num_words, texts_to_generate,
                       checkpoint_location=checkpoint_location, working_dir=temp_location)

    # reset tf in order to avoid OOMs
    gpt2.reset_session(sess)


def generate(args):

    checkpoint_location = os.path.join(args.cache_dir, checkpoint_dir)
    config = download_config_file(args.prompt, args.cache_dir)

    # extract config params
    namespace = config['namespace'].strip()
    model_name = config['model']['name'].strip()
    model_version = config['model']['version']
    texts_to_generate = config['generate']['texts']
    temperature = config['generate']['temperature']
    num_words = config['generate']['words']
    labels = config['metadata']['labels']

    print(f" --> Prompts: {config}")

    # download model
    download_model(model_name, args.cache_dir,
                   checkpoint_location, model_version)

    # load the model
    sess = gpt2.start_tf_sess()
    gpt2.load_gpt2(sess, checkpoint_dir=checkpoint_location)

    # start generating texts
    n = 0
    print(f" --> Generating texts")

    prompts = config['prompts'].split("\n")
    for p in prompts:
        if len(p) > 0:
            # generate the text
            prompt = p.strip()

            # generate the text
            generate_text_file(sess, args.id, namespace, model_name, prompt, labels, temperature=temperature, num_words=num_words,
                               texts_to_generate=texts_to_generate, checkpoint_location=checkpoint_location, working_dir=args.cache_dir)

            # count and maybe reset TF?
            n = n + 1
            if n % purge_interval == 0:
                sess = gpt2.reset_session(sess)
                gpt2.load_gpt2(sess, checkpoint_dir=checkpoint_location)

    # reset tf in order to avoid OOMs
    gpt2.reset_session(sess)


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
        download_model(args.model, args.cache_dir,
                       checkpoint_location, args.version)
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
    version = args.version
    if args.upgrade == True:
        version = version + 1

    upload_model(args.model, args.cache_dir, checkpoint_location, version)
