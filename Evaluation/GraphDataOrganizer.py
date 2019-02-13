#!usr/bin/python
# -*- coding: utf-8 -*-

import logging
import networkx as nx
import re
import os
import json
import time

from multiprocessing import Process

from MetaScripts import meta
from MetaScripts import global_settings as gs

from Evaluation import GraphConstructionAlgorithms as gca

max_num_threads = 10

class GraphData():
	'''
	A class to manage graph data and handle the graph data export to json files
	'''
	def __init__(self, V, E, id, parameters={}):
		self.G = nx.Graph()
		self.G.add_nodes_from(V)
		self.G.add_edges_from(E)
		self.id = id
		self.parameters = parameters
		
	def __json__(self):
		return {"V": [n for n in self.G.nodes()],
				"E": [e for e in self.G.edges()],
				"id": self.id,
				"parameters": self.parameters}	

def check_filepath(filepath):
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
		if not os.path.exists(path):
			os.mkdir(path)

	if len(path_components) > 1:
		filename = path_components[-1]

	#if not "."+fileending in filename:
	#	filename += "."+fileending

	return [path, filename]


def write_graphs_to_json(list_of_graphs, filename, parameters={}):
	'''
	Stores a set of graphs in a json file.

	Args:
		list_of_graphs : a list of graphs in networkx-format.
		filename : the name of the target file.
		parameters : a dictionary that may contain additional informations
	'''

	[path, filename] = check_filepath(filename)

	data = []
	id_nr = 0
	for g in list_of_graphs:
		filenameparts = re.split(r'\.', filename)
		data.append(GraphData(g.nodes(), g.edges(), filenameparts[0]+"_"+str(id_nr), parameters))
		id_nr += 1

	if not ".json" in filename:
		filename += ".json"
		
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
		if "parameters" in g_data:
			graph_data = GraphData(g_data["V"], g_data["E"], g_data["id"], g_data["parameters"])
		else:
			graph_data = GraphData(g_data["V"], g_data["E"], g_data["id"])
		list_of_graphs.append(graph_data)

	return list_of_graphs

def construct_set_random_er(number_of_graphs, n, p, force_new_data=False):
	filename_init = "data/eval/random_general/input/ER_n"+str(n)+"_p"+str(p)
	filename = re.sub('\.','', filename_init)
	if (not os.path.isfile(filename+".json")) or (force_new_data):
		gg = gca.GraphGenerator()
		graphs = []
		for i in range(number_of_graphs):
			graphs.append(gg.construct_connected_er(n, p))
	
		write_graphs_to_json(graphs, filename)

def construct_set_random_planar_er(number_of_graphs, n, m, force_new_data=False):
	filename_init = "data/eval/random_planar/input/ERP_n"+str(n)+"_m"+str(int(m))
	filename = re.sub('\.','', filename_init)
	if (not os.path.isfile(filename+".json")) or force_new_data:
		gg = gca.GraphGenerator()
		graphs = []
		for i in range(number_of_graphs):
			graphs.append(gg.construct_planar_er(n, m))
	
		write_graphs_to_json(graphs, filename)
	
def construct_set_random_planar(number_of_graphs, n, m, force_new_data=False):
	filename_init = "data/eval/random_planar/input/P_n"+str(n)+"_m"+str(int(m))
	filename = re.sub('\.','', filename_init)
	if (not os.path.isfile(filename+".json")) or force_new_data:
		gg = gca.GraphGenerator()
		graphs = []
		for i in range(number_of_graphs):
			graphs.append(gg.construct_planar_random(n, m))

		write_graphs_to_json(graphs, filename)

def construct_set_random_maxdeg(number_of_graphs, n, p, max_deg, force_new_data=False):
	filename_init = "data/eval/random_maxdeg/input/ERMD_n"+str(n)+"_p"+str(p)+"_d"+str(max_deg)
	filename = re.sub('\.','', filename_init)
	if (not os.path.isfile(filename+".json")) or force_new_data:
		gg = gca.GraphGenerator()
		graphs = []
		for i in range(number_of_graphs):
			graphs.append(gg.construct_random_max_degree(n, p, max_deg))

		write_graphs_to_json(graphs, filename, {"max degree": max_deg})

def construct_set_random_maxclique(number_of_graphs, n, p, max_cliquesize, force_new_data=False):
	filename_init = "data/eval/random_maxclique/input/ERMC_n"+str(n)+"_p"+str(p)+"_c"+str(max_cliquesize)
	filename = re.sub('\.','', filename_init)
	print (filename)
	if (not os.path.isfile(filename+".json")) or force_new_data:
		gg = gca.GraphGenerator()
		graphs = []
		for i in range(number_of_graphs):
			graphs.append(gg.construct_random_max_clique_size(n, p, max_cliquesize))

		write_graphs_to_json(graphs, filename, {"max clique": max_cliquesize})


