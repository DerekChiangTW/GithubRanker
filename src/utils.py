#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import numpy as np
from random import shuffle


def get_top30_stars(path):
    stars = {}
    with open(path, 'r') as infile:
        for line in infile:
            pair = line.rstrip().split(",")
            stars[pair[0]] = int(pair[1])
    return stars


def get_top30(path):
    top30 = [line.rstrip().split(",")[0] for line in open(path, 'r')]
    return top30


def get_relevance(path):
    stars = get_top30_stars(path)
    relevance = {}
    for user, star in stars.items():
        relevance[user] = int(star / 10000)
    return relevance


def get_all_users(path):
    users = [line.rstrip() for line in open(path, 'r')]
    return users


def get_all_repos(path):
    repos = [line.rstrip() for line in open(path, 'r')]
    return repos


def pairwise(x):
    N = len(x)
    tuple_list = []
    for i in range(N - 1):
        for j in range(i + 1, N):
            tuple_list.append((x[i], x[j]))
    return tuple_list


def rank_of_list(lst):
    indices = list(range(len(lst)))
    indices.sort(key=lambda x: lst[x], reverse=True)
    rank = [0 for i in range(len(lst))]
    for i, pos in enumerate(indices):
        rank[pos] = i + 1
    return rank


def compute_dcg(x):
    denom = np.array([np.log2(2 + i) for i in range(len(x))])
    return np.sum(np.array(x) / denom)


def compute_ndcg(x, num=10):
    """ Return the nDCG@num. """
    dcg = compute_dcg(x[:num])
    idcg = compute_dcg(sorted(x, reverse=True)[:num])
    ndcg = (dcg / idcg) if idcg != 0.0 else -1
    return ndcg


def save_neighbors(output_dir, all_users, repo_info):
    # Find the neighbors of each user
    neighbors = {user: set() for user in all_users}
    for repo, info in repo_info.items():
        contr = info['contributors']
        if len(contr.keys()) < 2:
            continue
        else:
            pair_list = pairwise(list(contr.keys()))
            for p1, p2 in pair_list:
                neighbors[p1].add(p2)
                neighbors[p2].add(p1)
    neighbors = {user: list(neighs) for user, neighs in neighbors.items()}

    path = os.path.join(output_dir, 'neighbors.json')
    with open(path, 'w') as outfile:
        json.dump(neighbors, outfile, indent=4, sort_keys=True, separators=(',', ':'))
    print("The file: {} is written and saved.".format(path))


def load_neighbors(path):
    neighbors = json.load(open(path, 'r'))
    return neighbors


def save_related_repos(output_dir, all_users, user_info):
    neighbors = load_neighbors(os.path.join(output_dir, 'neighbors.json'))

    user_repo = {}
    for user in all_users:
        related_repos = []
        written_repos = user_info[user]["written_repos"]

        # find related repos
        for neighbor in neighbors[user]:
            related_repos += user_info[neighbor]["written_repos"]
        related_repos = set(related_repos)
        related_repos = [repo for repo in related_repos if repo not in written_repos]

        user_repo[user] = {
            "written": written_repos,
            "related": related_repos
        }

    path = os.path.join(output_dir, 'related_repos.json')
    with open(path, 'w') as outfile:
        json.dump(user_repo, outfile, indent=4, sort_keys=True, separators=(',', ':'))
    print("The file: {} is written and saved.".format(path))


def load_related_repos(path):
    user_repo = json.load(open(path, 'r'))
    return user_repo


def create_fm_train_data(output_dir, all_users, all_repos, user2idx, repo2idx, repo_info):
    path = os.path.join(output_dir, "train.txt")
    outfile = open(path, 'w')

    user_repo = load_related_repos(os.path.join(output_dir, 'related_repos.json'))
    for user, repos in user_repo.items():
        related_repos = repos["related"]
        written_repos = repos["written"]
        unrelated_repos = [x for x in all_repos if x not in related_repos and x not in written_repos]
        for repo in written_repos:
            label = "1"
            user_idx = user2idx[user]
            repo_idx = repo2idx[repo]
            features = str(user_idx) + ":1.0 " + str(len(all_users) + repo_idx) + ":1.0 "
            data = " ".join([label, features])
            outfile.write(data + '\n')

        num_negative_samples = 4 * len(written_repos)
        shuffle(unrelated_repos)
        negative_samples = unrelated_repos[:num_negative_samples]
        for repo in negative_samples:
            label = "0"
            user = repo_info[repo]["owner"]
            user_idx = user2idx[user]
            repo_idx = repo2idx[repo]
            features = str(user_idx) + ":1.0 " + str(len(all_users) + repo_idx) + ":1.0 "
            data = " ".join([label, features])
            outfile.write(data + '\n')
    print("The file: {} is written and saved.".format(path))


def create_fm_test_data(output_dir, all_users, user2idx, repo2idx):
    path = os.path.join(output_dir, "test.txt")
    outfile = open(path, 'w')

    user_repo = load_related_repos(os.path.join(output_dir, 'related_repos.json'))
    for user, repos in user_repo.items():
        related_repos = repos["related"]
        for repo in related_repos:
            label = "0"
            user_idx = user2idx[user]
            repo_idx = repo2idx[repo]
            features = str(user_idx) + ":1.0 " + str(len(all_users) + repo_idx) + ":1.0 "
            data = " ".join([label, features])
            outfile.write(data + '\n')
    print("The file: {} is written and saved.".format(path))


def compute_fm_score(output_dir, all_users, idx2user):
    # get the fm predictions
    preds = [float(line.rstrip()) for line in open(os.path.join(output_dir, "predictions.txt"), 'r')]

    # get the corresponding user for each predictions from test file
    user_indices = [int(line.split(" ")[1].split(":")[0])
                    for line in open(os.path.join(output_dir, "test.txt"), 'r')]
    pred_users = [idx2user[ind] for ind in user_indices]

    # compute fm scores
    user_repo = load_related_repos(os.path.join(output_dir, 'related_repos.json'))
    fm_scores = {user: len(user_repo[user]["written"]) for user in all_users}
    for user, pred in zip(pred_users, preds):
        fm_scores[user] += pred
    return fm_scores


def compute_w_fm_score(output_dir, all_users, idx2user):
    # get the fm predictions
    preds = [float(line.rstrip()) for line in open(os.path.join(output_dir, "predictions.txt"), 'r')]

    # get the corresponding user for each predictions from test file
    user_indices = [int(line.split(" ")[1].split(":")[0])
                    for line in open(os.path.join(output_dir, "test.txt"), 'r')]
    pred_users = [idx2user[ind] for ind in user_indices]

    # compute fm scores
    user_repo = load_related_repos(os.path.join(output_dir, 'related_repos.json'))
    fm_scores = {user: len(user_repo[user]["written"]) for user in all_users}
    for user, pred in zip(pred_users, preds):
        fm_scores[user] += 0.2
    return fm_scores


def compute_contribution(output_dir, all_users):
    repo_info = json.load(open(os.path.join(output_dir, 'repos_info.json'), 'r'))
    contributions = {user: 0 for user in all_users}
    for repo, info in repo_info.items():
        contributors = info["contributors"]
        for user, contr in contributors.items():
            contributions[user] += contr
    return contributions
