#!usr/bin/python
# -*- coding: utf-8 -*-

import logging
import networkx as nx
import re
import os
import json

import meta
import global_settings as gs

import run_time_eval as rte
import GraphConstructionAlgorithms as gca

class GraphData():
	def __init__(self, V, E, id):
		self.G = nx.Graph()
		self.G.add_nodes_from(V)
		self.G.add_edges_from(E)
		self.id = id
		
	def __json__(self):
		return {"V": [n for n in self.G.nodes()], "E": [e for e in self.G.edges()], "id": self.id}	

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

	#if not "."+fileending in filename:
	#	filename += "."+fileending

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
	id_nr = 0
	for g in list_of_graphs:
		filenameparts = re.split(r'\.', filename)
		data.append(GraphData(g.nodes(), g.edges(), filenameparts[0]+"_"+str(id_nr)))
		id_nr += 1
		
	with open(path+filename, 'w') as jsonfile:
		json.dump(data, jsonfile, cls=meta.My_JSON_Encoder)

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
		graph_data = GraphData(g_data["V"], g_data["E"], g_data["id"])
		list_of_graphs.append(graph_data)

	return list_of_graphs

def construct_set_random_er(number_of_graphs, n, p, force_new_data=False):
	filename = "data/eval/random/input/ER_n"+str(n)+"_p"+str(p).replace('.','')
	if (not os.path.isfile(filename+".json")) or (force_new_data):
		gg = gca.GraphGenerator()
		graphs = []
		for i in range(number_of_graphs):
			graphs.append(gg.construct_connected_er(n, p))
	
		write_graphs_to_json(graphs, filename)

def construct_set_random_planar_er(number_of_graphs, n, m, force_new_data=False):
	filename = "data/eval/random_planar/input/ERP_n"+str(n)+"_m"+str(int(m)).replace('.','')
	if (not os.path.isfile(filename+".json")) or force_new_data:
		gg = gca.GraphGenerator()
		graphs = []
		for i in range(number_of_graphs):
			graphs.append(gg.construct_planar_er(n, m))
	
		write_graphs_to_json(graphs, filename)
	
def construct_set_random_planar(number_of_graphs, n, m, force_new_data=False):
	filename = "data/eval/random_planar/input/P_n"+str(n)+"_m"+str(int(m)).replace('.','')
	if (not os.path.isfile(filename+".json")) or force_new_data:
		gg = gca.GraphGenerator()
		graphs = []
		for i in range(number_of_graphs):
			graphs.append(gg.construct_planar_random(n, m))

		write_graphs_to_json(graphs, filename)

def construct_set_random_maxdeg(number_of_graphs, n, p, max_deg, force_new_data=False):
	filename = "data/eval/random_maxdeg/input/ERMD_n"+str(n)+"_p"+str(int(p))+"_d"+str(max_deg).replace('.','')
	if (not os.path.isfile(filename+".json")) or force_new_data:
		gg = gca.GraphGenerator()
		graphs = []
		for i in range(number_of_graphs):
			graphs.append(gg.construct_random_max_degree(n, p, max_deg))

		write_graphs_to_json(graphs, filename)

def construct_set_random_maxclique(number_of_graphs, n, p, max_cliquesize, force_new_data=False):
	filename = "data/eval/random_maxclique/input/ERMC_n"+str(n)+"_p"+str(int(p))+"_c"+str(max_cliquesize).replace('.','')
	if (not os.path.isfile(filename+".json")) or force_new_data:
		gg = gca.GraphGenerator()
		graphs = []
		for i in range(number_of_graphs):
			graphs.append(gg.construct_random_max_clique_size(n, p, max_cliquesize))

		write_graphs_to_json(graphs, filename)
