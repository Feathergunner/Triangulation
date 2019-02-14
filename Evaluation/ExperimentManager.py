#!usr/bin/python
# -*- coding: utf-8 -*-

import logging
import os
import time
import networkx as nx
import numpy as np
import random
import json
import csv
import re
from multiprocessing import Process

from MetaScripts import meta
from Evaluation import GraphDataOrganizer as gdo
from TriangulationAlgorithms import TriangulationAlgorithm as ta

class EvalData:
	'''
	Data structure to organize test and evaluation results
	'''
	def __init__(self, algo, input_graph_data, is_randomized, repetitions, reduce_graph, timelimit):
		self.algo = algo
		self.input = input_graph_data.G
		self.n = len(input_graph_data.G.nodes())
		self.m = len(input_graph_data.G.edges())
		self.id = input_graph_data.id
		self.is_randomized = is_randomized
		self.repetitions = repetitions
		self.reduce_graph = reduce_graph
		self.timelimit = timelimit
		
		self.measurement_finished = False
		self.output = None
		self.out_mean = None
		self.out_var = None
		self.running_time = None
		
	def __json__(self):
		return self.to_dict()

	def __str__(self):
		if type(self.algo) is str:
			string =  "ALGO_NAME:    "+self.algo+"\n"
		else:
			string =  "ALGO_NAME:    "+self.algo.__name__+"\n"
		string +=     "INPUT_ID:     "+self.id+"\n"
		if isinstance(self.input, list):
			string += "INPUT:        "+str([str(item) for item in self.input])+"\n";
		else:
			string += "INPUT:        "+str(self.input)+"\n"
		if self.is_randomized:
			string += "#RAND. REP.:  "+str(self.repetitions)+"\n"
		if self.measurement_finished:
			string += "OUTPUT:       "+str(self.output)+"\n"
			string += "RUNNING TIME: "+str(self.running_time)+" sec.\n"
		if self.reduce_graph:
			string += "REDUCED:      1\n"
		else:
			string += "REDUCED:      0\n"
		string +=     "TIME LIMIT:  "+str(self.timelimit)+" sec.\n"
		return string
		
	def to_dict(self):
		dict = {
			"input_id": self.id,
			"n": self.n,
			"m": self.m,
			"randomized": self.is_randomized,
			"repetitions": self.repetitions,
			"reduce_graph": self.reduce_graph,
			"timelimit": self.timelimit
		}
		
		if type(self.algo) is str:
			dict["algo"] = self.algo
		else:
			dict["algo"] = self.algo.__name__
		if self.measurement_finished:
			dict["output"] = self.output
			dict["running_time"] = self.running_time
			if not self.out_mean == None:
				dict["output mean"] = self.out_mean
			if not self.out_var == None:
				dict["output variance"] = self.out_var
		return dict
		
	def set_results(self, output, running_time):
		self.measurement_finished = True
		self.running_time = running_time
		if type(output) is dict:
			self.output = output["size"]
			self.out_mean = output["mean"]
			self.out_var = output["variance"]
		else:
			self.output = output

	def set_failed(self, running_time):
		self.measurement_finished = True
		self.running_time = running_time
		self.output = -1
		self.out_mean = -1
		self.out_var = -1
			
	def __lt__(self,other):
		if not self.algo == other.algo:
			return self.algo < other.algo
		elif not self.n == other.n:
			return self.n < other.n
		elif not self.reduce_graph == other.reduce_graph:
			if self.reduce_graph:
				return True
			else:
				return False
		elif not self.is_randomized == other.is_randomized:
			if self.is_randomized:
				return False
			else:
				return True
		elif not self.repetitions == other.repetitions:
			return self.repetitions < other.repetitions
		else:
			return self.id < other.id
		
#class ExperimentManager:
def run_single_experiment(evaldata):
	'''
	Run a single experiment and measure the running time.

	Return:
		The statistics of this experiment.
	'''
	t_start = time.time()
	if evaldata.timelimit > 0:
		timeout = t_start + evaldata.timelimit
	else:
		timeout = -1
	try:
		result = evaldata.algo(evaldata.input, evaldata.is_randomized, evaldata.repetitions, evaldata.reduce_graph, timeout)
		t_end = time.time()
		t_diff = t_end - t_start
		evaldata.set_results(result, t_diff)
	except ta.TimeLimitExceededException:
		t_end = time.time()
		t_diff = t_end - t_start
		evaldata.set_failed(t_diff)
	return evaldata
	
