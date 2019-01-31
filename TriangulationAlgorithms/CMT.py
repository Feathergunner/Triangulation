#!usr/bin/python
# -*- coding: utf-8 -*-

import logging

import networkx as nx
import random
import numpy as np

from TriangulationAlgorithms import TriangulationAlgorithm as ta

def triangulate_CMT(G, randomized=False, repetitions=1):
	algo = Algorithm_CMT(G)
	if not randomized:
		algo.run()
		return {
			"H" : algo.get_triangulated(),
			"size" : len(algo.get_triangulation_edges()),
			"mean" : len(algo.get_triangulation_edges()),
			"variance" : 0,
			"repetitions" : 1
			}

class Algorithm_CMT(ta.TriangulationAlgorithm):
	def __init__(self, G):
		logging.info("=== CMT.Algorithm_CMT.init ===")
		super().__init__(G)

	def run(self):
		self.triangulate(self.G)

	def run_randomized(self):
		pass

	def triangulate(self, randomize=False):
		'''
		Implementation of the algorithm "Clique Minimal Triangulation" 
			Mezzini, Moscarini: Simple algorithms for minimal triangulation of a graph and backward selection of a decomposable Markov network
			https://www.sciencedirect.com/science/article/pii/S030439750900735X
		to construct a minimal triangulation H of a graph G
		
		Args:
			G : a graph in netwokx format
			randomize : if set to True, the order in which the nodes are processed is randomized
		
		Returns:
			H : a minimal triangulation of G.
		'''
		logging.info("=== triangulate_CMT ===")
		#self.H = self.G.copy()
		
		F = self.get_edges_of_inverse_graph(self.G)
		F_prime = F
		T  = {}
		for edge in F_prime:
			T[edge] = []

	def get_edges_of_inverse_graph(self, G):
		'''
		computes all edges that are not in G

		Args:
			G : a graph in networkx format

		Returns:
			F : a set of edges s.t. no edge from F is in G and G + F is a complete graph
		'''

		F = []
		for i in range(len(G.nodes())):
			for j in range(i+1, len(G.nodes())):
				if (i,j) not in G.edges():
					F.append((i,j))
		return F