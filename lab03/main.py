import random
import matplotlib.pyplot as plt
from network import Network

random.seed(10)


def create_figure(size, title):
    figure = plt.figure(figsize=size)
    res = figure.gca()
    res.set_title(title)
    return res


if __name__ == '__main__':
    n_nodes, n_files = 1000, 10000
    network = Network(n_nodes, n_files)
    axes = create_figure((6, 6), '')
    network.visualize(axes)
    plt.subplots_adjust(top=0.975, bottom=0.075, right=0.975, left=0.075)

    plt.show()

    degrees_distrib = network.get_vertices_degree_distribution()
    axes = create_figure((5, 5), 'Распределение степеней вершин')
    axes.bar(degrees_distrib.keys(), degrees_distrib.values())

    mean = 0
    quantity = 0
    for degree, n_degrees in degrees_distrib.items():
        mean += degree * n_degrees
        quantity += n_degrees
    mean /= quantity
    print(f'Среднее количество соседей: {mean}')
    print(f'Минимальное количество соседей: {min(degrees_distrib.keys())}')
    print(f'Максимальное количество соседей: {max(degrees_distrib.keys())}')
    print()

    files_distrib = network.get_files_distribution()
    axes = create_figure((5, 5), 'Распределение количества хранимых файлов')
    axes.bar(files_distrib.keys(), files_distrib.values())

    plt.show()

    print('Длина кратчайшего пути\tСреднее количество рёбер\tМинимальное количество рёбер\tМаксимальное количество рёбер')
    statistics = network.calculate_statistics()
    for short_len, dist in sorted(statistics.items()):
        mean = 0
        quantity = 0
        for path_len, n_paths in dist.items():
            mean += path_len * n_paths
            quantity += n_paths
        mean /= quantity
        print(f'{short_len}\t{mean:.2f}\t{min(dist.keys())}\t{max(dist.keys())}')

    path_lengths = [5, 10, 15]
    for path_length in path_lengths:
        axes = create_figure((6, 6), f'{path_length} хопов')
        network.visualize(axes)
        shortest_paths = network[random.randint(0, n_nodes - 1)].find_paths(path_length)
        shortest_path = list(filter(lambda x: len(x[-1].files) != 0, shortest_paths))[0]
        start_node = shortest_path[0]
        end_pont = shortest_path[-1]
        for node in shortest_path[1:-1]:
            node.draw(axes, 'b', '#60a7b9')
        start_node.draw(axes, 'b', 'g')
        end_pont.draw(axes, 'b', '#d27d7d')

        files = end_pont.files
        i_file = random.randint(0, len(files) - 1)
        file_name = list(files.keys())[i_file]
        file_value = list(files.values())[i_file]
        found_file, path = start_node.download(file_name)
        if found_file != file_value:
            raise Exception()
        for node in path:
            node.draw(axes, 'r')
        plt.subplots_adjust(top=0.925, bottom=0.075, right=0.925, left=0.075)

    plt.show()