def run_subset_of_experiments(algo, randomized, repetitions, reduce_graph, timelimit, datadir, filename, result_filename):
	'''
	Run a specified algorithm on all graphs of a single dataset-file
	'''
	results = []
	list_of_graphs = gdo.load_graphs_from_json(datadir+"/input/"+filename)
	#print(filename)
	for graphdata in list_of_graphs:
		#print(graphdata.id)
		evaldata = EvalData(algo, graphdata, randomized, repetitions, reduce_graph, timelimit)
		results.append(run_single_experiment(evaldata))
	store_results_json(results, datadir+"/results/"+result_filename)
	store_results_csv(results, datadir+"/results/"+result_filename)

def run_set_of_experiments(algo, datadir, randomized, repetitions, threaded=False, reduce_graph=True, timelimit=-1, force_new_data=False):
	'''
	Run all experiment with a specific algorithm with all graphs from a directory
	'''
	logging.info("=== run_set_of_experiments ===")
	logging.debug("datadir: "+datadir)
	logging.debug("repetitions: ")
	logging.debug(repetitions)
	all_datafiles = [filename for filename in os.listdir(datadir+"/input") if ".json" in filename]
	logging.debug("all_Datafiles: "+str(all_datafiles))
	
	max_num_threads = 10
	if threaded:
		threads = []
		threadset = {}
	
	num_files = len(all_datafiles)
	filename_sufix = ""
	if randomized:
		filename_sufix += "_r"+str(repetitions)
	i = 0
	for file in all_datafiles:
		# construct output filename:
		filename = re.split(r'\.json', file)[0]
		result_filename = "results_"+algo.__name__
		if randomized:
			result_filename += "_R"+str(repetitions)
		if not reduce_graph:
			result_filename += "_B"
		result_filename += "_"+filename+filename_sufix
		
		if (not os.path.isfile(datadir+"/results/"+result_filename+".json")) or force_new_data:
			if not threaded:
				logging.debug("Evaluate algo "+algo.__name__+ "on graphs of file: "+filename)
				meta.print_progress(i, num_files)
				i += 1
			if threaded:
				p = Process(target=run_subset_of_experiments, args=(algo, randomized, repetitions, reduce_graph, timelimit, datadir, filename, result_filename))
				threads.append(p)
				p.start()
				
				threads = [p for p in threads if p.is_alive()]
				while len(threads) >= max_num_threads:
					#print ("thread limit reached... wait")
					time.sleep(1.0)
					threads = [p for p in threads if p.is_alive()]

			else:
				run_subset_of_experiments(algo, randomized, repetitions, reduce_graph, timelimit, datadir, filename, result_filename)
	
	if threaded:
		# wait until all threads are finished:
		for p in threads:
			p.join()
				
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
			
def load_evaldata_from_json(basedir, filename):
	graphdataset = []
	evaldataset = []
	with open(basedir+"/results/"+filename+".json", "r") as jsonfile:
		dataset = json.load(jsonfile)
		for data in dataset:
			graph_id = re.split(r'\.',data["input_id"])[0]
			if graphdataset == []:
				graphdatafile = "_".join(re.split(r'_',data["input_id"])[:-1])+".json"
				graphdataset = gdo.load_graphs_from_json(basedir+"/input/"+graphdatafile)
			graphdata = None
			for gd in graphdataset:
				gd.id = re.split(r'\.', gd.id)[0]
				if gd.id == graph_id:
					graphdata = gd
					break
			if "reduce_graph" not in data:
				data["reduce_graph"] = True
			if "timelimit" not in data:
				data["timelimit"] = -1
			if "randomized" not in data:
				data["randomized"] = False
			if "repetitions" not in data:
				data["repetitions"] = 1
			if "algo" in data:
				evaldata = EvalData(data["algo"], graphdata, data["randomized"], data["repetitions"], data["reduce_graph"], data["timelimit"])
			else:
				evaldata = EvalData("generic", graphdata)
			evaldata.set_results(data["output"], data["running_time"])
			if "output mean" in data:
				evaldata.out_mean = data["output mean"]
			if "output variance" in data:
				evaldata.out_var = data["output variance"]
			evaldataset.append(evaldata)
	return evaldataset	
		
