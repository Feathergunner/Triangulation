#!usr/bin/python
# -*- coding: utf-8 -*-

import time

class measurement_result:
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

def measure_running_time(algo_function, algo_input):
	start = time.time()
	result = algo_function(algo_input)
	end = time.time()

	running_time = end-start
	return measurement_result(algo_function.__name__, algo_input, result, running_time)