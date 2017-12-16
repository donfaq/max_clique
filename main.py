#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Find maxumum clique in given dimacs-format graph
based on:
http://www.m-hikari.com/ams/ams-2014/ams-1-4-2014/mamatAMS1-4-2014-3.pdf
'''
import os
import sys
import threading
from contextlib import contextmanager
import _thread
import time
import networkx as nx


class TimeoutException(Exception):
    pass


@contextmanager
def time_limit(seconds):
    timer = threading.Timer(seconds, lambda: _thread.interrupt_main())
    timer.start()
    try:
        yield
    except KeyboardInterrupt:
        raise TimeoutException()
    finally:
        timer.cancel()


def timing(f):
    '''
    Measures time of function execution
    '''
    def wrap(*args):
        time1 = time.time()
        ret = f(*args)
        time2 = time.time()
        print('\n{0} function took {1:.3f} ms'.format(
            f.__name__, (time2 - time1) * 1000.0))
        return (ret, '{0:.3f} ms'.format((time2 - time1) * 1000.0))
    return wrap


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
    parser.add_argument('--time', type=int, default=60,
                        help='Time limit in seconds')
    parser.add_argument('--test', type=str, default=None, required=False)
    return parser.parse_args()


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
    return len(used_colors)


def branching(graph, cur_max_clique_len):
    '''
    Branching procedure
    '''
    g1, g2 = graph.copy(), graph.copy()
    max_node_degree = len(graph) - 1
    nodes_by_degree = [node for node in sorted(nx.degree(graph),  # All graph nodes sorted by degree (node, degree)
                                               key=lambda x: x[1], reverse=True)]
    # Nodes with (current clique size < degree < max possible degree)
    partial_connected_nodes = list(filter(
        lambda x: x[1] != max_node_degree and x[1] <= max_node_degree, nodes_by_degree))
    # graph without partial connected node with highest degree
    g1.remove_node(partial_connected_nodes[0][0])
    # graph without nodes which is not connected with partial connected node with highest degree
    g2.remove_nodes_from(
        graph.nodes() -
        graph.neighbors(
            partial_connected_nodes[0][0]) - {partial_connected_nodes[0][0]}
    )
    return g1, g2


def bb_maximum_clique(graph):
    max_clique = greedy_clique_heuristic(graph)
    chromatic_number = greedy_coloring_heuristic(graph)
    if len(max_clique) == chromatic_number:
        return max_clique
    else:
        g1, g2 = branching(graph, len(max_clique))
        return max(bb_maximum_clique(g1), bb_maximum_clique(g2), key=lambda x: len(x))


@timing
def get_max_clique(graph):
    return bb_maximum_clique(graph)


def get_files_size_ordered(dirpath):
    return sorted((os.path.join(basedir, filename)
                   for basedir, dirs, files in os.walk(dirpath) for filename in files),
                  key=os.path.getsize)


def run_test(args):
    import pandas as pd
    test_results = pd.DataFrame(
        columns=['filename', 'nodes', 'edges', 'clique', 'clique length', 'time'])
    files = get_files_size_ordered(args.test)
    try:
        for f in files:
            graph = read_dimacs_graph(f)
            try:
                with time_limit(args.time):
                    max_clq = get_max_clique(graph)
                    test_results = test_results.append({'filename': f, 'nodes': graph.number_of_nodes(),
                                                        'edges': graph.number_of_edges(), 'clique': str(max_clq[0]),
                                                        'clique length': len(max_clq[0]), 'time': max_clq[1]},
                                                       ignore_index=True)
                    test_results.to_excel('test_results.xlsx')
            except TimeoutException:
                test_results = test_results.append({'filename': f, 'nodes': graph.number_of_nodes(),
                                                    'edges': graph.number_of_edges(), 'clique': 0,
                                                    'clique length': 0, 'time': 'TIMEOUT'},
                                                   ignore_index=True)
    finally:
        test_results.to_excel('test_results.xlsx')


def main():
    args = arguments()

    if args.test:
        run_test(args)
    else:
        graph = read_dimacs_graph(args.path)
        try:
            with time_limit(args.time):
                max_clq = get_max_clique(graph)
                print('\nMaximum clique', max_clq, '\nlen:', len(max_clq))
        except TimeoutException:
            print("Timed out!")
            sys.exit(0)


if __name__ == '__main__':
    main()
