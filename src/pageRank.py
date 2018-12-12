import sys
import numpy as np
import json

class PageRank():
    def __init__(self, input_filename):
        graph = {}
        self.node_dic = {}
        self.trans_matrix = None

        graph, self.node_dic = self.build_graph(input_filename)
        #print(node_dic)
        #with open('node_dic.json', 'w') as outfile:
        #    json.dump(node_dic, outfile, indent=4)
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
    rand_jump_prob = 0.2
    graph_path = 'output/user_graph'
    top30users = 'data/top30-award.txt'
    result_path = 'output/result_pageRank.tsv'

    pageRank = PageRank(graph_path)
    user_dic = pageRank.node_dic
    probs = pageRank.run(rand_jump_prob)
    rank = np.argsort(probs)


    user_name = []
    user_rank = []
    with open(top30users, 'r') as infile, open(result_path, 'w') as outfile:
        outfile.write('user\tprobability\tpredict_rank\n')
        for idx, line in enumerate(infile):
            user_name.append(line.strip().split(', ')[0])
            user_rank.append(rank[user_dic[user_name[idx]]])
        user_rank = np.argsort(user_rank)
        print(user_rank)
        for idx, name in enumerate(user_name):
            try:
                outfile.write(f'{name}\t{probs[user_dic[name]]:.4f}\t{user_rank[idx]+1}\n')
            except Exception as e:
                print('Exception:', e)

