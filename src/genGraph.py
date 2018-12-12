"""
Output graph file: entity1, entity2
"""
import json

def pairwise(contributors):
    pair_list = []
    for i in range(len(contributors)-2):
        for j in range(i+1, len(contributors)-1):
            pair_list.append(contributors[i] + ',' + contributors[j])
            pair_list.append(contributors[j] + ',' + contributors[i])
    return pair_list

if __name__ == "__main__":
    input_filename = 'output/repos_info.json'
    output_filename = 'output/user_graph'

    with open(input_filename, 'r') as infile:
        data = json.load(infile)

    with open(output_filename, 'w') as outfile:
        for repo, repo_info in data.items():
            if len(repo_info["contributors"]) == 2:
                users = list(repo_info["contributors"].keys())
                outfile.write(users[0] + ',' + users[1] + '\n')
                outfile.write(users[1] + ',' + users[0] + '\n')
            elif len(repo_info["contributors"]) > 2:
                pairs = pairwise(list(repo_info["contributors"].keys()))
                outfile.write('\n'.join(pairs))
                outfile.write('\n')