def construct_full_set_random_graphs(threaded=True):
	logging.info("=== construct_full_set_random_graphs ===")
	
	if threaded:
		threads = []
		threadset = {}
		
	total = len(gs.RANDOM_GRAPH_SETTINGS["n"]) * len(gs.RANDOM_GRAPH_SETTINGS["p"])
	i = 0
	for n in gs.RANDOM_GRAPH_SETTINGS["n"]:
		for p in gs.RANDOM_GRAPH_SETTINGS["p"]:
			logging.debug("Constructing graphs with parameters n: "+str(n)+", p "+str(p))
			if threaded:
				process = Process(target=construct_set_random_er, args=(100,n,p))
				threads.append(process)
				process.start()
				
				threads = [p for p in threads if p.is_alive()]
				while len(threads) >= max_num_threads:
					#print ("thread limit reached... wait")
					time.sleep(1.0)
					threads = [p for p in threads if p.is_alive()]
			else:
				meta.print_progress(i, total)
				i += 1
				construct_set_random_er(100, n, p)
				
	if threaded:
		# wait until all threads are finished:
		for p in threads:
			p.join()
	
def construct_full_set_random_planar_graphs(threaded=True):
	logging.info("=== construct_full_set_random_planar_graphs ===")
	
	if threaded:
		threads = []
		threadset = {}
		
	total = len(gs.RANDOM_PLANAR_SETTINGS["n"]) * len(gs.RANDOM_PLANAR_SETTINGS["rel_m"])
	i = 0
	for n in gs.RANDOM_PLANAR_SETTINGS["n"]:
		for rel_m in gs.RANDOM_PLANAR_SETTINGS["rel_m"]:
			logging.debug("Constructing graphs with parameters n: "+str(n)+", rel_m "+str(rel_m))
			m = n*rel_m
			if threaded:
				process = Process(target=construct_set_random_planar, args=(100,n,m))
				threads.append(process)
				process.start()
				
				threads = [p for p in threads if p.is_alive()]
				while len(threads) >= max_num_threads:
					#print ("thread limit reached... wait")
					time.sleep(1.0)
					threads = [p for p in threads if p.is_alive()]
			else:
				meta.print_progress(i, total)
				i += 1
				try:
					#gdo.construct_set_random_planar_er(100,n,m)
					construct_set_random_planar(100,n,m)
				except gca.TooManyIterationsException:
					logging.debug("TooManyIterationsException: No graphs constructed for this setting")
					
	if threaded:
		# wait until all threads are finished:
		for p in threads:
			p.join()

def construct_full_set_random_maxdegree_graphs(threaded=True):
	logging.info("=== construct_full_set_random_maxdegree_graphs ===")
	total = len(gs.RANDOM_GRAPH_SETTINGS["n"]) * len(gs.RANDOM_GRAPH_SETTINGS["p"]) * len(gs.RANDOM_MAXDEGREE_SETTINGS)
	
	if threaded:
		threads = []
		threadset = {}
		
	i = 0
	for n in gs.RANDOM_GRAPH_SETTINGS["n"]:
		for p in gs.RANDOM_GRAPH_SETTINGS["p"]:
			for md in gs.RANDOM_MAXDEGREE_SETTINGS:
				logging.debug("Constructing graphs with parameters n: "+str(n)+", p: "+str(p)+", max degree: "+str(md))
				if threaded:
					process = Process(target=construct_set_random_maxdeg, args=(100,n,p,md))
					threads.append(process)
					process.start()
					
					threads = [p for p in threads if p.is_alive()]
					while len(threads) >= max_num_threads:
						#print ("thread limit reached... wait")
						time.sleep(1.0)
						threads = [p for p in threads if p.is_alive()]
				else:
					meta.print_progress(i, total)
					i += 1
					try:
						#gdo.construct_set_random_planar_er(100,n,m)
						construct_set_random_maxdeg(100,n,p,md)
					except gca.TooManyIterationsException:
						logging.debug("TooManyIterationsException: No graphs constructed for this setting")

	if threaded:
		# wait until all threads are finished:
		for p in threads:
			p.join()

def construct_full_set_random_maxclique_graphs(threaded=True):
	logging.info("=== construct_full_set_random_maxdegree_graphs ===")
	total = len(gs.RANDOM_GRAPH_SETTINGS["n"]) * len(gs.RANDOM_GRAPH_SETTINGS["p"]) * len(gs.RANDOM_MAXCLIQUE_SETTINGS)
	
	if threaded:
		threads = []
		threadset = {}
		
	i = 0
	for n in gs.RANDOM_GRAPH_SETTINGS["n"]:
		for p in gs.RANDOM_GRAPH_SETTINGS["p"]:
			for mc in gs.RANDOM_MAXCLIQUE_SETTINGS:
				logging.debug("Constructing graphs with parameters n: "+str(n)+", p: "+str(p)+", max clique size: "+str(mc))
				if threaded:
					process = Process(target=construct_set_random_maxclique, args=(100,n,p,mc))
					threads.append(process)
					process.start()
					
					threads = [p for p in threads if p.is_alive()]
					while len(threads) >= max_num_threads:
						#print ("thread limit reached... wait")
						time.sleep(1.0)
						threads = [p for p in threads if p.is_alive()]
				else:
					meta.print_progress(i, total)
					i += 1
					try:
						#gdo.construct_set_random_planar_er(100,n,m)
						construct_set_random_maxclique(100,n,p,mc)
					except gca.TooManyIterationsException:
						logging.debug("TooManyIterationsException: No graphs constructed for this setting")
			
	if threaded:
		# wait until all threads are finished:
		for p in threads:
			p.join()
			