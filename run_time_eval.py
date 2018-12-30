#!usr/bin/python
# -*- coding: utf-8 -*-

import os
import time
import networkx as nx
import random
import json

import GraphDataOrganizer as gdo
import graph_meta as gm

class EvalData:
	'''
	Data structure to organize test and evaluation results
	'''
	def __init__(self, algo, input_graph_data):
		self.algo = algo
		self.input = input_graph_data.G
		self.id = input_graph_data.id
		self.max_iterations = -1
		
		self.measurement_finished = False
		self.output = None
		self.running_time = None
		
	def __json__(self):
		json_dict = {"name" : self.algo.__name__, "input_id": self.id}
		if self.max_iterations >= 0:
			json_dict["max_iter"] = self.max_iterations
		if self.measurement_finished:
			json_dict["output"] = self.output
			json_dict["running_time"] = self.running_time
		return json_dict

	def __str__(self):
		string =      "ALGO_NAME:    "+self.algo.__name__+"\n"
		string +=     "INPUT_ID:     "+self.id+"\n"
		if isinstance(self.input, list):
			string += "INPUT:        "+str([str(item) for item in self.input])+"\n";
		else:
			string += "INPUT:        "+str(self.input)+"\n"
		if self.measurement_finished:
			if self.max_iterations >= 0:
				string += "ITERATIONS:   "+str(self.max_iterations)+"\n"
			string += "OUTPUT:       "+str(self.output)+"\n"
			string += "RUNNING TIME: "+str(self.running_time)+" sec."
		return string
		
	def set_max_iter(self, n):
		self.max_iterations = n
		
	def set_results(self, output, running_time):
		self.measurement_finished = True
		self.output = output
		self.running_time = running_time
		
def run_single_experiment(evaldata):
	'''
	Run a single experiment and measure the running time.

	Return:
		The statistics of this experiment.
	'''
	t_start = time.time()
	result = evaldata.algo(evaldata.input, evaldata.max_iterations)
	t_end = time.time()

	t_diff = t_end - t_start
	evaldata.set_results(result, t_diff)
	return evaldata

def run_set_of_experiments(algo, datadir, n):
	'''
	Run all experiment with a specific algorithm with all graphs from a directory
	'''
	for filename in os.listdir(datadir+"/input"):
		results = []
		if ".json" in filename:
			list_of_graphs = gdo.load_graphs_from_json(datadir+"/input/"+filename)
			for graphdata in list_of_graphs:
				evaldata = EvalData(algo, graphdata)
				evaldata.set_max_iter(n)
				#id = graphdata["id"]
				#graph = [graphdata["V"], graphdata["E"]]
				results.append(run_single_experiment(evaldata))
		result_filename = "results_"+algo.__name__+"_"+filename
		store_results(results, datadir+"/results/"+result_filename)
				
def store_results(list_of_results, filename):
	print(filename)
	[path, filename] = gdo.check_filepath(filename)
		
	with open(path+filename, 'w') as jsonfile:
		json.dump(list_of_results, jsonfile, cls=gm.My_JSON_Encoder)

def make_statistics():
	## TODO
	pass