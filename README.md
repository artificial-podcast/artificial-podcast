# artificial-podcast
Create podcasts from AI generated texts

### Python environment for local model training

```shell
pip3 install virtualenv

python3 -m venv env

source env/bin/activate

...
...

deactivate
```

### Performance

#### Test 15.03, v1

* 2GPU,batch=2,iter=1000,ddp:   ca. 1.24 it/s
* 1GPU,batch=1,iter=1000,dp:    ca. 9.8 it/s

### References

