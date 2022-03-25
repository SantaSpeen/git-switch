import os
import glob
import json

import argparse
import sys

from github import Github

from git import Repo

import requests

import logging
logger = logging.getLogger('log')
logger.setLevel(logging.INFO)

fh = logging.FileHandler('repos_log.log')
fh.setLevel(logging.INFO)
logger.addHandler(fh)

console = logging.StreamHandler(sys.stdout)
logging.getLogger().addHandler(console)


def parse_args():
    """
    Parses command line arguments.

    :return:
    """
    parser = argparse.ArgumentParser()

    parser.add_argument('--token', type=str,
                        help='GitHub access token')

    parser.add_argument('--gitflic_token', type=str,
                        help='GitFlic access token')

    parser.add_argument('--dst_folder', type=str, default='./cloned-repos',
                        help='A folder to clone repositories into.')

    parser.add_argument('--is_private', type=str,
                        help='Sets the mode for copying repositories.'
                             'True - copies only private repositories'
                             'False - copies only public repositories')
    return parser.parse_args()


def insert_token(clone_url: str,
                 token: str,
                 proto='https://'):
    """
    Inserts a token into a repo address.

    :param clone_url: url to insert token into
    :param token: GitHub access token
    :param proto: protocol
    :return: clone_url with token inserted
    """
    assert clone_url.startswith(proto)
    # "https://{token}@github.com/{username}/{repo}.git"
    authed_clone_url = clone_url.replace(proto, proto + token + '@')
    logger.info(f'Modified repo url: {authed_clone_url}')
    return authed_clone_url


def get_org_name(repo):
    """
    Parses organization name from a repo object.

    :param repo: GitHub repository
    :return: repo organization name if org is filled or 'default'
    """
    if not repo.organization:
        return 'default'
    return repo.organization.login

def get_description(repo):
    """
    Parses description from a repo object.

    :param repo: GitHub repository
    :return: repo empty description if description is empty
    """
    if not repo.organization:
        return ''
    return repo.organization.description

def clone_repos(repos,
                token: str,
                dst_dir: str,
                gitflic_token: str,
                is_private: bool):
    """
    Clone all repos(private and public) of a token holder.
    :param repos: GitHub repositories
    :param token: GitHub access token
    :param dst_dir: directory to clone repos into
    :return:
    """

    github_clonned = ''

    if os.path.exists("github_clonned.txt"):
        file = open("github_clonned.txt", "r")
        github_clonned = file.read()
        file.close()

    file = open("github_clonned.txt", "a+")

    for i, repo in enumerate(repos):
        id = repo.id
        name = repo.name
        private = repo.private
        org = get_org_name(repo)
        description = get_description(repo)
        language = repo.language

        logger.info(f'\nCopying {name}:')

        if str(id) in github_clonned:
            logger.info(f'Repository {org}/{name} already copied')
            continue

        if is_private is not None:
            if is_private.lower() == 'true' and not private:
                logger.info('Repository is public, skipping...')
                continue

            if is_private.lower() == 'false' and private:
                logger.info('Repository is private, skipping...')
                continue

        try:
            logger.info(f'Creating directory to copy.')
            local_path = os.path.join(dst_dir, org, name)
            os.makedirs(local_path)
            authed_clone_url = insert_token(repo.clone_url, token)

            logger.info(f'Cloning: {org}/{name} into {local_path}')
            github_repo = Repo.clone_from(authed_clone_url, local_path)
        except Exception:
            logger.info(f'Error copying repository from github. Probably repository has already been copied locally.')
            continue

        json_data = {
            "title": f"{org}-{name}",
            "description": f"{description}",
            "alias": f"{org}-{name}",
            "language": f"{language}",
            "private": "true"
        }

        try:
            logger.info(f'Creating repository {org}-{name} on gitflic.')
            # Создаём репозиторий на гитфлике
            gitflic_repo = requests.post(
                'http://localhost:8047/project',  # Это кто ??
                headers={
                    "Authorization": f"token {gitflic_token}",
                    "Content-Type": "application/json"
                },
                data=json.dumps(json_data)
            )

            if gitflic_repo.status_code == 429:
                logger.info(f'Request limit exceeded.')
                sys.exit()

        except Exception:
            logger.info(f'Error while creating repository on gitflic.')
            continue


        try:
            logger.info(f'Geting ssh link to repository...')
            gitflic_url = gitflic_repo.json().get("sshTransportUrl")

            logger.info(f'Establishing a connection to the repository...')
            remote = github_repo.create_remote("gitflic", url = gitflic_url)
        except Exception:
            logger.info(f'Error creating connection to gitflic repository.')
            continue

        try:
            logger.info(f'Pushing files into repository...')
            remote.push(refspec='--all')

            file.write(str(id) + '\n')
            logger.info(f'Repository {org}-{name} successfully cloned.')
        except Exception:
            logger.info(f'Error while pushing files into gitflic repository.')
            continue


if __name__ == '__main__':
    args = parse_args()

    token = args.token
    gitflic_token = args.gitflic_token
    dst_folder = args.dst_folder
    is_private = args.is_private

    g = Github(token)
    user = g.get_user()
    repos = user.get_repos()

    i = 0
    logger.info('Existing repos:')
    for i, repo in enumerate(repos):
        logger.info(f'ORG: {get_org_name(repo)} - REPO: {repo.name}')

    clone_repos(repos, token, dst_folder, gitflic_token, is_private)

    local_repos = glob.glob(dst_folder + '/*/*')
    # all repos are cloned
    assert i + 1 == len(local_repos)


