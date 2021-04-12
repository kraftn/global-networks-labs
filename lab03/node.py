import random
import math
from hashlib import sha1, sha224
import matplotlib.patches as patches


def distance(point1, point2):
    diff_x = abs(point2[0] - point1[0])
    diff_y = abs(point2[1] - point1[1])
    res = min(diff_x, 1 - diff_x) ** 2 + min(diff_y, 1 - diff_y) ** 2
    return res ** 0.5


def are_neighbors(obj, other):
    top_bottom_dist = distance((0, obj.top), (0, other.bottom))
    bottom_top_dist = distance((0, obj.bottom), (0, other.top))
    part1 = math.isclose(top_bottom_dist, 0) or math.isclose(bottom_top_dist, 0)
    part1 = part1 and (obj.left < other.right) and (obj.right > other.left)

    left_right_dist = distance((obj.left, 0), (other.right, 0))
    right_left_dist = distance((obj.right, 0), (other.left, 0))
    part2 = math.isclose(left_right_dist, 0) or math.isclose(right_left_dist, 0)
    part2 = part2 and (obj.top > other.bottom) and (obj.bottom < other.top)

    return part1 or part2


def convert_file_to_point(file_key):
    file_key = file_key.encode()
    x = int.from_bytes(sha1(file_key).digest(), 'big') / 2 ** 160
    y = int.from_bytes(sha224(file_key).digest(), 'big') / 2 ** 224
    return x, y


class Node:
    def __init__(self, source_node):
        if source_node is not None:
            x = random.random()
            y = random.random()

            path = source_node.route((x, y))
            self.left, self.bottom, self.right, self.top, self.neighbors, self.files = path[-1]._split(self)
            self._update_neighbors()

        else:
            self.left = 0
            self.bottom = 0
            self.right = 1
            self.top = 1
            self.neighbors = set()
            self.files = dict()

    def contains(self, point):
        condition = self.left <= point[0] < self.right
        condition = condition and (self.bottom <= point[1] < self.top)
        return condition

    def route(self, point):
        if self.contains(point):
            return [self]

        curr_node = self
        visited_nodes = []

        while curr_node is not None:
            visited_nodes.append(curr_node)

            neighbors = curr_node.neighbors
            min_neighbor = None
            min_dist = 2 ** 0.5
            for curr_neighbor in neighbors:
                if curr_neighbor.contains(point):
                    visited_nodes.append(curr_neighbor)
                    return visited_nodes

                center = curr_neighbor.calc_center()
                dist = distance(center, point)
                if (dist < min_dist) and (curr_neighbor not in visited_nodes):
                    min_dist = dist
                    min_neighbor = curr_neighbor

            curr_node = min_neighbor

    def calc_center(self):
        return (self.left + self.right) / 2, (self.bottom + self.top) / 2

    def upload(self, file_key, file_value):
        point = convert_file_to_point(file_key)
        path = self.route(point)
        path[-1].files[file_key] = file_value

    def download(self, file_key):
        point = convert_file_to_point(file_key)
        path = self.route(point)
        return path[-1].files[file_key], path

    def draw(self, axes, edge_color, face_color='none'):
        rect = patches.Rectangle((self.left, self.bottom), self.right - self.left, self.top - self.bottom,
                                 edgecolor=edge_color, facecolor=face_color)
        axes.add_patch(rect)

    def find_paths(self, path_length):
        return self._bfs(lambda x: len(x) == path_length + 1)

    def find_path_to_node(self, node):
        return self._bfs(lambda x: x[-1] == node)[0]

    def _bfs(self, stop_criterion):
        visited = {self}
        queue = [[self]]
        while (len(queue) != 0) and not stop_criterion(queue[0]):
            path = queue.pop(0)
            for neighbor in path[-1].neighbors:
                if neighbor not in visited:
                    new_path = path.copy()
                    new_path.append(neighbor)
                    queue.append(new_path)
                    visited.add(neighbor)
        return queue

    def _split(self, new_neighbor):
        width = self.right - self.left
        height = self.top - self.bottom
        if width >= height:
            old_right = self.right
            self.right -= width / 2
            ret_left = self.right
            ret_top = self.top
            ret_right = old_right
            ret_bottom = self.bottom
        else:
            old_top = self.top
            self.top -= height / 2
            ret_left = self.left
            ret_top = old_top
            ret_right = self.right
            ret_bottom = self.top

        ret_neighbors = self.neighbors.copy()
        ret_neighbors.add(self)
        self._update_neighbors()
        self.neighbors.add(new_neighbor)

        ret_files = dict()
        files_to_delete = []
        for key, value in self.files.items():
            if not self.contains(convert_file_to_point(key)):
                ret_files[key] = value
                files_to_delete.append(key)

        for key in files_to_delete:
            self.files.pop(key)

        return ret_left, ret_bottom, ret_right, ret_top, ret_neighbors, ret_files

    def _update_neighbors(self):
        old_neighbors = self.neighbors
        self.neighbors = set(filter(lambda x: are_neighbors(self, x), self.neighbors))
        to_delete = old_neighbors.difference(self.neighbors)
        for node in to_delete:
            node.neighbors.discard(self)
        for node in self.neighbors:
            node.neighbors.add(self)

    def __repr__(self):
        return self.calc_center().__repr__()
