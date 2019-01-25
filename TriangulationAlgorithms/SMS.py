#!usr/bin/python
# -*- coding: utf-8 -*-

import logging

import networkx as nx
import random
import numpy as np

from TriangulationAlgorithms import TriangulationAlgorithm as ta

def triangulate_SMS(G, randomized=False, repetitions=1):
	algo = Algorithm_SMS(G)
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
	
class Algorithm_SMS(ta.TriangulationAlgorithm):
	def __init__(self, G):
		logging.info("=== SMS.Algorithm_SMS.init ===")
		super().__init__(G)

	def run(self):
		self.triangulate()
		
	def run_randomized(self):
		self.triangulate(randomized=True)

	def triangulate(self, randomized=False):
		'''
		Implementation of the algorithm SMS (Saturate Minimal Seperators)
		to construct a minimal triangulation G_prime
		
		Args:
			G : a graph in netwokx format
		
		Returns:
			G_prime : a minimal triangulation of G.
		'''
		logging.info("=== triangulate_SMS ===")
		
		G_prime = self.G.copy()
		finished = False
		while not finished:
			logging.debug("Next iteration")
			logging.debug("edges of G_prime: "+str(G_prime.edges()))
			separator = self.get_minimal_separator(G_prime, randomized=randomized)
			if separator == None:
				finished = True
			else:
				edges_to_add = []
				logging.debug("saturate separator "+str(separator))
				for i_u in range(len(separator)):
					for i_v in range(i_u+1, len(separator)):
						logging.debug("saturate pair "+str(separator[i_u])+","+str(separator[i_v]))
						if not G_prime.has_edge(separator[i_u], separator[i_v]):
							edges_to_add.append((separator[i_u], separator[i_v]))
							self.edges_of_triangulation.append((separator[i_u], separator[i_v]))
				G_prime.add_edges_from(edges_to_add)
		self.H = G_prime
		return G_prime
			
	def get_minimal_separator(self, G, randomized=False):
		'''
		Searches for a minimal separator in G that is not a clique
			
		see https://cstheory.stackexchange.com/questions/29464/algorithms-for-computing-the-minimal-vertex-separator-of-a-graph
		
		Args:
			randomized : if true, the order in which the nodes are processed gets shuffled (not yet implemented)
		
		Return:
			S : a set of nodes that form a minimal separator of G, if such a set exists that is not a clique. If every minimal separator of G is a clique, returns None
		'''
		logging.info("=== get_minimal_separator ===")
		
		node_processing_order = [n for n in G.nodes()]
		if randomized:
			random.shuffle(node_processing_order)
		for i in range(len(node_processing_order)):
			u = list(G.nodes())[i]
			neighbors_of_u = list(G.neighbors(u))#[n for n in ]
			for v in node_processing_order[i+1:]:
				logging.debug("Consider pair: "+str(u)+", "+str(v))
				# construct S as set of all nodes that are neighbors of u and reachable from v:
				S = []
				marked = {n : False for n in G.nodes()}
				if v in neighbors_of_u:
					logging.debug(str(u)+" and "+str(v)+" are adjacent, no separator exists")
				else:
					bfs_stack = [v]
					marked[v] = True
					while not len(bfs_stack) == 0:
						w = bfs_stack.pop(0)
						for n in G.neighbors(w):
							if not marked[n]:
								marked[n] = True
								if n in neighbors_of_u:
									logging.debug("Add "+str(n)+" to separator set")
									S.append(n)
								else:
									bfs_stack.append(n)
					logging.debug("Seperator: "+str(S))
				if len(S) > 1:
					S_graph = G.subgraph(S)
					logging.debug(S_graph.nodes())
					logging.debug(S_graph.edges())
					if len(S_graph.edges()) < (len(S)*(len(S)-1))/2:
						logging.debug(str(S) + " is a minimal seperator of G")
						return S
					else:
						logging.debug(str(S) + " is a clique")
		logging.debug("No non-clique minimal seperator of G found")
		return None
		