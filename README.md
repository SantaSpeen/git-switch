# GitSwitch

A tool that will help you copy repositories from GitHub into GitFlic.

## Installation

```shell
# Shell

$ pip3 install -r requirements.txt
```


## Usage

Get GitHub token from: https://github.com/settings/tokens \
Get GitFlic token from: https://gitflic.ru/settings/oauth/token

```shell
# Shell

python3 main.py --help
```

The script if going to clone all the repos for a given access token under `./cloned-repos/<login>/<repo_name>`.
