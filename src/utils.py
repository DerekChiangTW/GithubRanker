#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

data_dir = os.path.join('..', 'data')


def get_groundTruth(file_name):
    file_path = os.path.join(data_dir, file_name)
    gt = {}
    with open(file_path, 'r') as file:
        for line in file:
            pair = line.rstrip().split(", ")
            gt[pair[0]] = int(pair[1])
    return gt


if __name__ == "__main__":
    gt = get_groundTruth("top30-award.txt")
    for person, star in gt.items():
        print(person, star)
