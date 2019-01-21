#!usr/bin/python
# -*- coding: utf-8 -*-

import logging

import random
import networkx as nx
import numpy as np

import graph_meta as gm

def evaluate_RMT(G, parameters={"iterations": 10}):
	n = parameters["iterations"]
	best_result = -1
	randomized_results = []
	for i in range(n):
		result = len(random_search_for_minimum_triangulation(G.copy(), parameters))
		randomized_results.append(result)
		if best_result < 0 or result < best_result:
			best_result = result
	return [best_result, np.mean(randomized_results), np.var(randomized_results)]

def random_search_for_minimum_triangulation(G, parameters={"iterations": 10}):
	'''
	A randomized algorithm that searches for the minimum triangulation.
	Returns the best approximation that was found within a specified number of iterations
	In each iteration: randomly add new edges to the original graph until it is triangulated.
	'''

	number_of_iterations = parameters["iterations"]

	# init database of edges that are not in the graph:
	V = G.nodes()
	E = G.edges()
	unused_edges = [(i, j) for i in range(len(V)) for j in range(len(V)) if not i == j and not (i,j) in E]

	current_best_triangulation_edges = []
	current_best_triangulation_size = -1
	for i in range(number_of_iterations):
		H = G.copy()
		graph_is_triangulated = False
		used_edges_this_iteration = []
		while not graph_is_triangulated:
			new_edge = None
			while new_edge == None or new_edge in used_edges_this_iteration:
				new_edge = random.choice(unused_edges)
			used_edges_this_iteration.append(new_edge)
			H.add_edges_from([new_edge])
			if nx.is_chordal(H):
				graph_is_triangulated = True

		triangulation_size = len(used_edges_this_iteration)
		if current_best_triangulation_size < 0 or triangulation_size < current_best_triangulation_size:
			current_best_triangulation_size = triangulation_size
			current_best_triangulation_edges = used_edges_this_iteration

	return current_best_triangulation_edges
