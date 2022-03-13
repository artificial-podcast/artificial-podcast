import os
from google.cloud import storage

storage_client = storage.Client()

SEP = "/"


def remove_prefix(s, prefix):
    return s[len(prefix):] if s.startswith(prefix) else s


def bucket_from_url(url):
    p = url.split(SEP)

    # validation
    if p[0] != 'gs:':
        raise ValueError('Invalid url')
    if len(p) < 3 or p[2] == '':
        raise ValueError('Invalid url')

    return p[2]


def source_from_url(url):
    p = url.split(SEP)

    # validation
    if p[0] != 'gs:':
        raise ValueError('Invalid url')
    if len(p) < 3 or p[2] == '':
        raise ValueError('Invalid url')

    return SEP.join(p[3:])


def download_file(source, target):
    bucket_name = bucket_from_url(source)
    blob_name = source_from_url(source)

    # make sure path_to_target exists
    path = os.path.dirname(target)
    if not os.path.isdir(path):
        os.makedirs(path)

    # download the file
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.download_to_filename(target)


def upload_file(source, target):
    bucket_name = bucket_from_url(target)
    blob_name = source_from_url(target)

    # upload the file
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(source)


def remote_inventory(remote, prefix):
    bucket_name = bucket_from_url(remote)

    blobs = storage_client.list_blobs(
        bucket_name, max_results=None, prefix=prefix, delimiter=None)

    inv = []
    for b in blobs:
        inv.append(b.name)
    return inv


def sync_from_remote(remote, local, prefix):
    bucket_name = bucket_from_url(remote)
    effective_prefix = prefix + "/model/"

    blobs = storage_client.list_blobs(
        bucket_name, max_results=None, prefix=prefix, delimiter=None)

    for b in blobs:
        local_path = os.path.join(
            local, remove_prefix(b.name, effective_prefix))
        path = os.path.dirname(local_path)

        if not os.path.isdir(path):
            os.makedirs(path)
        b.download_to_filename(local_path)


def sync_from_local(local, remote, prefix, sync=False):
    bucket_name = bucket_from_url(remote)
    remote_base = source_from_url(remote)
    inventory = []

    if sync:
        inventory = remote_inventory(remote, prefix)

    bucket = storage_client.bucket(bucket_name)

    for root, dirs, files in os.walk(local):
        if len(files) > 0:
            for f in files:
                local_path = os.path.join(root, f)
                remote_path = remote_base + local_path.strip(local)
                if sync:
                    try:
                        inventory.remove(remote_path)
                    except:
                        None

                blob = bucket.blob(remote_path)
                blob.upload_from_filename(local_path)
    if sync:
        for f in inventory:
            blob = bucket.blob(f)
            if blob.exists():
                blob.delete()


if __name__ == '__main__':

    remote = 'gs://artificial-podcast/pretrained/test'
    prefix = 'pretrained/test'
    local = 'model'

    sync_from_remote(remote, local, prefix)
    #sync_from_local(local, remote, prefix, True)
    # print("")
    #remote_inventory(remote, prefix)
