#!usr/bin/python
# -*- coding: utf-8 -*-

import logging
import numpy as np
import json
import csv
import re
import os

try:
	import tkinter
except ImportError:
	import matplotlib
	matplotlib.use('agg')
	import matplotlib.pyplot as plt
else:
	import matplotlib.pyplot as plt
	import matplotlib.lines as mlines

from Evaluation import GraphDataOrganizer as gdo
from Evaluation import ExperimentManager as em
from MetaScripts import meta
from MetaScripts import global_settings as gs

def load_axis_data_from_file(filename, axis, keep_nulls=False, cutoff_at_timelimit=True):
	'''
	loads evaluation data from a file

	args:
		filename: the filename
		axis: "OUTPUT" or "TIME", defines which data to load
		keep_nulls: if False, null-entries are removed from the data before returning
		cutoff_at_timelimit : if True, evaldata that terminated with exceeded timelimit is considered as not terminated

	return:
		a list of numbers
	'''
	if not os.path.isfile(filename):
		return [-1 for i in range(100)]
	with open(filename) as jsonfile:
		this_file_data = json.load(jsonfile)
	
	if not cutoff_at_timelimit:
		if axis=="OUTPUT":
			data = [d["output"] for d in this_file_data]
		elif axis=="TIME":
			data = [d["running_time"] for d in this_file_data if d["running_time"]>0]
	else:
		if axis=="OUTPUT":
			data = [d["output"] if d["running_time"] < d["timelimit"] else -1 for d in this_file_data]
		elif axis=="TIME":
			data = [d["running_time"] if d["running_time"] > 0 and d["running_time"] < d["timelimit"] else d["timelimit"] for d in this_file_data]

	if not keep_nulls:
		return [d for d in data if d>=0]
	else:
		return data

def get_algo_name_from_filename(filename):
	'''
	parses a filename of a EvalData file to get the name of the algorithm
	'''
	algo_parts = re.split('_',filename)
	algo_name = algo_parts[2]+"_"+algo_parts[3]+"_"+algo_parts[4]
	
	return algo_name

def load_evaldata_from_json(basedir, filename):
	'''
	Loads the Evaldata from a specific file
	'''
	graphdataset = []
	evaldataset = []
	filepath = basedir+"/results/"+filename
	if not "json" in filepath:
		filepath+=".json"
	with open(filepath,"r") as jsonfile:
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
				evaldata = em.EvalData(data["algo"], graphdata, data["randomized"], data["repetitions"], data["reduce_graph"], data["timelimit"])
			else:
				evaldata = em.EvalData("generic", graphdata)
			evaldata.set_results(data["output"], data["running_time"])
			if "output mean" in data:
				evaldata.out_mean = data["output mean"]
			if "output variance" in data:
				evaldata.out_var = data["output variance"]
			evaldataset.append(evaldata)
	return evaldataset
	
