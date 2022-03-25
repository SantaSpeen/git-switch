# GitSwitch

Helper tools to move all you repos from GitHub into GitFlic

## Installation

```shell
# Shell

$ pip install -r requirements.txt
```


## Usage

Get GitHub token from: https://github.com/settings/tokens \
Get GitFlic token from: https://gitflic.ru/settings/oauth/token

```shell
# Shell

python main.py \
       --token=<your_access_token> \
       --dst_folder=<your_folder> \
	   --gitflic_token=<your_gitflic_token> \
	   --is_private=<True/False>
```

The script if going to clone all the repos for a given access token under `dst_folder/org_name/repo_name`.
