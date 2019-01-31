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
		
		self.H = self.G.copy()
		F = self.get_edges_of_inverse_graph(self.G)
		F_prime = F
		self.H.add_edges_from(F)

		# initialize set V_F of all nodes that are endpoint of some edge in F:
		V_F = list(set([v for e in F for v in e]))
		
		# init T: all edges e with len(T[e]) == 0 are removeable
		T  = {}
		for edge in F_prime:
			T[edge] = set()

		edge_uv = self.get_removeable_edge(F_prime, T)
		# while there are removeable edges:
		while (not edge_uv == None):
			u = edge_uv[0]
			v = edge_uv[1]
			for edge_rs in T:
				r = edge_rs[0]
				s = edge_rs[1]
				cn_of_rs_cap_VF = [n for n in self.get_combined_neighborhood(self.H,[r,s]) if n in V_F]
				if u in cn_of_rs_cap_VF and v in cn_of_rs_cap_VF:
					T[edge_rs].add(edge_uv)
			cn_of_uv_cap_VF = [n for n in self.get_combined_neighborhood(self.H,[u,v]) if n in V_F]
			for x in cn_of_uv_cap_VF:
				if (u,x) in F_prime:
					for e in [e for e in T[(u,x)] if v in e]:
						T[(u,x)].discard(e)
				if (v,x) in F_prime:
					for e in [e for e in T[(v,x)] if u in e]:
						T[(v,x)].discard(e)
			F_prime.remove(edge_uv)
			self.H.remove_edges_from([edge_uv])
			edge_uv = self.get_removeable_edge(F_prime, T)
		return self.H

	def get_edges_of_inverse_graph(self, G):
		'''
		computes all edges that are not in G

		Args:
			G : a graph in networkx format

		Returns:
			F : a set of edges s.t. no edge from F is in G and G + F is a complete graph
		'''

		F = []
		E = [e for e in G.edges()]
		V = list(G.nodes())
		for i in range(len(G.nodes())):
			for j in range(i+1, len(G.nodes())):
				e = (V[i],V[j])
				if e not in E:
					F.append(e)
		return F

	def get_removeable_edge(self, F, T):
		'''
		finds and returns an edge e form the set F with T[e] = {}
		'''
		removeable_edges = [e for e in F if len(T[e]) == 0]
		if len(removeable_edges) > 0:
			return removeable_edges[0]
		else:
			return None

	def get_combined_neighborhood(self, G, V):
		'''
		computes the combined neighborhood of V in G, that is:
			NC(V) = {w in V(G) | exists v in V: w in N(w) and not w in V}
		'''
		NC = []

		for v in V:
			NC += [n for n in G.neighbors(v) if n not in NC]

		return NC