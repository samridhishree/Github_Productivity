'''
Generates a graph from the pairwise co-commit counts. The matrix is weighted and undirected.
It also partitions the graph to find clusters/modules of files that are highly interdependent on each other.

The partioning mehod: Fast unfolding of communities in large networks, Vincent D Blondel, Jean-Loup Guillaume, 
					Renaud Lambiotte, Renaud Lefebvre, Journal of Statistical Mechanics: Theory and Experiment 2008
Outputs:
[1] A gml file containing the co-commit graph
[2] A csv file per project containing graph metric - degree of each node (file); class that each node belongs to after partioning
'''
import os
import sys
import csv
import community
import cPickle as pickle
import networkx as nx
import pandas as pd
import argparse

csv.field_size_limit(sys.maxsize)

parser = argparse.ArgumentParser()
parser.add_argument('--adj_pickle_dir', help='Directory containing pickles list of file pair co-commit counts')
parser.add_argument('--output_graph_path', help='Output directory to store the gml graph files.')
parser.add_argument('--output_csv_path', help='Output directory to store graph metrics obtained by partioning the graph')
args, unknown = parser.parse_known_args()


adj_pickle_dir = args.adj_pickle_dir
output_graph_path =args.output_graph_path
output_csv_path = args.output_csv_path
title_row = ['file_name', 'degree', 'modularity_class', 'modularity_measure']

#Read the pairwise co-commits and create code graph as well as partioning
for fileName in os.listdir(adj_pickle_dir):
	if fileName.endswith('.pickle'):
		project_name = fileName.split('_co_commit.pickle')[0]
		output_file_name = project_name + '_code_graph_metrics.csv'
		output_file = os.path.join(output_csv_path, output_file_name)
		
		if os.path.isfile(output_file) == False:
			print "Processing file: ", fileName
			with open(os.path.join(adj_pickle_dir, fileName), "rb") as f:
				adj_dict = pickle.load(f)
				graph = nx.Graph()
				#For each pair-weight add an undirected edge to the graph
				for (s_node, t_node) in adj_dict:
					graph.add_edge(s_node, t_node, weight=adj_dict[(s_node, t_node)])

				print "Computing Metrics for the project: ", project_name
				project_name = fileName.split('_co_commit.pickle')[0]
				nodes = graph.nodes()
				degrees = graph.degree(nodes)
				if len(nodes) > 1:
					#Modularity partitioning and classes - dict of code files and module class
					print "Calculating partioning"
					partition = community.best_partition(graph)
					print "Calculating modularity measure"
					modularity = community.modularity(partition, graph)
					w = open(output_file, 'a')
					writer = csv.writer(w, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
					writer.writerow(title_row)
					print "Writing metric information to the file"
					for node in nodes:
						degree = degrees[node]
						module_class = partition[node]
						to_write = [node, degree, module_class, modularity]
						writer.writerow(to_write)
					w.close()

				#Convert to gml file
				output_f_name = fileName.split('_co_commit.pickle')[0] + '_co_commit.gml'
				graph_gml_file = os.path.join(output_graph_path, output_f_name)
				nx.write_gml(graph, graph_gml_file)

