import networkx as nx
import matplotlib.pyplot as plt

def read_dimacs_graph(file_path):
    '''
        Parse .col file and return graph object
    '''
    vertices = set()
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
                vertices.add(v1)
                vertices.add(v2)
                edges.append((v1, v2))
            else:
                continue
        graph = nx.Graph()
        graph.add_nodes_from(vertices)
        graph.add_edges_from(edges)
        print(graph.number_of_edges(), graph.number_of_nodes())
        return graph


def main():
    read_dimacs_graph('sample_graphs\dsjc250.5.col')

if __name__ == '__main__':
    main()
