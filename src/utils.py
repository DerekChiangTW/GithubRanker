#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

input_dir = os.path.join('..', 'data')


def get_groundTruth(input_path):
    gt = {}
    with open(input_path, 'r') as infile:
        for line in infile:
            pair = line.rstrip().split(", ")
            gt[pair[0]] = int(pair[1])
    return gt


if __name__ == "__main__":
    input_path = os.path.join(input_dir, "top30-award.txt")
    gt = get_groundTruth(input_path)
    for person, star in gt.items():
        print(person, star)
