#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import requests
from utils import get_groundTruth

user_agent = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 '
              '(KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36')
header = {'User-Agent': user_agent}

# Increase the rate limit for OAuth applications to 5000
payload = {'client_id': 'e5f977a68ace627a1760',
           'client_secret': 'aa9e159b082180e875a96d68d84e26324771e5b4'}

input_dir = os.path.join('..', 'data')
output_dir = os.path.join('..', 'output')


def get_json(url, headers=header, params=payload):
    # r = requests.get(url)
    r = requests.get(url, headers=header, params=payload)
    r.raise_for_status()
    obj = r.json()
    # print("The rate limit remaining: {}".format(int(r.headers['X-RateLimit-Remaining'])))
    return obj


def get_repo(full_repo_name):
    repo_url = os.path.join("https://api.github.com/repos", full_repo_name)
    return get_json(repo_url)


def get_user(user_name):
    user_url = os.path.join("https://api.github.com/users", user_name)
    return get_json(user_url)


def get_user_repos(user_name, include_fork=False):
    """ Retrieve the Python repositories of a single user.

    @Parameters
    -----------
    user_name: The name of user
    include_fork: Whether to include forked repositories

    @Returns
    --------
    repo_list: The user's Python repository list

    """
    repo_list = []
    cur_page = 1
    print("Retrieving the repos of user: {}".format(user_name))
    while True:
        url = os.path.join("https://api.github.com/users", user_name, "repos?page=" + str(cur_page))
        obj = get_json(url)
        if not obj:     # break if it's an empty page
            break

        print("Processing page: {}".format(cur_page))
        if include_fork:
            for repo in obj:
                if repo["language"] == "Python":
                    repo_list.append(repo["full_name"])
        else:
            for repo in obj:
                if repo["language"] == "Python" and not repo["fork"]:
                    repo_list.append(repo["full_name"])
        cur_page += 1
    print("Successfully processed user: {}, # of repos: {}\n".format(user_name, len(repo_list)))
    return repo_list


def write_top30_repo(input_path, output_path, include_fork=False):
    """ Write the Python repositories of the top 30 users to output file.

    @Parameters
    -----------
    input_path: The path of input file which contains the top 30 users
    output_path: The output file path
    include_fork: Whether to include forked repositories

    """
    # Get the top 30 users
    gt = get_groundTruth(input_path)
    top_users = gt.keys()

    # Retrieve the Python repositories of the top users
    print("Writing to {}".format(output_path))
    with open(output_path, 'w') as outfile:
        for user in top_users:
            repo_list = get_user_repos(user, include_fork=include_fork)
            if not repo_list:
                continue
            for repo in repo_list:
                outfile.write(repo + '\n')
    print("Successfully saved {}".format(output_path))


def write_contributors(input_path, output_path):
    """ Write the contributors of repos owned by the top 30 users to file.

    @Parameters
    -----------
    input_path: The path which contains the repos of top 30 users.
    output_path: The output file path

    """
    contributors = set()
    with open(input_path, 'r') as infile:
        for line in infile:
            full_repo_name = line.rstrip()
            print("\nGet the contributors of repo: {}".format(full_repo_name))
            cur_page = 1
            while True:
                url = os.path.join("https://api.github.com/repos", full_repo_name,
                                   "contributors?page=" + str(cur_page))
                obj = get_json(url)
                if not obj:     # break if it's an empty page
                    break

                print("Processing page: {}".format(cur_page))
                for user in obj:
                    contributors.add(user["login"])
                cur_page += 1
    print("Total number of contributors: {}".format(len(contributors)))

    # Write the contributor names to output file
    print("Writing to {}".format(output_path))
    with open(output_path, 'w') as outfile:
        for user in contributors:
            outfile.write(user + '\n')
    print("Successfully saved {}".format(output_path))


def write_all_repositories(input_path, output_path, include_fork=False):
    """ Write all the repositories to output file.input_path

    @Parameters
    -----------
    input_path: The path which contains all the users
    output_path: The output file path
    include_fork: Whether to include forked repositories

    """
    # Read the entire user list
    remain_users = set()
    with open(input_path, 'r') as user_file:
        remain_users = {line.rstrip() for line in user_file}

    # Eliminate the users that are already examined
    examined_path = os.path.join('..', 'output', 'examined_users.txt')
    try:
        with open(examined_path, 'r') as examined_file:
            for line in examined_file:
                user = line.rstrip()
                remain_users.remove(user)
    except IOError:
        print("Examined user file {} does not exist.".format(examined_path))
    print("Number of remaining users: {}".format(len(remain_users)))

    # Get the repos of the remaining users and write them to output file
    with open(output_path, 'a') as repo_file, open(examined_path, 'a') as examined_file:
        current_user = None
        try:
            for user in remain_users:
                current_user = user
                repo_list = get_user_repos(user, include_fork=include_fork)

                # Write the examined user and repos to file
                examined_file.write(user + '\n')
                if not repo_list:
                    continue
                else:
                    for repo in repo_list:
                        repo_file.write(repo + '\n')
        except requests.exceptions.HTTPError:
            print("Exceeds rate limit, stop at user {}".format(current_user))
    print("Successfully saved {}".format(output_path))


if __name__ == "__main__":
    # Make the output directory
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Write the repos of top 30 users (without fork)
    input_path = os.path.join(input_dir, 'top30-award.txt')
    output_path = os.path.join(output_dir, 'top30_repos_wo_fork.txt')
    write_top30_repo(input_path, output_path)

    # Write the repos of top 30 users (with fork)
    input_path = os.path.join(input_dir, 'top30-award.txt')
    output_path = os.path.join(output_dir, 'top30_repos_w_fork.txt')
    write_top30_repo(input_path, output_path, include_fork=True)

    # Write all users
    input_path = os.path.join(output_dir, 'top30_repos_wo_fork.txt')
    output_path = os.path.join(output_dir, 'all_users.txt')
    write_contributors(input_path, output_path)

    # Write all repositories
    input_path = os.path.join(output_dir, 'all_users.txt')
    output_path = os.path.join(output_dir, 'all_repos.txt')
    write_all_repositories(input_path, output_path)
