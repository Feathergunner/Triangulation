#!usr/bin/python
# -*- coding: utf-8 -*-

import logging

import networkx as nx
import itertools

from TriangulationAlgorithms import TriangulationAlgorithm as ta
from TriangulationAlgorithms import LEX_M

def triangulate_MT(G, randomized=False, repetitions=1):
	algo = Algorithm_MinimumTriangulation(G)
	algo.run()
	return {
		"H" : algo.get_triangulated(),
		"size" : len(algo.get_triangulation_edges()),
		"mean" : len(algo.get_triangulation_edges()),
		"variance" : 0,
		"repetitions" : 1
		}

class Algorithm_MinimumTriangulation(ta.TriangulationAlgorithm):
	def __init__(self, G):
		logging.info("=== MTA.Algorithm_MinimumTriangulation.init ===")
		super().__init__(G)
		
	def run(self):
		for C in self.component_subgraphs:
			# get triangulation for each connected component of the reduced graph G_c:
			self.edges_of_triangulation += self.compute_minimum_triangulation_of_component(C)
		
		self.H = self.G.copy()
		self.H.add_edges_from(self.edges_of_triangulation)
		
	def compute_minimum_triangulation_of_component(self, C):
		logging.debug("Find minimum triangulation for next component...")
		edges_of_triangulation = []
	
		# use LEX-M to determine the size of a minimal triangulation to have an upper bound for the minimum triangulation
		lexm_triang = LEX_M.triangulate_LexM(C)
		size_minimal = lexm_triang["size"]
		logging.debug("size of minimal: "+str(size_minimal))
		
		# iterate through all subsets of chord edges by increasing set size.
		# for each subset, check if self.G + additional edges is chordal
		# return first set of edges that makes self.G chordal. this is a minimum triangulation.
		k = 1
		found_minimum = False
		while not found_minimum and k < size_minimal:
			logging.debug("Current iteration: consider edgesets of size "+str(k))
			edgesets_size_k = itertools.combinations(self.chordedge_candidates, k)
			for edgeset in edgesets_size_k:
				H = C.copy()
				H.add_edges_from(edgeset)
				if nx.is_chordal(H):
					edges_of_triangulation += [e for e in edgeset]
					found_minimum = True
			k += 1
		if k == size_minimal:
			edges_of_triangulation += [e for e in lexm_triang["H"].edges() if e not in C.edges()]
			
		return edges_of_triangulation
		