# -*- coding: utf-8 -*-
import argparse
import csv
import sys
import networkx as nx
from math import log
from nltk.util import bigrams
import community

def init():
    parser = argparse.ArgumentParser()
    parser.add_argument('--inFileCSV', dest='inFileCSV', 
                        type=str,
                        help='input file with UK first names in CSV',
                        required=True)
    parser.add_argument('--minFreq', dest='minFreq', 
                        type=int, default=10,
                        help='minimum frequency required for a name to be read')
    parser.add_argument('--simThreshold', dest='simThreshold', 
                        type=float, default=0.2,
                        help='minimum inter-name similarity for a link to be created')
    parser.add_argument('--degreeThreshold', dest='degreeThreshold', 
                        type=float, default=1.0,
                        help='minimum degree required for a node to be included in the output graph')
    parser.add_argument('--rankThreshold', dest='rankThreshold', 
                        type=int, default=100,
                        help='all nodes below this rank are guaranteed to be included in the output graph')
    parser.add_argument('--bonusMultiplier', dest='bonusMultiplier', 
                        type=float, default=1.2,
                        help='the edge weights of the nodes below rankThreshold get multiplied with this bonus to increase their chances of survival')
    parser.add_argument('--outFileGraphML', dest='outFileGraphML', 
                        type=str,
                        help='output file with Belgian first names in GraphML format',
                        required=True)
    global args
    args = vars(parser.parse_args())
    print(args, file=sys.stderr)

def read_file(filename):
    
    global G
    G = nx.Graph()

    with open(filename, 'r') as csvfile:

        reader = csv.DictReader(csvfile, delimiter=',')
        for row in reader:

            name = row['name']
            freq = int(row['n'])
            rank = int(row['rank'])

            if freq < args['minFreq']:
                continue

            # Give importance to first letter
            charBigrams = bigrams('_%s' % name)

            if not G.has_node(name):
                G.add_node(name, kind='firstname', freq=freq, ranks=[rank])
            else:
                G.node[name]['freq'] += freq
                G.node[name]['ranks'].append(rank)
                
            for cb in charBigrams:
                if not G.has_node(cb):
                    G.add_node(cb, kind='charbigram')
                if not G.has_edge(name, cb):
                    G.add_edge(name,cb)

    for node in list(G):
        if G.node[node]['kind'] == 'firstname':
            G.node[node]['size'] = int(log(G.node[node]['freq']))*2
            G.node[node]['rank'] = sum(G.node[node]['ranks'])/len(G.node[node]['ranks'])
            del G.node[node]['ranks']

    print("Graph G has %d nodes and %d edges... " % (nx.number_of_nodes(G), nx.number_of_edges(G)),file=sys.stderr)


def project_network():
    global nameNetwork
    nameNetwork = nx.bipartite.overlap_weighted_projected_graph(G, [x for x,y in G.nodes(data=True) if y['kind']=='firstname'], jaccard=True)

    # Delete all edges that do not make the threshold
    print("Deleting edges with too low weight in name network with %d nodes and %d edges... " % (nx.number_of_nodes(nameNetwork), nx.number_of_edges(nameNetwork)), file=sys.stderr)
    for u,v,a in list(nameNetwork.edges(data=True)):

        if int(G.node[u]['rank']) > args['rankThreshold'] or int(G.node[v]['rank']) > args['rankThreshold']:
            if a['weight'] * args['bonusMultiplier'] < args['simThreshold']:
                nameNetwork.remove_edge(u,v)
        else:
            if a['weight'] < args['simThreshold']:
                nameNetwork.remove_edge(u,v)
    print("done",file=sys.stderr)

    # Apply minimum degree
    print("Deleting nodes with too low degree in name network with %d nodes and %d edges... " % (nx.number_of_nodes(nameNetwork), nx.number_of_edges(nameNetwork)),file=sys.stderr)
    for node in list(nameNetwork):
        if nameNetwork.degree(node) < args['degreeThreshold']:
            if int(G.node[node]['rank']) > args['rankThreshold']:
                nameNetwork.remove_node(node)
            else:
                pass
#                print("rank = %d not > %s" % (nameNetwork.node[node]['rank'], args['rankThreshold']),file=sys.stderr)
        else:
            pass
#            print("degree = %d not < %s" % (nameNetwork.degree(node), args['degreeThreshold']),file=sys.stderr)

    print("done",file=sys.stderr)


    # Detect communities
    print("Partitioning name network with %d nodes and %d edges ... " % (nx.number_of_nodes(nameNetwork), nx.number_of_edges(nameNetwork)),file=sys.stderr)
    partition = community.best_partition(nameNetwork)
    print("done",file=sys.stderr)

    print("Deleting unneeded attributes ...",file=sys.stderr)
    for name in partition.keys():
        nameNetwork.node[name]['community'] = partition[name]
        nameNetwork.node[name]['label'] = name
        del nameNetwork.node[name]['kind']
        del nameNetwork.node[name]['freq']
        del nameNetwork.node[name]['rank']
    print("done",sys.stderr)

def write_network():
    print("Writing name network with %d nodes and %d edges ... " % (nx.number_of_nodes(nameNetwork), nx.number_of_edges(nameNetwork)),file=sys.stderr)
    nx.write_graphml(nameNetwork, args['outFileGraphML'], 'utf-8')
    print("done",file=sys.stderr)

if __name__ == '__main__':
    init()
    read_file(args['inFileCSV'])
    project_network()
    write_network()
