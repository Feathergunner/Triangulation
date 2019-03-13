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

class ParameterMissingException(Exception):
	'''
	Custom error type that gets thrown when the generalized graph set construction method misses input parameters
	'''

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
		self.n = len(V)
		self.m = len(E)
		
	def __json__(self):
		return {"V": [n for n in self.G.nodes()],
				"E": [e for e in self.G.edges()],
				"n": self.n,
				"m": self.m,
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

	#if len(path_components) > 1:
	filename = path_components[-1]

	#if not "."+fileending in filename:
	#	filename += "."+fileending

	return [path, filename]

def parse_graph_filename(filename):
	'''
	Parses a filename of a graphset-json and returns the parameters of the contained set
	'''
	basic_filename = re.split('\/', re.plit('\.', filename)[0])[-1]
	parts = re.split('_', basic_filename)
	
	parameters = {}
	parameters["subclass"] = parts[0]
	parameters["n"] = int(parts[1][1:])
	
	if parameters["subclass"] == "dense":
		parameters["p"] = float(parts[2][2:])/10
	elif parameters["subclass"] == "sparse":
		parameters["rel_m"] = float(parts[2][4:])/10
	
	for i in range(3, len(parts)):
		if parts[i][0] == "d":
			parameters["max_deg"] = int(parts[i][1:])
		elif parts[i][0] == "c":
			parameters["max_clique"] = int(parts[i][1:])
		
	return parameters

def check_parameters(parameters):
	if not "class" in parameters or parameters["class"] not in gs.GRAPH_CLASSES:
		raise ParameterMissingException("Missing parameters in initialization: class")
	
	if parameters["class"] == "maxdeg" and not "deg_bound" in parameters:
		raise ParameterMissingException("Missing parameters in initialization: deg_bound")
		
	if parameters["class"] == "maxclique" and not "clique_bound" in parameters:
		raise ParameterMissingException("Missing parameters in initialization: clique_bound")
		
	if not "n" in parameters:
		raise ParameterMissingException("Missing parameters in initialization: n")
	
	if not "p" in parameters and not "rel_m" in parameters:
		raise ParameterMissingException("Missing parameters in initialization: p or rel_m")
		
	if not "number_of_graphs" in parameters:
		raise ParameterMissingException("Missing parameters in initialization: number_of_graphs")
	
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

def construct_set_random_graph(parameters, force_new_data=False):
	check_parameters(parameters)
		
	graphclass = parameters["class"]
	n = parameters["n"]
	
	p = -1	
	if "p" in parameters:
		subclass = "dense"
		p = parameters["p"]
	elif "rel_m" in parameters:
		subclass = "sparse"
		p = round((2*parameters["rel_m"]*n)/(n*(n-1)),2)
	
	graphdir = "data/eval/random_"+graphclass+"/input/"
	check_filepath(graphdir)
	
	if subclass == "dense":
		p_as_string = "{0:.2f}".format(p)
		filename_init = subclass+"_n"+str(n)+"_p"+p_as_string
	elif subclass == "sparse":
		filename_init = subclass+"_n"+str(n)+"_relm"+str(parameters["rel_m"])
	if graphclass == "maxdeg":
		filename_init += "_d"+str(parameters["deg_bound"])
	if graphclass == "maxclique":
		filename_init += "_c"+str(parameters["clique_bound"])
	filename = re.sub('\.','', filename_init)
	filepath = graphdir+filename+".json"
	
	if (not os.path.isfile(filepath)) or force_new_data:
		gg = gca.GraphGenerator()
		graphs = []
		for i in range(parameters["number_of_graphs"]):
			if graphclass == "general":
				graphs.append(gg.construct_connected_er(n, p))
				
			elif graphclass == "planar":
				graphs.append(gg.construct_planar_random(n, p))
			
			elif graphclass == "maxdeg":
				graphs.append(gg.construct_random_max_degree(n, p, parameters["deg_bound"]))
			
			elif graphclass == "maxclique":
				graphs.append(gg.construct_random_max_clique_size(n, p, parameters["clique_bound"]))
	
		write_graphs_to_json(graphs, filepath, parameters)
	

def construct_full_set_graphs(graphclass, number_of_graphs_per_subclass = 100, threaded=True):
	logging.info("=== construct_full_set_raphs ===")
	
	options_for_p = []
	if graphclass == "general":
		options_for_p = gs.GRAPH_DENSITIY_P
	if graphclass == "maxdeg":
		options_for_p = gs.BOUNDEDGRAPHS_DENSITY_P
		options_for_d = gs.MAXDEGREE_SETTINGS
	else:
		options_for_d = [-1]
	if graphclass == "maxclique":
		options_for_p = gs.BOUNDEDGRAPHS_DENSITY_P
		options_for_c = gs.MAXCLIQUE_SETTINGS
	else:
		options_for_c = [-1]	
			
	base_params = {
		"number_of_graphs" : number_of_graphs_per_subclass,
		"class" : graphclass
	}
	
	if threaded:
		threads = []
		threadset = {}
	else:
		total = len(gs.GRAPH_SIZES) * len(options_for_d) * len(options_for_c) * (len(options_for_p) + len(gs.SPARSE_DENSITY_RELM))
		i = 0
		
	for n in gs.GRAPH_SIZES:		
		for d in options_for_d:
			for c in options_for_c:
				if graphclass == "maxdeg":
					base_params["deg_bound"] = d
				if graphclass == "maxclique":
					base_params["clique_bound"] = c
				for p in options_for_p:
					# construct dense graphs:
					
					params = {key : base_params[key] for key in base_params}
					params["n"] = n
					params["p"] = p
					
					logging.debug("Constructing graphs with parameters n: "+str(n)+", p: "+str(p)+", d: "+str(d)+", c: "+str(c))
					
					if threaded:
						process = Process(target=construct_set_random_graph, kwargs={"parameters":params})
						threads.append(process)
						process.start()
						
						threads = [p for p in threads if p.is_alive()]
						while len(threads) >= gs.MAX_NUM_THREADS:
							#print ("thread limit reached... wait")
							time.sleep(1.0)
							threads = [p for p in threads if p.is_alive()]
					else:
						meta.print_progress(i, total)
						i += 1
						construct_set_random_graph(params)
		
				for rel_m in gs.SPARSE_DENSITY_RELM:
					# construct sparse graphs:
					params = {key : base_params[key] for key in base_params}
					params["n"] = n
					params["rel_m"] = rel_m
					if graphclass == "maxdeg":
						params["deg_bound"] = d
					if graphclass == "maxclique":
						params["clique_bound"] = c
						
					logging.debug("Constructing sparse graphs with parameters n: "+str(n)+", rel_m "+str(rel_m)+", d: "+str(d)+", c: "+str(c))
					
					if threaded:
						process = Process(target=construct_set_random_graph, kwargs={"parameters":params})
						threads.append(process)
						process.start()
						
						threads = [p for p in threads if p.is_alive()]
						while len(threads) >= gs.MAX_NUM_THREADS:
							#print ("thread limit reached... wait")
							time.sleep(1.0)
							threads = [p for p in threads if p.is_alive()]
					else:
						meta.print_progress(i, total)
						i += 1
						construct_set_random_graph(params)
	
	if threaded:
		# wait until all threads are finished:
		for p in threads:
			p.join()
			