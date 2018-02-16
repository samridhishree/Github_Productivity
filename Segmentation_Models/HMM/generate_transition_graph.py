'''
Generates the transition graph for a trained HMM model.
Creates a graphviz layout for the graph.
'''

import os
import sys
import csv
import joblib
import pandas as pd
import networkx as nx
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--model_file', help='The trained model whose transition graph is to be generated')
parser.add_argument('--output_dir', help='Output directory for the transition graphs')
parser.add_argument('--nstates', help='Number of states in the trained model file')
args, unknown = parser.parse_known_args()

model_file = args.model_file
output_dir = args.output_dir
nstates = int(args.nstates) 

# Returns a dictionary of edge pairs with the transition probability as the weights
def GetMarkovEdges(trans_mat, nstates):
    edges = {}
    for row in range(nstates):
        for col in range(nstates):
            edges[(row, col)] = trans_mat[row][col]
    return edges

# Load the model
model = joblib.load(model_file)
states = range(nstates)

# Get the edge weights from the transition matrix
edge_wts = GetMarkovEdges(model.transmat_, nstates)

# create graph object
G = nx.MultiDiGraph()

# nodes correspond to states
G.add_nodes_from(states)

# Add edges to the graph
for k, v in edge_wts.items():
    tmp_origin, tmp_destination = k[0], k[1]
    G.add_edge(tmp_origin, tmp_destination, weight=v, label=v)

# Get the dot graph directory with respect to graphviz layout and save the dot file
out_file = 'transition_prob_' + str(nstates) + '_states.dot'
pos = nx.drawing.nx_pydot.graphviz_layout(G, prog='dot')
nx.draw_networkx(G, pos)
nx.drawing.nx_pydot.write_dot(G, os.path.join(output_dir, out_file))







