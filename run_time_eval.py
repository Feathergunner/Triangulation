#!usr/bin/python
# -*- coding: utf-8 -*-

import time
import networkx as nx
import random

class measurement_result:
	'''
	Data structure to organize test and evaluation results
	'''
	def __init__(self, algorithm_name, algo_input, algo_output, running_time):
		self.algorithm_name = algorithm_name
		self.input = algo_input
		self.output = algo_output
		self.running_time = running_time

	def __str__(self):
		string =  "NAME:         "+self.algorithm_name+"\n"
		if isinstance(self.input, list):
			string += "INPUT:        "+str([str(item) for item in self.input])+"\n";
		else:
			string += "INPUT:        "+str(self.input)+"\n"
		if isinstance(self.output, list):
			string += "OUTPUT:       "+str([str(item) for item in self.output])+"\n";
		else:
			string += "OUTPUT:       "+str(self.output)+"\n"
		string += "RUNNING TIME: "+str(self.running_time)+" sec."
		return string

class AlgorithmEvaluator:
	def __init__(self, algo, algo_input, number_of_experiments=1, expected_result=None):
		self.algo = algo
		self.algo_input = algo_input
		self.number_of_experiments = number_of_experiments
		self.expected_result = expected_result
		self.results = []

	def run_single_experiment(self):
		'''
		Run a single experiment and measure the running time.

		Return:
			The statistics of this experiment.
		'''
		t_start = time.time()
		result = self.algo(self.algo_input)
		t_end = time.time()

		t_diff = t_end - t_start
		return measurement_result(self.algo.__name__, self.algo_input, result, t_diff)

	def run(self):
		for i in range(self.number_of_experiments):
			self.results.append(self.run_single_experiment())
