import networkx as nx


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


def main():
    args = arguments()
    graph = read_dimacs_graph(args.path)
    print('Maximum cliques:', [i for i in bronk(graph, set(graph.nodes))])


if __name__ == '__main__':
    main()
