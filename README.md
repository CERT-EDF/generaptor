# Generaptor


## Contributors

- [koromodako](https://github.com/koromodako)


## Introduction

Generaptor is a platform-agnostic command line tool to generate a
[Velociraptor](https://github.com/velocidex/velociraptor) offline collector
based on pre-configured or customizable collection profiles.

All platforms can generate collectors for all targets, there is no limitation
thanks to Python on the generation side and velociraptor on the configuration
repacking side. Generation of Darwin collector is not implemented for the moment.

## Dependencies

Dependencies are listed in [setup.cfg](setup.cfg) under `install_requires` option.


## Setup

The setup is the same for Linux, Windows and Darwin as long as Python 3.9+ is
installed and registered in the PATH environment variable. Using a Python virtual
environment is recommended.

```bash
python3 -m pip install git+https://github.com/cert-edf/generaptor
```


## Basic Collector Generation

```bash
# First, we fetch latest stable release of velociraptor
generaptor refresh
# When installing a new version of generaptor, embedded configuration files are
# not deployed automatically in the cache to prevent overwriting of potential
# changes made by the user. You can force the update of configuration files
# using --refresh-config and skip velociraptor release upgrade using --do-not-fetch
generaptor refresh --refresh-config --do-not-fetch
# Then create a collector for windows for instance
generaptor generate -o /data/case/case-001/collectors windows
# keep the private key secret in a password vault to be able to decrypt the archive
# /data/case/case-001/collectors now contains a collector and its configuration file
```


## Advanced Collector Generation

Some options allow to customize collectors:

```bash
# Explore generate options using
generaptor generate -h
# Explore linux-specific options using
generaptor generate linux -h
# Explore windows-specific options using
generaptor generate windows -h
# Generate a single-device collector for windows
# (windows default collector collects all devices)
generaptor generate windows --device D:
# Collector targets customization (interactive)
generaptor generate --custom windows
# Collector targets customization using a profile (non interactive)
echo '{"targets":["IISLogFiles"]}' > iis_server.json
generaptor generate --custom-profile iis_server.json windows
```


## Expert Collector Generation

Generaptor creates a cache directory and puts all the files it uses to generate
collectors: velociraptor binaries and template configuration files.

Configuration templates can be modified to add custom artifacts or modify the
collector behavior.

Please refer to [Velociraptor documentation](https://docs.velociraptor.app/) to
learn how to master VQL and write your own configuration files.


## Collection Processing

```bash
# get the archive certificate fingerprint to identify matching private key
generaptor get-fingerprint Collection_COMPUTERNAME_DEVICENAME_YYYY-mm-ddTHH-MM-SS.zip
# fingerprint is displayed
# --
# get the archive password using private key
generaptor get-secret private.key.pem Collection_COMPUTERNAME_DEVICENAME_YYYY-mm-ddTHH-MM-SS.zip
# archive secret is displayed
# --
# use 7zip to extract archive data and type previously retrieved archive secret
# when prompted for archive password
```
