# Tests

### Performance

#### Test 15.03, v1 (aitextgen)

* 2GPU,batch=2,iter=1000,ddp:   ca. 1.24 it/s
* 1GPU,batch=1,iter=1000,dp:    ca. 9.8 it/s

aitextgen: https://github.com/artificial-podcast/aitextgen/commit/559a465022695a23e1a73840c83766ecd7ea4cc8

#### Test 18.03, rewrite with gpt-2-simple

Test run with 33Mb training set

```shell
./bin/ml_train.sh granger_nsfw_v2.txt granger_nsfw_124_v2 500
```

* n1-standard-4, 1x NVIDIA_TESLA_T4,b=1 job: train_granger_nsfw_124_v2_20220318_082137 -> t=28'22''
* n1-standard-4, 1x NVIDIA_TESLA_T4,b=64 job: train_granger_nsfw_124_v2_20220318_092625 -> crashed OOM
* n1-standard-4, 1x NVIDIA_TESLA_T4,b=2 job: train_granger_nsfw_124_v2_20220318_095024 -> cancelled because GPU at 100%
* n1-standard-4, 2x NVIDIA_TESLA_T4,b=2 job: train_granger_nsfw_124_v2_20220318_095126 -> cancelled because stalled for > 15min
* n1-standard-4, 2x NVIDIA_TESLA_T4,b=1 job: train_granger_nsfw_124_v2_20220318_101645 -> t=28'21''
* n1-standard-4, 1x NVIDIA_TESLA_V100,b=1 job: train_granger_nsfw_124_v2_20220318_110508 -> t=


#### Models

Training with e.g.

```shell
./bin/train_gpu.sh granger_nsfw_355_50k_v2 granger_nsfw_v2.txt
```

#### v1

* granger_nsfw_124: GPT-2 124M, 50k iterations          -> training time: 1:35h, ca. 9.8 it/s
* granger_nsfw_124_100k: GPT-2 124M, 100k iterations    -> training time: 3:04h, ca. 9.5 it/s
* granger_nsfw_355_50k: GPT-2 355M, 50k iterations      -> training time: 3:48h, ca. 3.8 it/s

#### v2

* granger_nsfw_355_50k_v2: GPT-2 355M, 50k iterations   -> training time: 3:49h, ca. 3.8 it/s

#### Generation

```shell
.bin/generate.sh 
```

#### Download the texts

```shell

gsutil -m cp \
  "gs://ap-trained-models/generated/granger_test/granger_test_203908_203922.md" \
  "gs://ap-trained-models/generated/granger_test/granger_test_203908_204520.md" \
  .

```
