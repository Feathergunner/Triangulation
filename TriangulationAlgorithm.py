#!usr/bin/python
# -*- coding: utf-8 -*-

import logging

import networkx as nx
import matplotlib.pyplot as plt

import graph_meta as gm

class TriangulationNotSuccessfulException(Exception):
	'''
	Custom error type that gets thrown
	when an internal check yields that the graph resulting from a trianguliation
	is somehow not chordal.
	'''

class TriangulationAlgorithm:
	'''
	Superclass for all triangulation algorithms

	Args:
		G : the graph to triangulate

	Attributes:
		G : the original graph
		H : the triangulated graph
		edges_of_triangulation = the set of edges that are added to G to achieve H
	'''
	def __init__(self, G, parameters={}):
		self.G = G
		self.parameters = parameters
		self.H = None
		self.edges_of_triangulation = []

	def run(self):
		pass

	def get_triangulation_edges(self):
		return self.edges_of_triangulation

	def get_triangulation_size(self):
		return len(self.edges_of_triangulation)

	def draw_triangulation(self):
		edges_original = self.G.edges()
		self.G.add_edges_from(self.edges_of_triangulation)

		pos = nx.shell_layout(self.G)
		nx.draw_networkx_nodes(self.G, pos, node_color='r', node_size=50)
		nx.draw_networkx_edges(self.G, pos, edgelist=edges_original, width=1, edge_color='black')
		nx.draw_networkx_edges(self.G, pos, edgelist=self.edges_of_triangulation, width=1, edge_color='blue')

		labels = {}
		for n in self.G.nodes():
			labels[n] = n
		nx.draw_networkx_labels(self.G, pos, labels, font_size=16)
		plt.axis('off')
		plt.show()
		