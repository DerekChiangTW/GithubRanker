#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
from src.utils import *
from scipy.stats import spearmanr, kendalltau

data_dir = os.path.join('data', 'Python')
output_dir = os.path.join('output', 'Python')
result_dir = os.path.join(output_dir, 'result')
top10_dir = os.path.join(result_dir, 'top10')
top20_dir = os.path.join(result_dir, 'top20')
top30_dir = os.path.join(result_dir, 'top30')

top30 = get_top30(os.path.join(data_dir, 'top30-award.txt'))
all_users = get_all_users(os.path.join(output_dir, 'all_users.txt'))
all_repos = get_all_repos(os.path.join(output_dir, 'all_repos.txt'))

user2idx = {user: i for i, user in enumerate(all_users)}
repo2idx = {repo: i for i, repo in enumerate(all_repos)}
idx2user = {i: user for i, user in enumerate(all_users)}
user_info = json.load(open(os.path.join(output_dir, 'users_info.json'), 'r'))
repo_info = json.load(open(os.path.join(output_dir, 'repos_info.json'), 'r'))


def save_owned_result(user_list, path):
    with open(path, 'w') as outfile:
        owned = [len(user_info[user]["owned_repos"]) for user in user_list]
        rank = rank_of_list(owned)
        for i in range(len(user_list)):
            outfile.write(",".join([user_list[i], str(owned[i]), str(rank[i])]) + "\n")
    print("Successfully saved file: {}".format(path))


def save_written_result(user_list, path):
    with open(path, 'w') as outfile:
        written = [len(user_info[user]["written_repos"]) for user in user_list]
        rank = rank_of_list(written)
        for i in range(len(user_list)):
            outfile.write(",".join([user_list[i], str(written[i]), str(rank[i])]) + "\n")
    print("Successfully saved file: {}".format(path))


def save_contribution_result(user_list, path):
    with open(path, 'w') as outfile:
        contribution_scores = compute_contribution(output_dir, all_users)
        contributions = [contribution_scores[user] for user in user_list]
        rank = rank_of_list(contributions)
        for i in range(len(user_list)):
            outfile.write(",".join([user_list[i], str(contributions[i]), str(rank[i])]) + "\n")
    print("Successfully saved file: {}".format(path))


def save_fm_result(user_list, path):
    with open(path, 'w') as outfile:
        fm_scores = compute_fm_score(output_dir, all_users, idx2user)
        fm = [fm_scores[user] for user in user_list]
        rank = rank_of_list(fm)
        for i in range(len(user_list)):
            outfile.write(",".join([user_list[i], str(fm[i]), str(rank[i])]) + "\n")
    print("Successfully saved file: {}".format(path))


def save_w_fm_result(user_list, path):
    with open(path, 'w') as outfile:
        fm_scores = compute_w_fm_score(output_dir, all_users, idx2user)
        fm = [fm_scores[user] for user in user_list]
        rank = rank_of_list(fm)
        for i in range(len(user_list)):
            outfile.write(",".join([user_list[i], str(fm[i]), str(rank[i])]) + "\n")
    print("Successfully saved file: {}".format(path))


def load_result(path):
    ranks = []
    with open(path, 'r') as infile:
        for line in infile:
            words = line.rstrip().split(",")
            ranks.append(int(words[2]))
    return ranks


if __name__ == "__main__":

    # preprocess data for FM
    # save_neighbors(output_dir, all_users, repo_info)
    # save_related_repos(output_dir, all_users, user_info)
    # create_fm_train_data(output_dir, all_users, all_repos, user2idx, repo2idx, repo_info)
    # create_fm_test_data(output_dir, all_users, user2idx, repo2idx)

    # save top30 results
    # save_owned_result(top30, os.path.join(top30_dir, 'result_owned.txt'))
    # save_written_result(top30, os.path.join(top30_dir, 'result_written.txt'))
    # save_contribution_result(top30, os.path.join(top30_dir, 'result_commit.txt'))
    # save_fm_result(top30, os.path.join(top30_dir, 'result_wo_fm.txt'))
    # save_w_fm_result(top30, os.path.join(top30_dir, 'result_w_fm.txt'))

    # save top20 results
    # top20 = top30[:20]
    # save_owned_result(top20, os.path.join(top20_dir, 'result_owned.txt'))
    # save_written_result(top20, os.path.join(top20_dir, 'result_written.txt'))
    # save_contribution_result(top20, os.path.join(top20_dir, 'result_commit.txt'))
    # save_fm_result(top20, os.path.join(top20_dir, 'result_wo_fm.txt'))
    # save_w_fm_result(top20, os.path.join(top20_dir, 'result_w_fm.txt'))

    # save top10 results
    # top10 = top30[:10]
    # save_owned_result(top10, os.path.join(top10_dir, 'result_owned.txt'))
    # save_written_result(top10, os.path.join(top10_dir, 'result_written.txt'))
    # save_contribution_result(top10, os.path.join(top10_dir, 'result_commit.txt'))
    # save_fm_result(top10, os.path.join(top10_dir, 'result_wo_fm.txt'))
    # save_w_fm_result(top10, os.path.join(top10_dir, 'result_w_fm.txt'))

    # get relevance score
    relevance_scores = get_relevance(os.path.join(data_dir, "top30-award.txt"))
    sorted_relevance = [None for i in range(30)]

    # show the results
    file_names = ["result_owned.txt", "result_written.txt", "result_commit.txt",
                  "result_pageRank.txt", "result_WpageRank.txt", "result_wo_fm.txt", "result_w_fm.txt"]
    result_types = ["Owned", "Written", "Commits", "PageRank(binary)", "PageRank(weighted)", "FM wo", "FM w"]
    dirs = [top10_dir, top20_dir, top30_dir]
    dir_names = ["top 10", "top 20", "top 30"]
    correct_ranks = [list(range(1, 11)), list(range(1, 21)), list(range(1, 31))]
    for dir, dir_name, correct_rank in zip(dirs, dir_names, correct_ranks):
        print("\nThe result for {} users...".format(dir_name))
        length = len(correct_rank)
        for result_type, file_name in zip(result_types, file_names):
            rank = load_result(os.path.join(dir, file_name))
            rho, _ = spearmanr(correct_rank, rank)
            tau, _ = kendalltau(correct_rank, rank)

            # compute ndcg
            for i, user in enumerate(top30[:length]):
                sorted_relevance[rank[i] - 1] = relevance_scores[user]
            relevance = sorted_relevance[:length]
            ndcg = compute_ndcg(relevance, num=length)
            print("{}: Spearman's rho: {}, Kendall's tau: {}, ndcg: {}".format(result_type, rho, tau, ndcg))
