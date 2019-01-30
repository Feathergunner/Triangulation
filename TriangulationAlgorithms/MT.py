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
		
		# construct set of possible chord edges:
		cycle_nodes = list(set([n for c in nx.cycle_basis(self.G) for n in c]))
		chord_edges = []
		for i in range(len(cycle_nodes)):
			for j in range(i+1, len(cycle_nodes)):
				chord_edge = (cycle_nodes[i], cycle_nodes[j])
				if chord_edge not in self.G.edges():
					chord_edges.append(chord_edge)
				
		# iterate through all subsets of chord edges by increasing set size.
		# for each subset, check if self.G + additional edges is chordal
		# return first set of edges that makes self.G chordal. this is a minimum triangulation.
		for k in range(1, len(chord_edges)+1):
			edgesets_size_k = itertools.combinations(chord_edges, k)
			for edgeset in edgesets_size_k:
				H = self.G.copy()
				H.add_edges_from(edgeset)
				if nx.is_chordal(H):
					self.H = H
					self.edges_of_triangulation = [e for e in edgeset]
					return