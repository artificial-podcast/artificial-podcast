import os
import time
from google.cloud import storage


# the Google cloud credential file
credential_file = 'google-credentials.json'

storage_client = None
try:
    storage_client = storage.Client()
except:
    try:
        storage_client = storage.Client.from_service_account_json(
            credential_file)
    except:
        sys.exit(1)


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


def upload_with_retry(blob, local_path, retries=3):
    success = False
    retry = 0

    while success == False:
        try:
            blob.upload_from_filename(local_path)
            success = True
        except:
            retry = retry + 1
            if retry == retries:
                sys.exit(0)

            time.sleep(retry*retry)  # backoff a bit 1,4,9 seconds ...
            print(f"Re-try upload of '{local_path}'. ({retry}/{retries})")
            pass


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
    # blob.upload_from_filename(source)
    upload_with_retry(blob, source)


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

    blobs = storage_client.list_blobs(
        bucket_name, max_results=None, prefix=prefix, delimiter=None)

    for b in blobs:
        local_path = os.path.join(local, remove_prefix(b.name, prefix))
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
                remote_path = f"{remote_base}/{f}"
                if sync:
                    try:
                        inventory.remove(remote_path)
                    except:
                        None

                blob = bucket.blob(remote_path)
                upload_with_retry(blob, local_path)

    if sync:
        for f in inventory:
            blob = bucket.blob(f)
            if blob.exists():
                blob.delete()
