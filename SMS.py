#!usr/bin/python
# -*- coding: utf-8 -*-

import logging

import random
import networkx as nx

import TriangulationAlgorithm as ta

def evaluata_sms(G, parameters):
	sms = Algorithm_SMS(G)
	sms.run()
	return len(sms.edges_of_triangulation)

class Algorithm_SMS(ta.TriangulationAlgorithm):
	def __init__(self, G):
		logging.info("=== FMT.Algorithm_SMS.init ===")
		super().__init__(G)

	def run(self):
		self.triangulate()

	def get_alpha(self):
		return self.alpha

	def get_triangulated(self):
		return self.H

	def triangulate(self):
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
			separator = self.get_minimal_separator(G_prime)
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
		
		for u in range(len(G.nodes())):
			neighbors_of_u = [n for n in G.neighbors(u)]
			for v in range(u+1, len(G.nodes())):
				logging.debug("Consider pair: "+str(u)+", "+str(v))
				# construct S as set of all nodes that are neighbors of u and reachable from v:
				S = []
				marked = {n : False for n in G.nodes()}
				if v in neighbors_of_u:
					logging.debug(str(u)+" and "+str(v)+" are adjacent, no seperator exists")
				else:
					bfs_stack = [v]
					marked[v] = True
					while not len(bfs_stack) == 0:
						w = bfs_stack.pop(0)
						for n in G.neighbors(w):
							if not marked[n]:
								marked[n] = True
								if n in neighbors_of_u:
									S.append(n)
								else:
									bfs_stack.append(n)
				
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
		