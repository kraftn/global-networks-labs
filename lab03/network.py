import random
from collections import Counter
from node import Node


class Network:
    def __init__(self, n_nodes, n_files):
        nodes = [Node(None)]
        for i_file in range(n_files):
            nodes[0].upload(f'File {i_file + 1}', f'Text of the file {i_file + 1}')
        for i_node in range(n_nodes - 1):
            nodes.append(Node(nodes[0]))
        self.nodes = nodes

    def __getitem__(self, item):
        return self.nodes[item]

    def visualize(self, axes):
        for node in self.nodes:
            node.draw(axes, 'b')

    def get_vertices_degree_distribution(self):
        statistics = Counter()
        for node in self.nodes:
            statistics[len(node.neighbors)] += 1
        return statistics

    def get_files_distribution(self):
        statistics = Counter()
        for node in self.nodes:
            statistics[len(node.files)] += 1
        return statistics

    def calculate_statistics(self):
        n_nodes = len(self.nodes)
        counter = dict()
        for start_node in self.nodes:
            end_points = list(filter(lambda x: x != start_node, self.nodes))
            end_point = end_points[random.randint(0, n_nodes - 2)]
            shortest_path = start_node.find_path_to_node(end_point)
            shortest_len = len(shortest_path) - 1
            point_x = end_point.left + random.random() * (end_point.right - end_point.left)
            point_y = end_point.bottom + random.random() * (end_point.top - end_point.bottom)
            algo_path = start_node.route((point_x, point_y))
            algo_len = len(algo_path) - 1
            if shortest_len not in counter.keys():
                counter[shortest_len] = dict()
            if algo_len not in counter[shortest_len].keys():
                counter[shortest_len][algo_len] = 0
            counter[shortest_len][algo_len] += 1
        return counter