def compute_statistics(datadir):
	logging.debug("Compute statistics for results in "+datadir)
	stats = []
	columns = ["graph id", "avg n", "avg m", "algorithm", "reduced", "repeats", "time limit", "mean time", "var time", "moo", "voo", "mmo", "mvo", "success (\%)"]
	for file in os.listdir(datadir+"/results"):
		if ".json" in file:
			filename = re.split(r'\.', file)[0]
			evaldata = load_evaldata_from_json(datadir, filename)
			graph_id = "_".join(re.split(r'_',evaldata[0].id)[:-1])
			avg_n = np.mean([data.n for data in evaldata])# if data.output >= 0])
			avg_m = np.mean([data.m for data in evaldata])# if data.output >= 0])
			timelimit = evaldata[0].timelimit
			mean_time = np.mean([data.running_time for data in evaldata if data.output >= 0])
			var_time = np.var([data.running_time for data in evaldata if data.output >= 0])
			mean_output = np.mean([data.output for data in evaldata if data.output >= 0])
			var_output = np.var([data.output for data in evaldata if data.output >= 0])
			repeats = evaldata[0].repetitions
			mmo = np.mean([data.out_mean for data in evaldata if data.out_mean >= 0])
			mvo = np.mean([data.out_var for data in evaldata if data.out_var >= 0])
			algo_name = evaldata[0].algo
			if evaldata[0].is_randomized:
				algo_name += " (R)"

			if mmo == mean_output:
				mmo = "N/A"
				mvo = "N/A"

			success = 100*float(len([data.output for data in evaldata if data.output >= 0]))/float(len([data.output for data in evaldata]))

			newstats = {
				"algorithm" : algo_name,
				"reduced" : str(evaldata[0].reduce_graph),
				"graph id" : graph_id,
				"avg n" : avg_n,
				"avg m" : avg_m, 
				"mean time" : mean_time,
				"var time" : var_time,
				"moo" : mean_output,
				"voo" : var_output,
				"repeats" : repeats,
				"mmo" : mmo,
				"mvo" : mvo,
				"time limit" : timelimit,
				"success (\%)": success
			}
			for key in newstats:
				if not isinstance(newstats[key], str) and np.isnan(newstats[key]):
					newstats[key] = "N/A"

			stats.append(newstats)
				
	return (columns, stats)
			
def construct_output_table(columns, dataset, outputfilename="out.tex"):
	# sort dataset:
	sorteddataset = sorted(dataset, key=lambda data: (data["avg n"], data["graph id"], data["algorithm"], data["repeats"], data["reduced"]))

	texoutputstring = ""
	with open("tex_template.txt", "r") as tex_template:
		for line in tex_template:
			texoutputstring += line

	tabulardefline = "\\begin{longtable}{"
	for c in columns:
		tabulardefline += "c"
	tabulardefline += "}"
	texoutputstring += tabulardefline+"\n"

	tabheadline = columns[0]
	for i in range(1,len(columns)):
		tabheadline += " & "+columns[i]
	tabheadline += " \\\\ \\hline \n"
	texoutputstring += tabheadline
	#all_graph_ids = [key for key in dataset if not key == "algo"]
	data_keys = [key for key in columns] #if not key == "algorithm" and not key == "graph id"]

	non_numeric_data_keys = ["algorithm", "graph id", "reduced"]
	string_data_keys = ["algorithm", "reduced"]
	might_be_string_data_keys = ["mean time", "var time", "moo", "voo", "mmo", "mvo"]

	for data in sorteddataset:
		rowstring = "\\verb+"+data["graph id"]+ "+"
		#rowstring = "\\verb+"+data["algo"] + "+ & \\verb+" + data["graph_id"] + "+"
		for data_key in data_keys:
			#print(data_key +": "+str(data[data_key]))
			if data_key not in non_numeric_data_keys and not isinstance(data[data_key], str):
				if data_key ==  "mean time":
					precision = 4
					formatstring = "${0:.4f}$"
				else:
					precision = 2
					formatstring = "${0:.2f}$"
				rowstring += " & "+formatstring.format(round(data[data_key],precision))
			elif data_key in string_data_keys+might_be_string_data_keys:
				rowstring += " & \\verb+"+data[data_key]+"+"
		texoutputstring += rowstring+"\\\\\n"
	texoutputstring += "\\end{longtable}\n"
	texoutputstring += "\\end{document}\n"

	with open(outputfilename, "w") as tex_output:
		tex_output.write(texoutputstring)
	