# Generaptor with Docker

## Build

```bash
sudo docker image build -t cert-edf/generaptor .
```

## Usage

```bash
# update cache
sudo docker container run --name generaptor \
                          --rm \
                          -v /data/generaptor/cache:/generaptor/cache \
                          -v /data/generaptor/config:/generaptor/config \
                          -v /data/generaptor/output:/output \
                          -it \
                          cert-edf/generaptor update
# generate windows default collector
sudo docker container run --name generaptor \
                          --rm \
                          -v /data/generaptor/cache:/generaptor/cache \
                          -v /data/generaptor/config:/generaptor/config \
                          -v /data/generaptor/output:/output \
                          -it \
                          cert-edf/generaptor generate windows
```

