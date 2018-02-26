'''
Generates a graph from the co-commit adjacency matrix provided. The matrix is weighted and undirected
'''
import os
import sys
import csv
import community
import cPickle as pickle
import networkx as nx
import pandas as pd

csv.field_size_limit(sys.maxsize)
adj_pickle_dir = sys.argv[1]
output_graph_path = sys.argv[2]
output_csv_path = sys.argv[3]
title_row = ['file_name', 'degree', 'modularity_class', 'modularity_measure']

#Read the adjacency matrix and create code graph as well as partioning
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

