#!usr/bin/python
# -*- coding: utf-8 -*-

import logging
import cProfile 
import sys
import re
import time
from multiprocessing import Process

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

max_num_threads = 10	

log_format = ('[%(asctime)s] %(levelname)-8s %(name)-12s %(message)s')
logging.basicConfig(
	filename='logs/debug_eval.log',
	filemode='w',
	format=log_format,
	level=logging.INFO,
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
				process = Process(target=gdo.construct_set_random_er, args=(100,n,p))
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
				gdo.construct_set_random_er(100, n, p)
				
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
				process = Process(target=gdo.construct_set_random_planar, args=(100,n,m))
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
					gdo.construct_set_random_planar(100,n,m)
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
					process = Process(target=gdo.construct_set_random_maxdeg, args=(100,n,p,md))
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
						gdo.construct_set_random_maxdeg(100,n,p,md)
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
					process = Process(target=gdo.construct_set_random_maxclique, args=(100,n,p,mc))
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
						gdo.construct_set_random_maxclique(100,n,p,mc)
					except gca.TooManyIterationsException:
						logging.debug("TooManyIterationsException: No graphs constructed for this setting")
			
	if threaded:
		# wait until all threads are finished:
		for p in threads:
			p.join()
			
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
		elif arg_data[0] == "threaded":
			threaded = True
				
	if mode == "test":
		import tests
		
	elif (mode == "undefined" or dataset == "undefined" or (mode == "eval" and len(algos) == 0)):
		print ("Error! Missing parameters!")
		
	elif mode == "build":
		if dataset == "general":
			construct_full_set_random_graphs()
		elif dataset == "planar":
			construct_full_set_random_planar_graphs()
		elif dataset == "maxdeg":
			construct_full_set_random_maxdegree_graphs()
		elif dataset == "maxclique":
			construct_full_set_random_maxclique_graphs()
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
			rte.run_set_of_experiments(algo, eval_dir, paramters, threaded=threaded)

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

		(columns, stats) = rte.compute_statistics(data_dir)
		rte.construct_output_table(columns, stats, data_dir+"/out.tex")


		
	
