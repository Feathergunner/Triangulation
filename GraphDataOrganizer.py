#!usr/bin/python
# -*- coding: utf-8 -*-

import global_settings as gs

import run_time_eval as rte
import GraphConstructionAlgorithms as gca

import networkx as nx
import re
import os
import json

def check_filepath(filepath, fileending="json"):
	'''
	Checks if a filepath exists

	Args:
		path: a filename or path

	Return:
		[dir, filename] : directory and filename as constructed from path
	'''
	path_components = re.split(r'/', filepath)
	path = ""
	for directory in path_components[:-1]:
		path += directory+"/"
		if not os.path.isdir(path):
			os.mkdir(path)

	if len(path_components) > 1:
		filename = path_components[-1]

	if not "."+fileending in filename:
		filename += "."+fileending

	return [path, filename]


def write_graphs_to_json(list_of_graphs, filename):
	'''
	Stores a set of graphs in a json file.

	Args:
		list_of_graphs : a list of graphs in networkx-format.
		filename : the name of the target file.
	'''

	[path, filename] = check_filepath(filename)

	data = []
	for g in list_of_graphs:
		data.append([[n for n in g.nodes()], [e for e in g.edges()]])
		
	with open(path+filename, 'w') as jsonfile:
		json.dump(data, jsonfile)

def load_graphs_from_json(filename):
	'''
	Loads a list of graphs from a json file.

	Args:
		filename : the name of the file that holds the data.

	Return:
		list_of_graphs : a list of graphs that were loaded from the file.
	'''
		
	[path, filename] = check_filepath(filename)

	if not os.path.isdir(path):
		## TO DO: raise error
		return

	if not ".json" in filename:
		filename += ".json"

	with open(path+filename) as jsonfile:
		data = json.load(jsonfile)

	list_of_graphs = []
	for g_data in data:
		new_graph = nx.Graph()
		new_graph.add_nodes_from(g_data[0])
		new_graph.add_edges_from(g_data[1])
		list_of_graphs.append(new_graph)

	return list_of_graphs

def construct_set_random_graphs(number_of_graphs, n, p):
	gg = gca.GraphGenerator()
	graphs = []
	for i in range(number_of_graphs):
		graphs.append(gg.construct_conneted_er(n, p))

	filename = "data/eval/random/graphs_"+str(n)+"_"+str(p).replace('.','')
	write_graphs_to_json(graphs, filename)

def construct_full_set_random_graphs():
	for n in gs.RANDOM_GRAPH_SETTINGS["n"]:
		for p in gs.RANDOM_GRAPH_SETTINGS["p"]:
			construct_set_random_graphs(100, n, p)