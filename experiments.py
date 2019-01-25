#!usr/bin/python
# -*- coding: utf-8 -*-

import logging
import cProfile 
import sys
import re
import time
from multiprocessing import Process

from MetaScripts import meta
from MetaScripts import global_settings as gs

from Evaluation import GraphConstructionAlgorithms as gca
from Evaluation import GraphDataOrganizer as gdo
from Evaluation import ExperimentManager as em

import LEX_M
import MT
import EG
import Random_Approx_MT as ramt

#all_algorithms = [LEX_M.evaluate_LEX_M, EG.evaluate_elimination_game, EG.evaluate_randomized_elimination_game]#, ramt.random_search_for_minimum_triangulation]#MT.find_minimum_triangulation,
all_algorithms = [EG.evaluate_elimination_game, EG.evaluate_randomized_elimination_game]
max_number_of_iterations = 100

max_num_threads = 10	

log_format = ('[%(asctime)s] %(levelname)-8s %(name)-12s %(message)s')
logging.basicConfig(
	filename='logs/debug_experiments.log',
	filemode='w',
	format=log_format,
	level=logging.ERROR,
)

def fix_filenames(datadir):
	import os
	import re
	for filename in [filename for filename in os.listdir(datadir)]:
		filenameparts = re.split(r'\.', filename)
		new_filename = ''.join(filenameparts[:-1])
		new_filename += '.'+filenameparts[-1]
		print ("orig filename: "+filename)
		print ("new filename: "+new_filename)
		os.rename(datadir+"/"+filename, datadir+"/"+new_filename)

def run_evaluation():
	paramters = {"n": 10}
	for algo in all_algorithms:
		me.run_set_of_experiments(algo, "data/eval/random_maxdeg", paramters)

#cProfile.run("gdo.construct_set_random_planar(1,40,60)")
#construct_full_set_random_planar_graphs()
#construct_full_set_random_graphs()
#construct_full_set_random_maxdegree_graphs()
#construct_full_set_random_maxclique_graphs()
#run_evaluation()

#print (me.compute_statistics("data/eval/random"))

if __name__ == "__main__":
	mode = "undefined"
	dataset = "undefined"
	threaded = False
	algos = []
	logging.info("cmd line args:")
	logging.info(sys.argv)
	for arg in sys.argv[1:]:
		arg_data = re.split(r'=', arg)
		if arg_data[0] == "mode":
			if arg_data[1] in ["build", "eval", "test", "output"]:
				mode = arg_data[1]
		elif arg_data[0] == "set":
			if arg_data[1] in ["general", "planar", "maxdeg", "maxclique"]:
				dataset = arg_data[1]
		elif arg_data[0] == "algo":
			if arg_data[1] in ["EG", "EG_R", "LEXM", "LEXM_R", "MT", "MT_R", "SMS", "SMS_R"]:
				algos.append(arg_data[1])
		elif arg_data[0] == "loglevel":
			if arg_data[1] >= 0 && arg_data[1] <= 50:
				logging.basicConfig(
					filename='logs/debug_experiments.log',
					filemode='w',
					format=log_format,
					level=arg_data[1]
				)
		elif arg_data[0] == "threaded":
			threaded = True
				
	if mode == "test":
		import tests
		
	elif (mode == "undefined" or dataset == "undefined" or (mode == "eval" and len(algos) == 0)):
		print ("Error! Missing parameters!")
		
	elif mode == "build":
		if dataset == "general":
			gdo.construct_full_set_random_graphs()
		elif dataset == "planar":
			gdo.construct_full_set_random_planar_graphs()
		elif dataset == "maxdeg":
			gdo.construct_full_set_random_maxdegree_graphs()
		elif dataset == "maxclique":
			gdo.construct_full_set_random_maxclique_graphs()
	elif mode == "eval":
		algorithms = []
		paramters = {}
		for algo_code in algos:
			if algo_code == "EG":
				algorithms.append(EG.evaluate_elimination_game)
			elif algo_code == "EG_R":
				algorithms.append(EG.evaluate_randomized_elimination_game)
				paramters["iterations"] = 10
			if algo_code == "SMS":
				algorithms.append(SMS.evaluata_sms)
			elif algo_code == "SMS_R":
				algorithms.append(EG.evaluata_randomized_sms)
				paramters["iterations"] = 10
			elif algo_code == "LEXM":
				algorithms.append(LEX_M.evaluate_LEX_M)
			elif algo_code == "LEXM_R":
				algorithms.append(LEX_M.evaluate_randomized_LEX_M)
				paramters["iterations"] = 10
			elif algo_code == "MT":
				algorithms.append(MT.get_minimum_triangulation_size)
			elif algo_code == "MT_R":
				algorithms.append(ramt.random_search_for_minimum_triangulation)
				paramters["iterations"] = 10
		
		eval_dir = ""
		if dataset == "general":
			eval_dir = "data/eval/random"
		elif dataset == "planar":
			eval_dir = "data/eval/random_planar"
		elif dataset == "maxdeg":
			eval_dir = "data/eval/random_maxdeg"
		elif dataset == "maxclique":
			eval_dir = "data/eval/random_maxclique"
		
		for algo in algorithms:
			me.run_set_of_experiments(algo, eval_dir, paramters, threaded=threaded)

	elif mode == "output":
		data_dir = "data/eval/"
		if dataset == "general":
			data_dir += "random"
		elif dataset == "planar":
			data_dir += "random_planar"
		elif dataset == "maxdeg":
			data_dir += "random_maxdeg"
		elif dataset == "maxclique":
			data_dir += "random_maxclique"

		(columns, stats) = me.compute_statistics(data_dir)
		me.construct_output_table(columns, stats, data_dir+"/out.tex")


		
	
