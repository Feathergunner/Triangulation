#!usr/bin/python
# -*- coding: utf-8 -*-

import logging

import networkx as nx
import random
import numpy as np

from TriangulationAlgorithms import TriangulationAlgorithm as ta

def triangulate_EG(G, randomized=False, repeats=1):
	algo = Algorithm_EliminationGame(G)
	if not randomized:
		algo.run()
		return {
			"H" : algo.get_triangulated(),
			"size" : len(algo.get_triangulation_edges()),
			"mean" : len(algo.get_triangulation_edges()),
			"variance" : 0,
			"repeats" : 1
			}
	else:
		H_opt = None
		size_opt = None
		all_sizes = []
		for i in range(repeats):
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
			"repeats" : repeats
			}
	
class Algorithm_EliminationGame(ta.TriangulationAlgorithm):
	def __init__(self, G):
		logging.info("=== EG.Algorithm_EliminationGame.init ===")
		super().__init__(G)
		
	def run(self):
		self.elimination_game_triangulation(self.G)
		
	def run_randomized(self):
		self.elimination_game_triangulation(self.G, randomized=True)
	
	def elimination_game_triangulation(self, G, alpha=None, randomized=False):
		'''
		The elimination game algorithm for computing a triangulation algorithm
		
		Args:
			G : the input graph in networkx format
			alpha : an ordering of the nodes that defines the order in which the nodes are processed, as a dict {node: position}
			randomized : if no ordering alpha is specified and randomized is set to True, the order of the nodes is shuffled
	
		Returns:
			H : a graph in networkx format, which is a triangulation of G
		'''
		logging.info("=== elimination_game_triangulation ===")
		logging.debug("Alpha: "+str(alpha))
		
		if alpha == None:
			all_nodes = [n for n in G]
			if randomized:
				random.shuffle(all_nodes)
		else:
			all_nodes = sorted([n for n in alpha.keys()], key=lambda x: alpha[x])
		G_temp = G.copy()
		edges_original = [e for e in G_temp.edges()]
		edges_added = []
		for node in all_nodes:
			all_neighbors = [n for n in G_temp.neighbors(node)]
			for i in range(0, len(all_neighbors)):
				for j in range(i+1, len(all_neighbors)):
					edge_between_neighbors = (all_neighbors[i], all_neighbors[j])
					if edge_between_neighbors not in G_temp.edges():
						G_temp.add_edges_from([edge_between_neighbors])
						edges_added.append(edge_between_neighbors)
						logging.debug("Added edge: "+str(edge_between_neighbors))
			G_temp.remove_node(node)
			logging.debug("removed node: "+str(node))
		H = nx.Graph()
		H.add_nodes_from(all_nodes)
		H.add_edges_from(edges_original)
		H.add_edges_from(edges_added)
		self.edges_of_triangulation = edges_added
		self.H = H
	
		if not nx.is_chordal(H):
			raise TriangulationNotSuccessfulException("Resulting graph is somehow not chordal!")
		return H