def load_data(graphclass="general", density_class="dense", n=None, p=None, rel_m=None, d=None, c=None, algocode=None, randomized=False, rand_repetitions=None, reduced=False, axis="OUTPUT", keep_nulls=False, cutoff_at_timelimit=False):
	'''
	loads all data from the evaldata-database that is conform to the specified parameters.
	
	args:
		n, p, rel_m, d, c: restrictions on the subclass of graphs.
			Only restrictions that are not "None" are considered.
		axis: "OUTPUT" or "TIME", defines which data to load
		keep_nulls: if False, null-entries are removed from the data before returning
		cutoff_at_timelimit : if True, evaldata that terminated with exceeded timelimit is considered as not terminated		
	'''
	logging.debug("sm.load_data")
	
	if not graphclass in gs.GRAPH_CLASSES:
		raise gdo.ParameterMissingException("Wrong parameter: graphclass: "+graphclass)
		
	if not density_class in ["dense", "sparse"]:
		raise gdo.ParameterMissingException("Wrong parameter: density_class: "+density_class)
	
	#if p == None and rel_m == None:
	#	raise gdo.ParameterMissingException("Missing parameters in initialization: p or rel_m")
		
	if density_class == "dense" and not graphclass == "general":
		raise gdo.ParameterMissingException("Incompatible parameters: graphclass: not general and density_class: dense")
		
	if graphclass == "maxdeg" and d == None:
		raise gdo.ParameterMissingException("Missing parameters in initialization: d")
		
	if graphclass == "maxclique" and c == None:
		raise gdo.ParameterMissingException("Missing parameters in initialization: c")
		
	if algocode not in gs.BASE_ALGO_CODES:
		raise gdo.ParameterMissingException("Wrong parameter: algocode: "+algocode)
	
	if randomized and rand_repetitions == None:
		raise gdo.ParameterMissingException("Missing parameters in initialization: rand_repetitions")
		
	base_dir = "data/eval/random_"+graphclass+"/results"
		
	if n == None:
		options_for_n = gs.GRAPH_SIZES
	else:
		options_for_n = [n]
	
	if density_class == "dense":
		if p == None:
			options_for_p = gs.GRAPH_DENSITIY_P
		else:
			options_for_p = [p]
	else:
		options_for_p = [-1]
		
	if density_class == "sparse":
		if rel_m == None:
			options_for_relm = gs.SPARSE_DENSITY_RELM
		else:
			options_for_relm = [rel_m]
	else:
		options_for_relm = [-1]
			
	if graphclass == "maxdeg":
		if d == None:
			options_for_d = gs.MAXDEGREE_SETTINGS
		else:
			options_for_d = [d]
	else:
		options_for_d = [-1]
			
	if graphclass == "maxclique":
		if c == None:
			options_for_c = gs.MAXCLIQUE_SETTINGS
		else:
			options_for_c = [c]
	else:
		options_for_c = [-1]
			
	data = {}
	for n in options_for_n:
		if n not in data:
			data[n] = {}
		for p in options_for_p:
			if p not in data[n]:
				data[n][p] = {}
			for rel_m in options_for_relm:
				if rel_m not in data[n][p]:
					data[n][p][rel_m] = {}
				for d in options_for_d:
					if d not in data[n][p][rel_m]:
						data[n][p][rel_m][d] = {}
					for c in options_for_c:
						if c not in data[n][p][rel_m][d]:
							data[n][p][rel_m][d][c] = {}
						if density_class == "dense":
							p_as_string = p_as_string = "{0:.2f}".format(p)
							graph_base_filename = "dense_n"+str(n)+"_p"+p_as_string
						elif density_class == "sparse":
							graph_base_filename = "sparse_n"+str(n)+"_relm"+str(rel_m)
						if graphclass == "maxdeg":
							graph_base_filename += "_d"+str(d)
						if graphclass == "maxclique":
							graph_base_filename += "_c"+str(c)
						graph_filename = re.sub('\.','', graph_base_filename)
						extended_algo_code = algocode
						if randomized:
							extended_algo_code += "_R"+str(rand_repetitions)
						else:
							extended_algo_code += "_X"
						if not reduced:
							extended_algo_code += "_B"
						else:
							extended_algo_code += "_X"
							
						evaldata_filename = "results_triangulate_"+extended_algo_code+"_"+graph_filename
						#print (evaldata_filename)
						
						filepath = base_dir+"/"+evaldata_filename+".json"
						data[n][p][rel_m][d][c][density_class] = load_axis_data_from_file(filepath, axis, keep_nulls, cutoff_at_timelimit)
	return data								
				
def compute_statistics(graphclass, density_class=None, algo=None):
	'''
	Computes relevant statistic from all EvalData files in a specific directory.
	Constructs a list of dicts that contains a dictionary for each file in the directory.
	Each dictionary contains data of the based experiment (graph data, algorithm data)
	as well as some computed statistics like mean and variance of fill-in size and runtime.
	Also writes these statistics to a file

	return:
		columns : contains the keys of the constructed dictionaries
		stats : contains the data
	'''
	datadir = "data/eval/random_"+graphclass
	logging.debug("Compute statistics for results in "+datadir)

	stats = []
	columns = ["graph id", "avg n", "avg m", "algorithm", "reduced", "repeats", "time limit", "mean time", "var time", "moo", "voo", "mmo", "mvo", "success (\%)"]
	progress = 0
	allfiles = [file for file in os.listdir(datadir+"/results") if ".json" in file]
	
	if not density_class == None:
		allfiles = [file for file in allfiles if density_class in file]
	if not algo == None:
		allfiles = [file for file in allfiles if algo in file]
	for file in allfiles:
		meta.print_progress(progress, len(allfiles))
		progress += 1

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
	write_stats_to_file(datadir, stats)

	return (columns, stats)
	
def write_stats_to_file(datadir, stats):
	with open(datadir+"/stats.json", 'w') as statsfile:
		json.dump(stats, statsfile, cls=meta.My_JSON_Encoder)

def load_stats_from_file(datadir):
	[path, filename] = gdo.check_filepath(datadir+"/stats.json")

	if not os.path.isdir(path):
		## TO DO: raise error
		return

	if not ".json" in filename:
		filename += ".json"

	with open(path+filename) as jsonfile:
		data = json.load(jsonfile)

	return data
	
