import os
import yaml

from . import gsync

run_name = 'run1'
model_prefix = 'model'
training_file_name = 'input.txt'

bucket = 'gs://ap-trained-models'  # the storage location


def download_training_file(training_file, dest):
    print(f" --> Downloading the training file ({training_file})")

    remote_training_file = f"{bucket}/datasets/{training_file}"

    # download the training file
    local_training_file = os.path.join(dest, training_file_name)
    gsync.download_file(remote_training_file, local_training_file)

    return local_training_file


def upload_model(model, cache_dir, checkpoint_dir):
    remote_base_dir = f"{bucket}/models/{model}"

    print(f" --> Uploading training assets to '{remote_base_dir}'")

    # training input file
    local_training_file = os.path.join(cache_dir, training_file_name)
    remote_training_file = f"{remote_base_dir}/{training_file_name}"

    gsync.upload_file(local_training_file, remote_training_file)

    # model checkpoints
    local_checkpoint_location = f"{checkpoint_dir}/{run_name}"
    remote_checkpoint_location = f"{remote_base_dir}/{model_prefix}"
    sync_prefix = f"models/{model}/{model_prefix}"

    gsync.sync_from_local(local_checkpoint_location,
                          remote_checkpoint_location, sync_prefix, True)


def download_model(model, cache_dir, checkpoint_dir):
    remote_base_dir = f"{bucket}/models/{model}"

    print(f" --> Downloading model from '{remote_base_dir}'")

    # model checkpoints
    local_checkpoint_location = f"{checkpoint_dir}/{run_name}"
    remote_checkpoint_location = f"{remote_base_dir}/{model_prefix}"
    sync_prefix = f"models/{model}/{model_prefix}/"

    gsync.sync_from_remote(remote_checkpoint_location,
                           local_checkpoint_location, sync_prefix)


def load_generation_config(prompt_file, cache_dir):
    config = {}

    config_file = f"{cache_dir}/generate.yaml"
    remote_prompt_file = f"{bucket}/generated/{prompt_file}"

    print(f" --> Downloading prompts from '{remote_prompt_file}'")

    # download and parse the config file
    gsync.download_file(remote_prompt_file, config_file)

    with open(config_file, 'r') as cf:
        try:
            config = yaml.safe_load(cf)
        except yaml.YAMLError as exc:
            pass

    return config
