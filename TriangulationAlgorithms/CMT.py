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
	else:
		H_opt = None
		size_opt = None
		all_sizes = []
		for i in range(repetitions):
			algo.run_randomized()
			all_sizes.append(len(algo.get_triangulation_edges()))
			if H_opt == None or len(algo.get_triangulation_edges()) < size_opt:
				H_opt = algo.get_triangulated()
				size_opt = len(algo.get_triangulation_edges())
		return {
			"H" : H_opt,
			"size" : size_opt,
			"mean" : np.mean(all_sizes),
			"variance" : np.var(all_sizes),
			"repetitions" : repetitions
			}

class Algorithm_CMT(ta.TriangulationAlgorithm):
	'''
	Implementation of the algorithm "Clique Minimal Triangulation" 
		Mezzini, Moscarini: Simple algorithms for minimal triangulation of a graph and backward selection of a decomposable Markov network
		https://www.sciencedirect.com/science/article/pii/S030439750900735X
	to construct a minimal triangulation H of a graph G
	
	Args:
		G : a graph in netwokx format
	'''
	
	def __init__(self, G):
		logging.info("=== CMT.Algorithm_CMT.init ===")
		super().__init__(G)

	def run(self):
		self.triangulate()

	def run_randomized(self):
		self.triangulate(randomized=True)

	def triangulate(self, randomized=False):
		'''
		Args:
			randomize : if set to True, the order in which the nodes are processed is randomized
		
		Returns:
			H : a minimal triangulation of G.
		'''
		logging.info("=== triangulate_CMT ===")
		
		self.H = self.G.copy()
		F = self.get_possible_triangulation_edges(self.G)
		#F = self.get_edges_of_inverse_graph(self.G)
		logging.info("size of F: "+str(len(F)))
		
		F_prime = self.minimize_triangulation(self.G, F, randomized)
		self.H.add_edges_from(F_prime)
		return self.H

	def minimize_triangulation(self, G, F, randomized):
		'''
		Minimize a given triangulation.
		
		Following the pseudocode given in:
		Mezzini, Moscarini: Simple algorithms for minimal triangulation of a graph and backward selection of a decomposable Markov network (see above)
		
		Args:
			G : a graph
			F : a set of edges, s.t. G + F is chordal
			randomized : if set to True, get_removeable_edge is randomized
			
		Returns:
			F_prime : a subset of F, s.t. G + F_prime is minimal chordal
		'''
		logging.info("=== CMT.minimize_triangulation ===")
		
		F_prime = F
		H = G.copy()
		H.add_edges_from(F)

		# initialize set V_F of all nodes that are endpoint of some edge in F:
		V_F = list(set([v for e in F for v in e]))
		
		# initialize T: all edges e with len(T[e]) == 0 are removeable
		T  = {}
		for edge in F_prime:
			T[edge] = set()

		edge_uv = self.get_removeable_edge(F_prime, T, randomized)
		# while there are removeable edges:
		while (not edge_uv == None):
			u = edge_uv[0]
			v = edge_uv[1]
			for edge_rs in T:
				r = edge_rs[0]
				s = edge_rs[1]
				cn_of_rs_cap_VF = [n for n in self.get_combined_neighborhood(H,[r,s]) if n in V_F]
				if u in cn_of_rs_cap_VF and v in cn_of_rs_cap_VF:
					T[edge_rs].add(edge_uv)
			cn_of_uv_cap_VF = [n for n in self.get_combined_neighborhood(H,[u,v]) if n in V_F]
			for x in cn_of_uv_cap_VF:
				if (u,x) in F_prime:
					for e in [e for e in T[(u,x)] if v in e]:
						T[(u,x)].discard(e)
				if (v,x) in F_prime:
					for e in [e for e in T[(v,x)] if u in e]:
						T[(v,x)].discard(e)
			F_prime.remove(edge_uv)
			H.remove_edges_from([edge_uv])
			edge_uv = self.get_removeable_edge(F_prime, T, randomized)
		self.edges_of_triangulation = F_prime
		
		if self.H == None:
			self.H = H
		return F_prime
		
	def get_possible_triangulation_edges(self, G):
		'''
		Computes set of edges that are possible chord edges, ie
		all edges between nodes that are part of a cycle and that are not contained in G
		
		Args:
			G : a graph in networkx format

		Returns:
			F : a set of edges s.t. no edge from F is in G and every cycle in G is a clique in G + F
		'''
		cycle_nodes = list(set([n for c in nx.cycle_basis(self.G) for n in c]))
		F = []
		for i in range(len(cycle_nodes)):
			for j in range(i+1, len(cycle_nodes)):
				chord_edge = (cycle_nodes[i], cycle_nodes[j])
				if chord_edge not in self.G.edges():
					F.append(chord_edge)
		return F
		
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

	def get_removeable_edge(self, F, T, randomized):
		'''
		Finds and returns an edge e form the set F with T[e] = {}
		
		Args:
			F : A set of edges
			T : The dictionary that tracks removeability for all edges
			randomized : if set to True, in each iteration the next removeable edge is chosen randomly.
							Otherwise, the first edge of F that satisfies the requirements is returned.
		
		Return:
			A removeable edge (i.e. T[e] is empty), if one exists. Otherwise None.
		
		'''
		logging.info("=== CMT.get_removeable_edge ===")
		
		removeable_edges = [e for e in F if len(T[e]) == 0]
		logging.debug("Number of removable edges: "+str(len(removeable_edges)))
		if len(removeable_edges) > 0:
			if not randomized:
				return removeable_edges[0]
			else:
				return random.choice(removeable_edges)
		else:
			return None

	def get_combined_neighborhood(self, G, V):
		'''
		Computes the combined neighborhood of V in G, that is:
			NC(V) = {w in V(G) | exists v in V: w in N(w) and not w in V}
		'''
		NC = []

		for v in V:
			NC += [n for n in G.neighbors(v) if n not in NC]

		return NC