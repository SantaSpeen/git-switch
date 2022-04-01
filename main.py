# -*- coding: utf-8 -*-

# noinspection GrazieInspection
"""
    Программа для клонирования репозиториев с https://github.com/ на https://gitflic.ru
    Программа была написана: @dikola
    Программа была отрефакторена: @SantaSpeen
"""

# Типы. Используется для <того, что бы тебя любило IDE>.
from typing import NoReturn, Union

# Удобная и встроенная в Python библиотека логирования. Подробнее: https://docs.python.org/3.10/library/logging.html
import logging
# Встроенные библиотеки. Нужны для некоторых функций прогрммы.
import os
import sys
import time

# Библиотека для работы с аргументами. Подробнее: https://click.palletsprojects.com/en/8.0.x
import click
# Библиотека для работы c GitHub API. Подробнее: https://github.com/PyGithub/PyGithub
from github import Github, AuthenticatedUser, PaginatedList
# Библиотека для работы с Gitflic API. Подробнее: https://github.com/SantaSpeen/gitflic
from gitflic import GitflicAuth, Gitflic
# Библиотека для работы с git. Подробнее про систему git: https://habr.com/ru/post/588801/
from git import Repo
#
import requests

# Инициализируем логирование
log_format = "%(asctime)s - %(name)-5s - %(levelname)-5s - %(message)s"
logging.basicConfig(level=logging.INFO,
                    format=log_format)
log = logging.getLogger(name="GitSwitch")

# Настройка логирование в файл.
fh = logging.FileHandler('git-switch.log')
fh.setLevel(logging.INFO)
fh.setFormatter(logging.Formatter(log_format))
log.addHandler(fh)


class GitSwitch:

    # noinspection PyTypeChecker
    def __init__(self,
                 gf_token: str,
                 gh_token: str,
                 clone_folder: str,
                 apply_private: bool,
                 apply_organisations: bool,
                 use_ssh: bool):

        self.gf_token = gf_token
        self.gh_token = gh_token

        self.clone_folder = clone_folder
        self.apply_private = apply_private
        self.apply_organisations = apply_organisations
        self.use_ssh = use_ssh

        self.gf: Gitflic = None
        self.gh: Github = None
        self.gh_user: AuthenticatedUser = None
        self.github_repos: PaginatedList = None

        self.gh_user_name = None
        self.get_login = None

        self.session: requests.Session = None

    def authorization(self) -> NoReturn:
        """ Авторизуемся и получаем список репозиториев с GitHub """
        gf_session = GitflicAuth(self.gf_token)
        self.gf = Gitflic(gf_session)
        self.session = gf_session.session
        log.info(f"Logged into GitFlic as {self.gf.call('/user/me')['username']}")
        self.gh = Github(self.gh_token)
        self.gh_user = self.gh.get_user()
        log.info(f"Logged into Github as {self.gh_user.login}")

        self.github_repos = self.gh_user.get_repos()
        self.gh_user_name = self.gh_user.login
        self.get_login = lambda repo_info: repo_info.organization.login if repo_info.organization else self.gh_user_name

    def get_github_repo(self, repo_info) -> Union[Repo, None]:
        """ Получаем репозиторий с GitHub """
        login = self.get_login(repo_info)
        name = repo_info.name
        path = os.path.join(self.clone_folder, login, name)
        proto = "https://"
        if not os.path.exists(path):
            clone_url = repo_info.clone_url.replace(proto, proto + self.gh_token + '@')
            log.info(f'Clone {login} : {name}; Clone path: {path};')
            return Repo.clone_from(clone_url, path)

        log.info(f"Path: {path} already exists.")
        return None

    def get_gitflic_repo(self, repo_info) -> Union[dict, None]:
        """ Создаём репозиторий на гитфлике """
        login = self.get_login(repo_info)
        title = f"{login}-{repo_info.name}" if login != self.gh_user_name else repo_info.name
        congfig = {
            "title": title,
            "description": f"{repo_info.description}",
            "alias": title,
            "language": f"{repo_info.language}",
            "private": "true"
        }
        repo_object = self.session.post("https://api.gitflic.ru/project", json=congfig)

        code = repo_object.status_code
        if code != 200:
            log.error(f"GitGlic api send {repo_object.status_code} HTTP Error.")
            if code == 429:
                log.info("Waiting 10 seconds and try again.")
                time.sleep(10)
                return self.get_gitflic_repo(repo_info)
            log.warning("Skip repository.")
            return

        jsn = repo_object.json()
        log.info(f"Sucsessfully created new empty repo: {jsn['httpTransportUrl'][:-3]}")
        return jsn

    @staticmethod
    def push_into_gitflic(repo, url) -> bool:
        """ Пушим репозиторий на GitFlic """
        try:
            remote = repo.create_remote("gitflic", url=url)
            remote.push(refspec='--all')
            return True
        except Exception as e:
            print(f"Exception while pushing: {e}")
            return False

    def is_skip(self, repo_info) -> bool:
        if repo_info.private and not self.apply_private:
            return True
        if self.get_login(repo_info) != self.gh_user_name and not self.apply_organisations:
            return True

        return False

    def run(self) -> NoReturn:
        """ Запуск основной части """
        for repo_info in self.github_repos:
            if self.is_skip(repo_info): continue
            github_repo = self.get_github_repo(repo_info)
            if not github_repo: continue
            gitflic_repo = self.get_gitflic_repo(repo_info)
            if not gitflic_repo: continue
            if self.push_into_gitflic(github_repo, gitflic_repo['sshTransportUrl' if self.use_ssh else 'httpTransportUrl']):
                log.info(f"Repository {self.get_login(repo_info)}/{repo_info.name} successfully cloned.")

    def start(self) -> NoReturn:
        self.authorization()

        i = j = 0
        log.info("GitHub repositories:")
        for repo in self.github_repos:
            skip = self.is_skip(repo)
            if skip:
                j += 1
                log.info(f'[SKIP] GitGub => {self.get_login(repo)} : {repo.name};')
                continue
            i += 1
            log.info(f'GitGub => {self.get_login(repo)} : {repo.name}')
        log.info(f"Repositories found: {i+j}. Repositories to copy: {i}. Ignored repositories: {j}.")

        if input("Do you agree to copying these repositories to GitFlic? (y/n) ").lower() != "y":
            log.info("Stopped by the user.")
            exit(0)

        self.run()


# Инициализируем наши аргументы
@click.command()
@click.option("--gf_token", help="Your GitFlic token.", type=str, required=True)
@click.option("--gh_token", help="Your GitHub token.", type=str, required=True)
@click.option("--apply_private", help="Need to copy private repositories?", default=False, required=False)
@click.option("--apply_organisations", help="Need to copy organisations repositories?", default=False, required=False)
@click.option("--use_ssh", help="Use SSH mode to upload repositories.", default=False, required=False)
@click.option("--clone_folder", help="Directory where to download repositories.", default="./cloned-repos", required=False)
def main(**kwargs):
    log.info("New log start.")
    log.info(f"Local time: {time.asctime()}")
    log.info(f"GitSwitch start with: {sys.argv} argumets.")
    try:
        gs = GitSwitch(**kwargs)
        gs.start()
    except Exception:
        log.exception("GitSwitch send error:")
    finally:
        log.info(f"Exiting at {time.asctime()}\n{'-----'*20}")


if __name__ == '__main__':
    main()
