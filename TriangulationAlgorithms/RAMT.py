#!usr/bin/python
# -*- coding: utf-8 -*-

import logging

import networkx as nx
import random
import numpy as np

from TriangulationAlgorithms import TriangulationAlgorithm as ta

def triangulate_RAMT(G, repeats=1):
	algo = Algorithm_RAMT(G)
	
	H_opt = None
	size_opt = None
	all_sizes = []
	for i in range(repeats):
		algo.run()
		all_sizes.append(len(algo.get_triangulation_edges()))
		if H_opt == None or len(algo.get_triangulation_edges()) < size_opt:
			H_opt = algo.get_triangulated()
			size_opt = len(algo.get_triangulation_edges())
	return {
		"H" : H_opt,
		"size" : size_opt,
		"mean" : np.mean(all_sizes),
		"variance" : np.var(all_sizes),
		"repeats" : repeats
		}

class Algorithm_RAMT(ta.TriangulationAlgorithm):
	'''
	Randomized Approximative Minimum Triangulation
	'''
	def __init__(self, G):
		logging.info("=== RAMT.Algorithm_RAMT.init ===")
		super().__init__(G)

	def run(self):
		self.triangulate()
		
	def triangulate(self):
		'''
		A randomized algorithm that searches for the minimum triangulation by randomly adding new edges to the original graph until it is triangulated.
		'''
		# init database of edges that are not in the graph:
		V = self.G.nodes()
		E = self.G.edges()
		unused_edges = [(i, j) for i in range(len(V)) for j in range(len(V)) if not i == j and not (i,j) in E]
	
		self.H = self.G.copy()
		graph_is_triangulated = False
		self.edges_of_triangulation = []
		while not graph_is_triangulated:
			new_edge = None
			while new_edge == None or new_edge in self.edges_of_triangulation:
				new_edge = random.choice(unused_edges)
			self.edges_of_triangulation.append(new_edge)
			self.H.add_edges_from([new_edge])
			if nx.is_chordal(self.H):
				graph_is_triangulated = True
