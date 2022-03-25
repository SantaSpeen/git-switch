# -*- coding: utf-8 -*-

# noinspection GrazieInspection
"""
    Программа для клонирования репозиториев с https://github.com/ на https://gitflic.ru
    Программа была написана: @dikola
    Программа была отрефакторена: @SantaSpeen
"""

# Удобная и встроенная в Python библиотека логирования. Подробнее: https://docs.python.org/3.10/library/logging.html
import logging
import sys
import time

# Библиотека для работы с аргументами. Подробнее: https://click.palletsprojects.com/en/8.0.x
import click
# Библиотека для работы c GitHub API
from github import Github, AuthenticatedUser, PaginatedList
# Библиотека для работы с Gitflic API
from gitflic import GitflicAuth, Gitflic

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
    def __init__(self, gf_token: str, gh_token: str, dist_folder: str, is_private: bool):
        self.gf_token = gf_token
        self.gh_token = gh_token

        self.dist_folder = dist_folder
        self.is_private = is_private

        self.gh: Gitflic = None
        self.gf: Github = None
        self.gh_user: AuthenticatedUser = None

        self.github_repos: PaginatedList = None

    def authorization(self):
        """ Авторизуемся и получаем список репозиториев с GitHub """
        gf_session = GitflicAuth(self.gf_token)
        self.gf = Gitflic(gf_session)
        log.info(f"Logged into GitFlic as {self.gf.call('/user/me')['username']}")
        self.gh = Github(self.gh_token)
        self.gh_user = self.gh.get_user()
        log.info(f"Logged into Github as {self.gh_user.login}")

        self.github_repos = self.gh_user.get_repos()

    def start(self):
        self.authorization()

        log.info("Fouded github repositories:")
        for repo in self.github_repos:
            login = repo.organization.login if repo.organization else self.gh_user.login
            log.info(f'GitGub => {login} : {repo.name}')
        log.info(f"Repositories found: {self.github_repos.totalCount}")


# Инициализируем наши аргументы
@click.command()
@click.option("--gf_token", help="Your GitFlic token.", type=str, required=True)
@click.option("--gh_token", help="Your GitHub token.", type=str, required=True)
@click.option("--dist_folder", help="A folder to clone repositories into.", default="./cloned-repos", required=False)
@click.option("--is_private", help="Sets the mode for copying repositories.", default=True, required=False)
def main(**kwargs):
    log.info("New log start.")
    log.info(f"Local time: {time.asctime()}")
    log.info(f"GitSwitch start with: {sys.argv} argumets.")

    gs = GitSwitch(**kwargs)
    gs.start()


if __name__ == '__main__':
    main()
