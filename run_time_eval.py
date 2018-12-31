#!usr/bin/python
# -*- coding: utf-8 -*-

import meta
import logging
import os
import time
import networkx as nx
import random
import json
import csv
import re

import GraphDataOrganizer as gdo
#import graph_meta as gm

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
		return self.to_dict()

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
		
	def to_dict(self):
		dict = {"name" : self.algo.__name__, "input_id": self.id}
		if self.max_iterations >= 0:
			dict["max_iter"] = self.max_iterations
		if self.measurement_finished:
			dict["output"] = self.output
			dict["running_time"] = self.running_time
		return dict
		
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

def run_set_of_experiments(algo, datadir, n, force_new_data=False):
	'''
	Run all experiment with a specific algorithm with all graphs from a directory
	'''
	all_datafiles = [filename for filename in os.listdir(datadir+"/input") if ".json" in filename]
	num_files = len(all_datafiles)
	i = 0
	for file in all_datafiles:
		filename = re.split(r'\.json', file)[0]
		result_filename = "results_"+algo.__name__+"_"+filename
		logging.debug("Evaluate algo "+algo.__name__+ "on graphs of file: "+filename)
		meta.print_progress(i, num_files)
		i += 1
		if (not os.path.isfile(result_filename)) or force_new_data:
			results = []
			list_of_graphs = gdo.load_graphs_from_json(datadir+"/input/"+filename)
			for graphdata in list_of_graphs:
				evaldata = EvalData(algo, graphdata)
				evaldata.set_max_iter(n)
				#id = graphdata["id"]
				#graph = [graphdata["V"], graphdata["E"]]
				results.append(run_single_experiment(evaldata))
			store_results_json(results, datadir+"/results/"+result_filename)
			store_results_csv(results, datadir+"/results/"+result_filename)
				
def store_results_json(list_of_results, filename):
	logging.debug("Store evaluation results to json file: "+filename)
	[path, filename] = gdo.check_filepath(filename)
		
	with open(path+filename+".json", 'w') as jsonfile:
		json.dump(list_of_results, jsonfile, cls=meta.My_JSON_Encoder)
		
def store_results_csv(list_of_results, filename):
	logging.debug("Store evaluation results to csv file: "+filename)
	[path, filename] = gdo.check_filepath(filename)
	
	with open (path+filename+".csv", 'w') as csvfile:
		csvwriter = csv.DictWriter(csvfile, fieldnames=list_of_results[0].to_dict().keys())
		csvwriter.writeheader()
		for r in list_of_results:
			csvwriter.writerow(r.to_dict())
		#csvwriter.writerows([r.to_dict() for r in list_of_results])

def make_statistics():
	## TODO
	pass