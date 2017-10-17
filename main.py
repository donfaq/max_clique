'''
Find maxumum clique in given dimacs-format graph
based on:
http://www.m-hikari.com/ams/ams-2014/ams-1-4-2014/mamatAMS1-4-2014-3.pdf
'''
import networkx as nx
import matplotlib.pyplot as plt
import sys


def read_dimacs_graph(file_path):
    '''
        Parse .col file and return graph object
    '''
    edges = []
    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith('c'):  # graph description
                print(*line.split()[1:])
            # first line: p name num_of_vertices num_of_edges
            elif line.startswith('p'):
                p, name, vertices_num, edges_num = line.split()
                vertices_num = int(vertices_num)
                edges_num = int(edges_num)
                print('{0} {1} {2}'.format(name, vertices_num, edges_num))
            elif line.startswith('e'):
                _, v1, v2 = line.split()
                edges.append((v1, v2))
            else:
                continue
        return nx.Graph(edges)


def arguments():
    import argparse
    parser = argparse.ArgumentParser(
        description='Compute maximum clique for a graph')
    parser.add_argument('--path', type=str, required=True,
                        help='Path to dimacs-format graph file')
    parser.add_argument('--draw', type=bool, default=False, required=False)
    return parser.parse_args()


def clique(graph):
    from networkx.algorithms.clique import find_cliques_recursive
    return find_cliques_recursive(graph)


def lengths(x):
    if isinstance(x, list):
        yield len(x)
        for y in x:
            yield from lengths(y)


def bronk(graph, P, R=set(), X=set()):
    '''
    Implementation of Bron–Kerbosch algorithm for finding all maximal cliques in graph
    '''
    if not any((P, X)):
        yield R
    for node in P.copy():
        for r in bronk(graph, P.intersection(graph.neighbors(node)),
                       R=R.union(node), X=X.intersection(graph.neighbors(node))):
            yield r
        P.remove(node)
        X.add(node)


def greedy_clique_heuristic(graph):
    '''
    Greedy search for clique iterating by nodes 
    with highest degree and filter only neighbors 
    '''
    K = set()
    nodes = [node[0] for node in sorted(nx.degree(graph),
                                        key=lambda x: x[1], reverse=True)]
    while len(nodes) != 0:
        neigh = list(graph.neighbors(nodes[0]))
        K.add(nodes[0])
        nodes.remove(nodes[0])
        nodes = list(filter(lambda x: x in neigh, nodes))
    return K


def greedy_coloring_heuristic(graph):
    '''
    Greedy graph coloring heuristic with degree order rule
    '''
    color_num = iter(range(0, len(graph)))
    color_map = {}
    used_colors = set()
    nodes = [node[0] for node in sorted(nx.degree(graph),
                                        key=lambda x: x[1], reverse=True)]
    color_map[nodes.pop(0)] = next(color_num)  # color node with color code
    used_colors = {i for i in color_map.values()}
    while len(nodes) != 0:
        node = nodes.pop(0)
        neighbors_colors = {color_map[neighbor] for neighbor in
                      list(filter(lambda x: x in color_map, graph.neighbors(node)))}
        if len(neighbors_colors) == len(used_colors):
            color = next(color_num)
            used_colors.add(color)
            color_map[node] = color
        else:
            color_map[node] = next(iter(used_colors - neighbors_colors))
    return used_colors


def main():
    args = arguments()
    graph = read_dimacs_graph(args.path)

    lower_bound = len(greedy_clique_heuristic(graph))
    print('heuristic max clique size', lower_bound)
    upper_bound = len(greedy_coloring_heuristic(graph))
    print('heuristic chromatic number', upper_bound)

    # print('Maximum cliques:', [i for i in bronk(graph, set(graph.nodes))])
    # print('NetworkX algorithm: ', max(lengths([c for c in clique(graph)])))
    if args.draw:
        nx.draw_networkx(graph)
        plt.savefig('temp.png')


if __name__ == '__main__':
    main()
