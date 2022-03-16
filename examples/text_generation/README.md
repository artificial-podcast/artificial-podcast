# Tests

### Performance

#### Test 15.03, v1

* 2GPU,batch=2,iter=1000,ddp:   ca. 1.24 it/s
* 1GPU,batch=1,iter=1000,dp:    ca. 9.8 it/s

aitextgen: https://github.com/artificial-podcast/aitextgen/commit/559a465022695a23e1a73840c83766ecd7ea4cc8

#### Models

* granger_nsfw_124: GPT-2 124M, 50000 iterations -> ca. 9.8 it/s
* granger_nsfw_124_100k: GPT-2 124M, 100000 iterations
* granger_nsfw_355_50k: GPT-2 355M, 50000 iterations