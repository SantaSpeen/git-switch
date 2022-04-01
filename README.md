# GitSwitch

<p class="text-center" align="center">
    <a href="https://gitflic.ru/project/dbi471/git-switch/blob?file=LICENSE"><img alt="License" src="https://img.shields.io/github/license/SantaSpeen/git-switch?style=for-the-badge"></a>    
    <a href="#"><img alt="GitHub stars" src="https://img.shields.io/github/stars/SantaSpeen/git-switch?style=for-the-badge"></a>    
    <a href="https://gitflic.ru/user/santaspeen"><img src="https://img.santaspeen.ru/github/magic.svg" alt="magic"></a>
</p>

A tool that will help you copy repositories from GitHub into GitFlic.

## Installation

```shell
# Shell

$ pip3 install -r requirements.txt
```

If you don't have python installed, download it from [http://python.org/](http://python.org/).

## Usage

```shell
# Shell

$ python3 main.py --help
```

Then: 

* Get GitHub token from: [https://github.com/settings/tokens](https://github.com/settings/tokens)
* Get GitFlic token from: [https://github.com/settings/tokens](https://gitflic.ru/settings/oauth/token)

If you are using 2AF into GitFlic select ssh connection using the key: `--use_ssh true`.

The script will copy all the necessary repositories to `./cloned-repos/<login>/<repo_name>`, then push it to GitFlic
