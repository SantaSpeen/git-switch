# -*- coding: utf-8 -*-

# noinspection GrazieInspection
"""
    Программа для клонирования репозиториев с https://github.com/ на https://gitflic.ru
    Программа была написана: @dikola
    Программа была отрефакторена: @SantaSpeen
"""

# Удобная и встроенная в Python библиотека логирования. Подробнее: https://docs.python.org/3.10/library/logging.html
import logging
import os
import sys
import time

# Библиотека для работы с аргументами. Подробнее: https://click.palletsprojects.com/en/8.0.x
from typing import NoReturn, Union

import click
# Библиотека для работы c GitHub API
from github import Github, AuthenticatedUser, PaginatedList
# Библиотека для работы с Gitflic API
from gitflic import GitflicAuth, Gitflic
# Библиотека для работы с git
from git import Repo


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
    def __init__(self, gf_token: str, gh_token: str, dist_folder: str, apply_private: bool, apply_organisations: bool):
        self.gf_token = gf_token
        self.gh_token = gh_token

        self.clone_folder = dist_folder
        self.apply_private = apply_private
        self.apply_organisations = apply_organisations

        self.gh: Gitflic = None
        self.gf: Github = None
        self.gh_user: AuthenticatedUser = None

        self.github_repos: PaginatedList = None

        self.get_login = lambda repo_info: repo_info.organization.login if repo_info.organization else self.gh_user.login

    def authorization(self) -> NoReturn:
        """ Авторизуемся и получаем список репозиториев с GitHub """
        gf_session = GitflicAuth(self.gf_token)
        self.gf = Gitflic(gf_session)
        log.info(f"Logged into GitFlic as {self.gf.call('/user/me')['username']}")
        self.gh = Github(self.gh_token)
        self.gh_user = self.gh.get_user()
        log.info(f"Logged into Github as {self.gh_user.login}")

        self.github_repos = self.gh_user.get_repos()

    def get_github_repo(self, repo_info) -> Union[Repo, None]:
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

    def get_gitflic_repo(self) -> Union[dict, None]:
        """ Я хуй знает что тут писать. Какой нахуй localhost? Бесплатный блять host или чё? """
        pass

    def push_into_gitflic(self, repo, url) -> bool:
        return False

    def clone(self):
        for repo_info in self.github_repos:
            github_repo = self.get_github_repo(repo_info)
            if not github_repo: continue
            gitflic_repo = self.get_gitflic_repo()
            if not gitflic_repo: continue
            if self.push_into_gitflic(github_repo, gitflic_repo['sshTransportUrl']):
                log.info(f"Repository {self.get_login(repo_info)}-{repo_info.name} successfully cloned.")

    def start(self) -> NoReturn:
        self.authorization()

        log.info("GitHub repositories:")
        for repo in self.github_repos:
            log.info(f'GitGub => {self.get_login(repo)} : {repo.name}')
        log.info(f"Repositories found: {self.github_repos.totalCount}")

        if input("Do you agree to copying these repositories to GitFlic? (y/n) ").lower() != "y":
            log.info("Stopped by the user.")
            exit(0)

        self.clone()


# Инициализируем наши аргументы
@click.command()
@click.option("--gf_token", help="Your GitFlic token.", type=str, required=True)
@click.option("--gh_token", help="Your GitHub token.", type=str, required=True)
@click.option("--dist_folder", help="Directory where to download repositories.", default="./cloned-repos", required=False)
@click.option("--apply_private", help="Need to copy private repositories or not.", default=False, required=False)
@click.option("--apply_organisations", help="Need to copy organisations repositories or not.", default=False, required=False)
def main(**kwargs):
    log.info("New log start.")
    log.info(f"Local time: {time.asctime()}")
    log.info(f"GitSwitch start with: {sys.argv} argumets.")

    gs = GitSwitch(**kwargs)
    gs.start()


if __name__ == '__main__':
    main()
