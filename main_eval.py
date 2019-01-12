#!usr/bin/python
# -*- coding: utf-8 -*-

import logging
import cProfile 

import sys
import re

import meta

import GraphConstructionAlgorithms as gca
import GraphDataOrganizer as gdo
import global_settings as gs
import run_time_eval as rte

import LEX_M
import MT
import EG
import Random_Approx_MT as ramt

#all_algorithms = [LEX_M.evaluate_LEX_M, EG.evaluate_elimination_game, EG.evaluate_randomized_elimination_game]#, ramt.random_search_for_minimum_triangulation]#MT.find_minimum_triangulation,
all_algorithms = [EG.evaluate_elimination_game, EG.evaluate_randomized_elimination_game]
max_number_of_iterations = 100

log_format = ('[%(asctime)s] %(levelname)-8s %(name)-12s %(message)s')
logging.basicConfig(
	filename='logs/debug_eval.log',
	filemode='w',
	format=log_format,
	level=logging.DEBUG,
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

def construct_full_set_random_graphs():
	logging.info("=== construct_full_set_random_graphs ===")
	total = len(gs.RANDOM_GRAPH_SETTINGS["n"]) * len(gs.RANDOM_GRAPH_SETTINGS["p"])
	i = 0
	for n in gs.RANDOM_GRAPH_SETTINGS["n"]:
		for p in gs.RANDOM_GRAPH_SETTINGS["p"]:
			logging.debug("Constructing graphs with parameters n: "+str(n)+", p "+str(p))
			meta.print_progress(i, total)
			i += 1
			gdo.construct_set_random_er(100, n, p)
	
def construct_full_set_random_planar_graphs():
	logging.info("=== construct_full_set_random_planar_graphs ===")
	total = len(gs.RANDOM_PLANAR_SETTINGS["n"]) * len(gs.RANDOM_PLANAR_SETTINGS["rel_m"])
	i = 0
	for n in gs.RANDOM_PLANAR_SETTINGS["n"]:
		for rel_m in gs.RANDOM_PLANAR_SETTINGS["rel_m"]:
			logging.debug("Constructing graphs with parameters n: "+str(n)+", rel_m "+str(rel_m))
			meta.print_progress(i, total)
			i += 1
			m = n*rel_m
			try:
				#gdo.construct_set_random_planar_er(100,n,m)
				gdo.construct_set_random_planar(100,n,m)
			except gca.TooManyIterationsException:
				logging.debug("TooManyIterationsException: No graphs constructed for this setting")

def construct_full_set_random_maxdegree_graphs():
	logging.info("=== construct_full_set_random_maxdegree_graphs ===")
	total = len(gs.RANDOM_GRAPH_SETTINGS["n"]) * len(gs.RANDOM_GRAPH_SETTINGS["p"]) * len(gs.RANDOM_MAXDEGREE_SETTINGS)
	i = 0
	for n in gs.RANDOM_GRAPH_SETTINGS["n"]:
		for p in gs.RANDOM_GRAPH_SETTINGS["p"]:
			for md in gs.RANDOM_MAXDEGREE_SETTINGS:
				logging.debug("Constructing graphs with parameters n: "+str(n)+", p: "+str(p)+", max degree: "+str(md))
				meta.print_progress(i, total)
				i += 1
				try:
					#gdo.construct_set_random_planar_er(100,n,m)
					gdo.construct_set_random_maxdeg(100,n,p,md)
				except gca.TooManyIterationsException:
					logging.debug("TooManyIterationsException: No graphs constructed for this setting")


def construct_full_set_random_maxclique_graphs():
	logging.info("=== construct_full_set_random_maxdegree_graphs ===")
	total = len(gs.RANDOM_GRAPH_SETTINGS["n"]) * len(gs.RANDOM_GRAPH_SETTINGS["p"]) * len(gs.RANDOM_MAXCLIQUE_SETTINGS)
	i = 0
	for n in gs.RANDOM_GRAPH_SETTINGS["n"]:
		for p in gs.RANDOM_GRAPH_SETTINGS["p"]:
			for mc in gs.RANDOM_MAXCLIQUE_SETTINGS:
				logging.debug("Constructing graphs with parameters n: "+str(n)+", p: "+str(p)+", max clique size: "+str(mc))
				meta.print_progress(i, total)
				i += 1
				try:
					#gdo.construct_set_random_planar_er(100,n,m)
					gdo.construct_set_random_maxclique(100,n,p,mc)
				except gca.TooManyIterationsException:
					logging.debug("TooManyIterationsException: No graphs constructed for this setting")
			
def run_evaluation():
	paramters = {"n": 10}
	for algo in all_algorithms:
		rte.run_set_of_experiments(algo, "data/eval/random_maxdeg", paramters)

#cProfile.run("gdo.construct_set_random_planar(1,40,60)")
#construct_full_set_random_planar_graphs()
#construct_full_set_random_graphs()
#construct_full_set_random_maxdegree_graphs()
#construct_full_set_random_maxclique_graphs()
#run_evaluation()

#print (rte.compute_statistics("data/eval/random"))

if __name__ == "__main__":
	mode = "undefined"
	set = "undefined"
	algos = []
	logging.info("cmd line args:")
	logging.info(sys.argv)
	for arg in sys.argv[1:]:
		arg_data = re.split(r'=', arg)
		if arg_data[0] == "mode":
			if arg_data[1] in ["build", "eval", "test"]:
				mode = arg_data[1]
		elif arg_data[0] == "set":
			if arg_data[1] in ["general", "planar", "maxdeg", "maxclique"]:
				set = arg_data[1]
		elif arg_data[0] == "algo":
			if arg_data[1] in ["EG", "EG_R", "LEXM", "LEXM_R", "MT", "MT_R"]:
				algos.append(arg_data[1])
				
	if mode == "test":
		import tests
		
	elif (mode == "undefined" or set == "undefined" or (mode == "eval" and len(algos) == 0)):
		print ("Error! Missing parameters!")
		
	elif mode == "build":
		if set == "general":
			construct_full_set_random_graphs()
		elif set == "planar":
			construct_full_set_random_planar_graphs()
		elif set == "maxdeg":
			construct_full_set_random_maxdegree_graphs()
		elif set == "maxclique":
			construct_full_set_random_maxclique_graphs()
	elif mode == "eval":
		algorithms = []
		for algo_code in algos:
			if algo_code == "EG":
				algorithms.append(EG.evaluate_elimination_game)
			elif algo_code == "EG_R":
				algorithms.append(EG.evaluate_randomized_elimination_game)
			elif algo_code == "LEXM":
				algorithms.append(LEX_M.evaluate_LEX_M)
			elif algo_code == "LEXM_R":
				algorithms.append(LEX_M.evaluate_randomized_LEX_M)
			elif algo_code == "MT":
				algorithms.append(MT.get_minimum_triangulation_size)
			elif algo_code == "MT_R":
				algorithms.append(ramt.random_search_for_minimum_triangulation)
		
		eval_dir = ""
		if set == "general":
			eval_dir = "data/eval/random"
		elif set == "planar":
			eval_dir = "data/eval/random_planar"
		elif set == "maxdeg":
			eval_dir = "data/eval/random_maxdeg"
		elif set == "maxclique":
			eval_dir = "data/eval/random_maxclique"
			
		paramters = {"n": 10}
		for algo in algorithms:
			rte.run_set_of_experiments(algo, eval_dir, paramters)
		
	
