# Generaptor


## Introduction

Generaptor is a platform-agnostic command line tool to generate a [Velociraptor](https://github.com/velocidex/velociraptor) offline collector based on pre-configured or customizable collection profiles.

All platforms can generate collectors for all targets, there is no limitation thanks to Python on the generation side and velociraptor on the configuration repacking side.

Generation of Darwin collector is not implemented for the moment due to the lack of use case on our side. Feel free to open a pull request regarding this feature.


## Dependencies

Dependencies are listed in [pyproject.toml](pyproject.toml) under `dependencies` option.


## Setup

The setup is the same for Linux, Windows and Darwin as long as Python 3.12+ is
installed and registered in the PATH environment variable. Using a Python virtual
environment is recommended.

```bash
# install without interactive prompt support
python3 -m pip install git+https://github.com/cert-edf/generaptor
# install with interactive prompt support
python3 -m pip install 'generaptor[pick] @ git+https://github.com/cert-edf/generaptor'
```


## Basic Collector Generation

```bash
# First, we fetch latest stable release of velociraptor
generaptor update
# Then create a collector for windows for instance
generaptor generate -o /data/case/case-001/collectors/ windows
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
# Collector targets customization
# (require interactive prompt support, see setup)
generaptor generate --custom windows
# Collector targets customization using a profile (non interactive)
echo '{"targets":["WebServer/IIS"]}' > ~/.config/generaptor/windows/iis_server.json
generaptor generate --profile iis_server windows
```


## Expert Collector Generation

Generaptor can use optional configuration files put in `$HOME/.config/generaptor` directory to generate collectors.

Target and rules can be extended using this configuration directory.

VQL templates can also be modified to add custom artifacts or modify the collector behavior. Please refer to [Velociraptor documentation](https://docs.velociraptor.app/) to learn how to master VQL and write your own configuration files.

After starting generaptor for the first time, you can use the following commands to initialize the configuration directory

```bash
# Add variables for directories in current environment
export CACHE="${HOME}/.cache/generaptor"
export CONFIG="${HOME}/.config/generaptor"
# Copy header for each file
head -n 1 "${CACHE}/config/linux/rules.csv" > "${CONFIG}/linux/rules.csv"
head -n 1 "${CACHE}/config/linux/targets.csv" > "${CONFIG}/linux/targets.csv"
head -n 1 "${CACHE}/config/windows/rules.csv" > "${CONFIG}/windows/rules.csv"
head -n 1 "${CACHE}/config/windows/targets.csv" > "${CONFIG}/windows/targets.csv"
# Copy VQL templates
cp "${CACHE}/config/linux/collector.yml.jinja" "${CONFIG}/linux/"
cp "${CACHE}/config/windows/collector.yml.jinja" "${CONFIG}/windows/"
```


## Collection Processing

```bash
# Extract a collection
generaptor extract \
           --directory /data/case/case-001/collection/ \
           private.key.pem \
           Collection_COMPUTERNAME_DEVICENAME_YYYY-mm-ddTHH-MM-SS.zip
```
