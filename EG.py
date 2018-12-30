#!usr/bin/python
# -*- coding: utf-8 -*-

import logging

import networkx as nx

import TriangulationAlgorithm as ta

def elimination_game(G, n=None):
	aeg = Algorithm_EliminationGame(G)
	return aeg.run()
	
def evaluate_elimination_game(G, n=None):
	aeg = Algorithm_EliminationGame(G)
	aeg.run()
	return len(aeg.edges_of_triangulation)

class Algorithm_EliminationGame(ta.TriangulationAlgorithm):
	def __init__(self, G):
		self.G = G
		
	def run(self):
		self.elimination_game_triangulation(self.G)
	
	def elimination_game_triangulation(self, G, alpha=None):
		'''
		The elimination game algorithm for computing a triangulation algorithm
		
		Args:
			G : the input graph in networkx format
	
		Returns:
			H : a graph in networkx format, which is a triangulation of G
		'''
		logging.info("=== elimination_game_triangulation ===")
		logging.debug("Alpha: "+str(alpha))
		if alpha == None:
			all_nodes = [n for n in G]
		else:
			all_nodes = sorted([n for n in alpha.keys()], key=lambda x: alpha[x])
		edges_original = [e for e in G.edges()]
		edges_added = []
		for node in all_nodes:
			all_neighbors = [n for n in G.neighbors(node)]
			for i in range(0, len(all_neighbors)):
				for j in range(i+1, len(all_neighbors)):
					edge_between_neighbors = (all_neighbors[i], all_neighbors[j])
					if edge_between_neighbors not in G.edges():
						G.add_edges_from([edge_between_neighbors])
						edges_added.append(edge_between_neighbors)
						logging.debug("Added edge: "+str(edge_between_neighbors))
			G.remove_node(node)
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