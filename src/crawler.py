#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import requests
from utils import get_groundTruth

user_agent = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6)'
              'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36')
header = {'User-Agent': user_agent}

# Increase the unauthenticated rate limit for OAuth applications to 5000
payload = {'client_id': 'e5f977a68ace627a1760',
           'client_secret': 'aa9e159b082180e875a96d68d84e26324771e5b4'}


def get_json(url):
    try:
        # response = requests.get(url)
        response = requests.get(url, headers=header, params=payload)
        response.raise_for_status()
        obj = None
        if int(response.headers['X-RateLimit-Remaining']) < 10:
            print("The rate limit remaining is less than 10.")
        else:
            obj = response.json()
    except requests.exceptions.ConnectionError:
        print("Failed to reach a server.")
    except requests.exceptions.Timeout:
        print("The request has timed out.")
    except requests.exceptions.HTTPError:
        print("Bad request:", url, response.headers['Status'])

    return obj


def get_repo(full_repo_name):
    repo_url = os.path.join("https://api.github.com/repos", full_repo_name)
    return get_json(repo_url)


def get_user(user_name):
    user_url = os.path.join("https://api.github.com/users", user_name)
    return get_json(user_url)


def write_top30_repo(input_file, include_fork=True):
    """ Write the Python repositories of the top 30 users to output file.

    @Parameters
    -----------
    input_file: The file which includes the top 30 users.
    include_fork: Whether to include the forked repositories.

    """
    # Get the top 30 users
    gt = get_groundTruth(input_file)
    top_users = gt.keys()

    # Retrieve the Python repositories of the top users
    total_repo_list = []
    for user in top_users:
        count = 0
        cur_page = 1
        while True:
            url = os.path.join("https://api.github.com/users", user, "repos?page=" + str(cur_page))
            repo_list = get_json(url)
            if not repo_list:
                break
            if include_fork:
                for repo in repo_list:
                    if repo["language"] == "Python":
                        total_repo_list.append(repo["full_name"])
                        count += 1
            else:
                for repo in repo_list:
                    if repo["language"] == "Python" and not repo["fork"]:
                        total_repo_list.append(repo["full_name"])
                        count += 1
            cur_page += 1
        print("{}: {}".format(user, count))
    print("Total number of retrieved repositories: {}".format(len(total_repo_list)))

    # Set the output directory
    output_dir = os.path.join('..', 'output')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Write the repo list to output file
    if include_fork:
        output_path = os.path.join(output_dir, 'top30_repos.txt')
    else:
        output_path = os.path.join(output_dir, 'top30_repos_wo_fork.txt')
    print("Writing to {}".format(output_path))
    with open(output_path, 'w') as outfile:
        for repo in total_repo_list:
            outfile.write(repo + '\n')


def write_repo_contributors(input_path):
    """ Retrieve the contributors of all repos and write their names to file.

    @Parameters
    -----------
    input_path: The path of file which contains the repositories of the top30 users.

    """
    contributors_names = set()
    with open(input_path, 'r') as infile:
        for line in infile:
            full_repo_name = line.rstrip()
            print("Processing: {}".format(full_repo_name))
            cur_page = 1
            while True:
                url = os.path.join("https://api.github.com/repos", full_repo_name,
                                   "contributors?page=" + str(cur_page))
                contributor_list = get_json(url)
                if not contributor_list:
                    break
                for user in contributor_list:
                    contributors_names.add(user["login"])
                cur_page += 1
    print("Total number of contributors: {}".format(len(contributors_names)))

    # Set the output directory
    output_dir = os.path.join('..', 'output')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_path = os.path.join(output_dir, 'all_users.txt')
    print("Writing to {}".format(output_path))
    with open(output_path, 'w') as outfile:
        for user in contributors_names:
            outfile.write(user + '\n')


if __name__ == "__main__":
    # write_top30_repo("top30-award.txt")
    # write_top30_repo("top30-award.txt", include_fork=False)
    # write_repo_contributors(os.path.join('..', 'output', 'top30_repos_wo_fork.txt'))
    pass
