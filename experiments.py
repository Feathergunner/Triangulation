#!usr/bin/python
# -*- coding: utf-8 -*-

import logging
#import cProfile 
import os
import sys
import re
import time
from multiprocessing import Process
from subprocess import call

from MetaScripts import meta
from MetaScripts import global_settings as gs

from Evaluation import GraphConstructionAlgorithms as gca
from Evaluation import GraphDataOrganizer as gdo
from Evaluation import ExperimentManager as em

from TriangulationAlgorithms import LEX_M
from TriangulationAlgorithms import MCS_M
from TriangulationAlgorithms import MT
from TriangulationAlgorithms import MTA
from TriangulationAlgorithms import EG
from TriangulationAlgorithms import RAMT
from TriangulationAlgorithms import SMS
from TriangulationAlgorithms import CMT

ALGORITHMS = {
	"EG"		: EG.triangulate_EG,
	"EG_R"		: EG.triangulate_EG,
	"LEXM"		: LEX_M.triangulate_LexM,
	"LEXM_R"	: LEX_M.triangulate_LexM,
	"MCSM"		: MCS_M.triangulate_MCSM,
	"MCSM_R"	: MCS_M.triangulate_MCSM,
	"MT"		: MT.triangulate_MT,
	"MTA"		: MTA.triangulate_MTA, 
	"MT_R"		: RAMT.triangulate_RAMT, 
	"SMS"		: SMS.triangulate_SMS,
	"SMS_R"		: SMS.triangulate_SMS,
	"CMT"		: CMT.triangulate_CMT,
	"CMT_R"		: CMT.triangulate_CMT,
	"EGP"		: EG.triangulate_EGPLUS,
	"EGP_R"		: EG.triangulate_EGPLUS
	}
	
#all_algorithms = [LEX_M.evaluate_LEX_M, EG.evaluate_elimination_game, EG.evaluate_randomized_elimination_game]#, ramt.random_search_for_minimum_triangulation]#MT.find_minimum_triangulation,
#all_algorithms = [EG.evaluate_elimination_game, EG.evaluate_randomized_elimination_game]
#max_number_of_iterations = 100

#max_num_threads = 10	

log_format = ('[%(asctime)s] %(levelname)-8s %(name)-12s %(message)s')
logging.basicConfig(
	filename='logs/debug_experiments.log',
	filemode='w',
	format=log_format,
	level=logging.ERROR,
)

VALID_MODES = ["build", "eval", "test", "output"]
VALID_SETS = ["general", "planar", "maxdeg", "maxclique"]

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
		em.run_set_of_experiments(algo, "data/eval/random_maxdeg", paramters)

if __name__ == "__main__":
	
	mode = "undefined"
	dataset = "undefined"
	threaded = False
	randomized = False
	reduced = True
	num_iter = 1
	algo_code = None
	data_dir = "data/eval/"
	timelimit = -1
	forcenew = False
	
	for arg in sys.argv[1:]:
		arg_data = re.split(r'=', arg)
		if arg_data[0] == "mode":
			if arg_data[1] in VALID_MODES:
				mode = arg_data[1]
			else:
				print("Error! Incorrect mode: "+arg_data[1])
		elif arg_data[0] == "set":
			if arg_data[1] in VALID_SETS:
				dataset = arg_data[1]
				data_dir += "random_"+dataset
			else:
				print("Error! Incorrect set: "+arg_data[1])
		elif arg_data[0] == "algo":
			if arg_data[1] in ALGORITHMS.keys():
				algo_code = arg_data[1]
			else:
				print("Error! Incorrect algo code: "+arg_data[1])
		elif arg_data[0] == "loglevel":
			level = int(arg_data[1])
			if level >= 0 and level <= 50:
				logging.basicConfig(
					filename='logs/debug_experiments.log',
					filemode='w',
					format=log_format,
					level=level
				)
		elif arg_data[0] == "threaded":
			threaded = True
		elif arg_data[0] == "iterations":
			num_iter = int(arg_data[1])
		elif arg_data[0] == "noreduce":
			reduced = False
		elif arg_data[0] == "forcenew":
			forcenew = True
		elif arg_data[0] == "timelimit":
			timelimit = float(arg_data[1])
		else:
			print ("Argument "+arg_data[0]+" unknown!")
				
	logging.info("cmd line args:")
	logging.info(sys.argv)
	logging.info(mode)
	logging.info(dataset)
	logging.info(algo_code)
	
	if mode == "test":
		import tests
		
	elif (mode == "undefined" or dataset == "undefined" or (mode == "eval" and algo_code == None)):
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
		algo = ALGORITHMS[algo_code]
		if "_R" in algo_code:
			randomized = True
		
		em.run_set_of_experiments(algo, data_dir, randomized=randomized, repetitions=num_iter, threaded=threaded, reduce_graph=reduced, timelimit=timelimit, force_new_data=forcenew)

	elif mode == "output":
		(columns, stats) = em.compute_statistics(data_dir)
		em.construct_output_table(columns, stats, data_dir+"/out.tex")
		
		os.chdir(data_dir)
		call(["pdflatex","out.tex"])
