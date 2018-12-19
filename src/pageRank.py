import sys
import os
import numpy as np

class PageRank():
    def __init__(self, input_filename, weighted=False):
        self.weighted = weighted
        graph = {}
        self.node_dic = {}
        self.trans_matrix = None

        graph, self.node_dic = self.build_graph(input_filename)
        N = len(self.node_dic)
        print('Total # of users in graph', N)
        self.trans_matrix = self.build_transMatrix(graph)

    def build_graph(self, input_filename):
        node_dic = {}
        graph = {}
        with open(input_filename, 'r') as infile:
            for line in infile:
                start, end = line.strip().split(',')
                if start not in node_dic:
                    node_dic[start] = len(node_dic)
                    graph[node_dic[start]] = []
                if end not in node_dic:
                    node_dic[end] = len(node_dic)
                    graph[node_dic[end]] = []
                graph[node_dic[start]].append(node_dic[end])
        return graph, node_dic

    def build_transMatrix(self, graph):
        N = len(self.node_dic)
        trans_matrix = np.zeros((N, N))
        for start, ends in graph.items():
            for end in ends:
                if self.weighted:
                    trans_matrix[start][end] += 1
                else:
                    trans_matrix[start][end] = 1
        trans_matrix /= np.sum(trans_matrix, axis=1)[:, np.newaxis]

        # Solve zero-outlink problem (if all elements in a row is zero, assign 1/N to all nodes)
        for row in trans_matrix:
            if sum(row) == 0:
                trans_matrix[row:] = 1/N
        return trans_matrix

    def run(self, rand_jump_prob):
        """ Return probabilities: type=np.array
        """
        N = len(self.node_dic)
        equal_matrix = np.ones((N, N)) / N
        prob = np.ones(N).T/N
        for i in range(10000):
            prob = (1-rand_jump_prob) * prob.dot(self.trans_matrix) + rand_jump_prob * prob.dot(equal_matrix)
        return prob
    
if __name__ == '__main__':
    graph_path = 'output/user_graph'
    top30_path = 'data/top30-award.txt'
    weighted_graph = True

    # Get top 30 users
    users = []
    with open(top30_path, 'r') as infile:
        users = [line.strip().split(',')[0] for line in infile]

    # Run PageRank
    pageRank = PageRank(graph_path, weighted_graph)
    user_dic = pageRank.node_dic
    probs = pageRank.run(rand_jump_prob)

    for i in range(1, 4):
        rand_jump_prob = 0.85
        k = 10 * i
        topK_users = users[:k]
        rank = np.argsort(probs)
        user_rank_abs = [rank[user_dic[user]] for user in topK_users]
        user_rank_rel = np.argsort(user_rank_abs)

        if weighted_graph:
            result_path = f'output/result/top{k}/result_WpageRank.txt'
        else:
            result_path = f'output/result/top{k}/result_pageRank.txt'

        print('Write to', result_path) 
        with open(result_path, 'w') as outfile:
            for idx, user in enumerate(topK_users):
                try:
                    outfile.write(f'{user},{probs[user_dic[user]]},{user_rank_rel[idx]+1}\n')
                except Exception as e:
                    print('Exception:', e)

