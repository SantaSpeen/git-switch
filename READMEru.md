# GitSwitch

<p class="text-center" align="center">
    <a href="https://gitflic.ru/project/dbi471/git-switch/blob?file=LICENSE"><img alt="License" src="https://img.shields.io/github/license/SantaSpeen/git-switch?style=for-the-badge"></a>    
    <a href="#"><img alt="GitHub stars" src="https://img.shields.io/github/stars/SantaSpeen/git-switch?style=for-the-badge"></a>    
    <a href="https://gitflic.ru/user/santaspeen"><img src="https://img.santaspeen.ru/github/magic.svg" alt="magic"></a>
</p>

Инструмент, который поможет вам скопировать репозитории из GitHub в GitFlic.

## Установка

```shell
# Shell

$ pip3 install -r requirements.txt
```

Если у вас не установлен питон, скачайте с [http://python.org/](http://python.org/).\
Актуально для windows.

## Использование 

```shell
# Shell

$ python3 main.py --help
```

Изучив аргументы:

* Получите GitHub токен отсюда: [https://github.com/settings/tokens](https://github.com/settings/tokens)
* Получите GitFlic токен отсюда: [https://github.com/settings/tokens](https://gitflic.ru/settings/oauth/token)

Если у вас подключена 2AF в GitFlic используйте ssh: `--use_ssh true`.

Скрипт скопирует все нужные репозитории в `./cloned-repos/<login>/<repo_name>`, затем запушит их в GitFlic.
