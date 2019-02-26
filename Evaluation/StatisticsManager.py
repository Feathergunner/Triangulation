#!usr/bin/python
# -*- coding: utf-8 -*-

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

from Evaluation import GraphDataOrganizer as gdo
from MetaScripts import meta

def load_axis_data_from_file(filename, axis, keep_nulls=False):
	with open(filename) as jsonfile:
		this_file_data = json.load(jsonfile)

	if axis=="RESULT_OPT":
		data = [d["output"] for d in this_file_data]
	elif axis=="TIME":
		data = [d["running_time"] for d in this_file_data if d["running_time"]>0]

	if not keep_nulls:
		return [d for d in data if d>0]
	else:
		return data

def get_algo_name_from_filename(filename, graph_set_id):
	algo_name_base = re.split('results_triangulate_',filename)[1]
	algo_name = re.split('\.',re.split("_"+graph_set_id, algo_name_base)[0])[0]
	return algo_name

def compute_relative_performance(setname, graph_set_id, axis="RESULT_OPT"):
	# initialize:
	datadir = "data/eval/random_"+setname+"/results"
	all_files_in_dir = os.listdir(datadir)
	files = [file for file in all_files_in_dir if ".json" in file and graph_set_id in file]
	data = {}
	files.sort()
	number_of_results = 0

	# load data:
	for algofile in files:
		filepath = datadir+"/"+algofile
		algo = get_algo_name_from_filename(algofile, graph_set_id)
		data[algo] = load_axis_data_from_file(filepath, axis, True)
		if number_of_results == 0:
			number_of_results = len(data[algo])

	# compute average_relative_performance:
	rp = {algo : [] for algo in data}
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
			rp[algoorder[a_i]].append(j)
			if a_i < len(algos)-1 and results[algoorder[a_i+1]] > results[algoorder[a_i]]:
				j += 1

	return rp

def compute_mean_relative_performance(setname, graph_set_id, axis="RESULT_OPT"):
	# initialize:
	datadir = "data/eval/random_"+setname+"/results"
	all_files_in_dir = os.listdir(datadir)
	files = [file for file in all_files_in_dir if ".json" in file and graph_set_id in file]
	algos = []

	# load data:
	for algofile in files:
		algos.append(get_algo_name_from_filename(algofile, graph_set_id))

	rp = compute_relative_performance(setname, graph_set_id, axis)
	mrp = {algo : np.mean(rp[algo]) for algo in algos}

	return mrp

def make_stat_boxplot(data, setname, graph_set_id, savedir=None, filename_suffix=None):
	# initialize:
	datadir = "data/eval/random_"+setname+"/results"
	all_files_in_dir = os.listdir(datadir)
	files = [file for file in all_files_in_dir if ".json" in file and graph_set_id in file]
	labels = []
	files.sort()

	# load data:
	for file in files:
		filepath = datadir+"/"+file
		results_label = get_algo_name_from_filename(file, graph_set_id)
		labels.append(results_label)

	# create plot:
	fig, ax1 = plt.subplots(figsize=(len(data), 6))
	#fig.canvas.set_window_title('A Boxplot Example')
	fig.subplots_adjust(bottom=0.3)

	ax1.set_xlabel('Algorithm')
	ax1.set_ylabel('Distribution of minimal fill-in')

	bp = ax1.boxplot(data, notch=0, sym='+', vert=1, whis=1.5)
	plt.setp(bp['boxes'], color='black')
	ax1.set_xticklabels(labels)
	for tick in ax1.get_xticklabels():
		tick.set_rotation(90)
	if savedir == None:
		plt.show()
	else:
		plt.savefig(savedir+"/"+graph_set_id+"_"+filename_suffix+".png")
	plt.close()

def make_stat_boxplot_output(setname, graph_set_id, axis="RESULT_OPT", savedir=None):
	# initialize:
	datadir = "data/eval/random_"+setname+"/results"
	all_files_in_dir = os.listdir(datadir)
	files = [file for file in all_files_in_dir if ".json" in file and graph_set_id in file]
	data = []
	files.sort()

	# load data:
	for file in files:
		filepath = datadir+"/"+file
		data.append(load_axis_data_from_file(filepath, axis))

	make_stat_boxplot(data, setname, graph_set_id, savedir, filename_suffix)

def make_stat_boxplot_rp(setname, graph_set_id, axis="RESULT_OPT", savedir=None):
	data = compute_relative_performance(setname, graph_set_id, axis)

	make_stat_boxplot(data, setname, graph_set_id, savedir)

def make_all_stat_boxplots(setname, axis="RESULT_OPT"):
	basedir = "data/eval/random_"+setname
	graphdir = basedir+"/input"
	resultdir = basedir+"/results"
	outputdir = basedir+"/plots"
	if not os.path.exists(outputdir):
		os.mkdir(outputdir)

	all_graph_set_ids = []
	for filename in os.listdir(graphdir):
		all_graph_set_ids.append(re.split(r'\.',filename)[0])

	for graph_set_id in all_graph_set_ids:
		make_stat_boxplot_output(setname, graph_set_id, axis, outputdir)