#!usr/bin/python
# -*- coding: utf-8 -*-

import logging

import networkx as nx
import matplotlib.pyplot as plt

import graph_meta as gm

class TriangulationAlgorithm:
	'''
	Superclass for all triangulation algorithms
	'''
	def __init__(self, G):
		self.G = G
		self.edges_of_triangulation = []
		#self.size_of_triangulation = -1

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
		for n in G:
			labels[n] = n
		nx.draw_networkx_labels(G, pos, labels, font_size=16)
		plt.axis('off')
		plt.show()
		