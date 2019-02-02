#!usr/bin/python
# -*- coding: utf-8 -*-

import logging

import networkx as nx
import itertools

from TriangulationAlgorithms import TriangulationAlgorithm as ta

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
		self.compute_minimum_triangulation()
		
	def compute_minimum_triangulation(self):
		# trivial case: check if G is already chordal:
		if nx.is_chordal(self.G):
			self.H = self.G
			self.edges_of_triangulation = []
			return
			
		# use LEX-M to determine the size of a minimal triangulation to have an upper bound for the minimum triangulation
		from TriangulationAlgorithms import LEX_M
		lexm_triang = LEX_M.triangulate_LexM(self.G)
		size_minimal = lexm_triang["size"]
		logging.debug("size of minimal: "+str(size_minimal))
		
		# construct set of possible chord edges:
		# only consider subgraphs after all separators of size 1 have been removed from graph:
		cycle_nodes = list(set([n for c in nx.cycle_basis(self.G) for n in c]))
		single_node_separators = [n for n in self.G.nodes() if n not in cycle_nodes]
		G_c = self.G.subgraph(single_node_separators)
		chord_edges = []
		for c in nx.connected_components(G_c):
			for i in range(len(c)):
				for j in range(i, len(c)):
					chord_edge = (c[i], c[j])
					if chord_edge not in self.G.edges():
						chord_edges.append(chord_edge)
		'''
		for i in range(len(cycle_nodes)):
			for j in range(i+1, len(cycle_nodes)):
				chord_edge = (cycle_nodes[i], cycle_nodes[j])
				if chord_edge not in self.G.edges():
					chord_edges.append(chord_edge)
		'''
				
		# iterate through all subsets of chord edges by increasing set size.
		# for each subset, check if self.G + additional edges is chordal
		# return first set of edges that makes self.G chordal. this is a minimum triangulation.
		for k in range(1, len(chord_edges)+1):
			if k == size_minimal:
				self.H = lexm_triang["H"]
				self.edges_of_triangulation = [e for e in self.H.edges() if e not in self.G.edges()]
				return
			logging.debug("Current iteration: consider edgesets of size "+str(k))
			edgesets_size_k = itertools.combinations(chord_edges, k)
			for edgeset in edgesets_size_k:
				H = self.G.copy()
				H.add_edges_from(edgeset)
				if nx.is_chordal(H):
					self.H = H
					self.edges_of_triangulation = [e for e in edgeset]
					return