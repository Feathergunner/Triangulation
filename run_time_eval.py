#!usr/bin/python
# -*- coding: utf-8 -*-

import time

class measurement_result:
	def __init__(self, algorithm, algo_input, algo_output, running_time):
		self.algorithm_name = algorithm
		self.input = algo_input
		self.output = algo_output
		self.running_time = running_time

def measure_running_time(algo_function, algo_input):
	start = time.time()
	result = algo_function(algo_input)
	end = time.time()

	running_time = end-start
	return measurement_result(algorithm, algo_input, result, running_time)