def compute_relative_performance_distribution(data, negative_is_invalid=True):
	'''
	computes relative performance distribution for a set of algorithms on a set of experiments
	
	Args:
		data : a dict {algorithm : results}
			where dict[algorithm] is a list of numeric values, and has the same length for all algorithms
		negative_is_invales : if True, negative values in the result data are interpreted as invalid results
			and get set to infinity when computing the relative performance.
		
	Return:
		rpd : a dict {algorithm : relative performance distribution}
	'''
	
	
	if not isinstance(data, dict):
		## TODO : raise exception
		return
	
	rpd = {algo : [] for algo in data}
	algos = [algo for algo in data]
	
	number_of_results = len(dict[algos[0]])
	for a in algos:
		if not len(dict[a]) == number_of_results:
			## TODO : raise exception
			return rpd
			
	for i in range(number_of_results):
		results = {}
		# compute relative performance:
		for algo in algos:
			results[algo] = data[algo][i]
			if negative_is_invalid and results[algo] < 0:
				results[algo] = float("inf")
		algoorder = sorted(algos, key=lambda a: results[a])
		j = 1
		for a_i in range(len(algos)):
			rpd[algoorder[a_i]].append(j)
			if a_i < len(algos)-1 and results[algoorder[a_i+1]] > results[algoorder[a_i]]:
				j += 1
		
		# scale relative performance:
		for algo in algos:
			if not j == 1:
				rpd[algo][i] = 1+((len(algos)-1)*float(rpd[algo][i]-1)/(j-1))
			else:
				rpd[algo][i] = len(algos)
				
	return rpd	

def compute_relative_performance_distribution_for_subclass(setname, density_class, graph_set_id, axis="OUTPUT", algo_subset=None):
	'''
	for a set of experiments defined by a setname and a graph_set_id,
	this method computes the relative performance of all algorithms individually
	for each graph of the dataset.
	That is, for each graph of the dataset the algorithms get ordered by performance.

	Args:
		setname : the name of the major graph class (ie. "general", "planar", ...)
		graph_set_id : the id of the subclass of graphs
		axis : the axis of evaluation output that should be used for evaluation, ie "OUTPUT" or "TIME"
		algo_subset : if not None, only algorithms contained in this subset will be considered

	Return:
		rpd : a dict that maps algorithms to lists. For each algorithm a list is constructed that contains the
		relative performance on each input graph.
		That is, if "ALGO_A" performed second best on the 15th test graph, then rp["ALGO_A"][14] = 2
	'''
	# initialize:
	datadir = "data/eval/random_"+setname+"/results"
	all_files_in_dir = os.listdir(datadir)
	files = [file for file in all_files_in_dir if ".json" in file and graph_set_id in file and density_class in file]
	data = {}
	files.sort()

	# load data:
	for algofile in files:
		filepath = datadir+"/"+algofile
		algo = get_algo_name_from_filename(algofile)
		if algo_subset == None or algo in algo_subset:
			data[algo] = load_axis_data_from_file(filepath, axis, True, True)
	
	return compute_relative_performance_distribution(data)
	'''
	# compute average_relative_performance:
	rpd = {algo : [] for algo in data}
	algos = [algo for algo in data]

	for i in range(number_of_results):
		results = {}
		for algo in data:
			results[algo] = data[algo][i]
			if results[algo] < 0:
				results[algo] += 1000000
		algoorder = sorted(algos, key=lambda a: results[a])
		j = 1
		for a_i in range(len(algos)):
			rpd[algoorder[a_i]].append(j)
			if a_i < len(algos)-1 and results[algoorder[a_i+1]] > results[algoorder[a_i]]:
				j += 1
		
		for algo in algos:
			if not j == 1:
				rpd[algo][i] = 1+((len(algos)-1)*float(rpd[algo][i]-1)/(j-1))
			else:
				rpd[algo][i] = len(algos)
				
	return rpd
	'''

def compute_mean_relative_performance(setname, graph_set_id, axis="OUTPUT"):
	# initialize:
	datadir = "data/eval/random_"+setname+"/results"
	all_files_in_dir = os.listdir(datadir)
	files = [file for file in all_files_in_dir if ".json" in file and graph_set_id in file]
	algos = []
	
	# load data:
	for algofile in files:
		algos.append(get_algo_name_from_filename(algofile))

	rp = compute_relative_performance_distribution(setname, graph_set_id, axis)
	mrp = {algo : np.mean(rp[algo]) for algo in algos}

	return mrp