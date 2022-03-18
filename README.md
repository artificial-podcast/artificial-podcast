# artificial-podcast
Create podcasts from AI generated fanfiction

### Python environment for local model training

```shell
pip3 install virtualenv

python3 -m venv env

source env/bin/activate

...
...

deactivate
```

### References

* https://huggingface.co/docs/transformers/model_doc/gpt2
* https://cloud.google.com/ai-platform/training/docs

### Tensorflow on M1 Mac

```shell
brew install hdf5

# https://stackoverflow.com/questions/70670205/failed-to-build-h5py-on-mac-m1
export HDF5_DIR=/opt/homebrew/Cellar/hdf5/1.13.0/
pip install --no-binary=h5py h5py

python -m pip install tensorflow-macos

# https://developer.apple.com/forums/thread/691317
pip install tensorflow-macos --no-cache-dir

# https://developer.apple.com/metal/tensorflow-plugin/
pip install tensorflow-metal

```
