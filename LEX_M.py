#!usr/bin/python
# -*- coding: utf-8 -*-

import logging

import random
import networkx as nx

'''
class LEX_M:
	def __init__(self, G):
		self.G = G
		self.alpha = {}
		self.H = tri
		self.triangulate_LEX_M(G)

	def get_alpha(self):
		return self.alpha

	def get_triangulated(self):
		return self.H
'''

def triangulate_LEX_M(G, randomize=False):
	'''
	Implementation of LEX M Algorithm 
		Rose, Tarjan, Lueker: Algorithmic Aspects of Vertex Elimination on Graphs
		https://epubs.siam.org/doi/abs/10.1137/0205021
	to construct a minimal elemination ordering alpha of a graph G
	and the corresponding minimal triangulation H(G, alpha)
	
	Args:
		G : a graph in netwokx format
		randomize : if set to True, the order in which the nodes are processed is randomized
	
	Returns:
		H : a minimal triangulation of G.
		alpha : the corresponding minimal elimination ordering of G 
	'''
	
	logging.info("=== triangulate_LEX_M ===")
	
	nodelabels = {node : [] for node in G}
	F = []
	alpha = {}
	n = len(G)
	for i in range(n,0, -1):
		logging.debug("Iteration: "+str(i))
		node_v = get_maxlex_node(G, alpha, nodelabels, randomize)
		logging.debug("max lex node: "+str(node_v))
		alpha[node_v] = i
		S = []
		all_unnumbered_vertices = [n for n in G if n not in alpha]
		if randomize:
			random.shuffle(all_unnumbered_vertices)
		logging.debug("all unnumbered nodes:")
		logging.debug([str(n)+": "+str(nodelabels[n]) for n in all_unnumbered_vertices])
		for node_u in all_unnumbered_vertices:
			smallerlex_nodes = [n for n in all_unnumbered_vertices if list_lexicographic_is_less_than(nodelabels[n], nodelabels[node_u])]+[node_v, node_u]
			logging.debug("start Node "+str(node_v)+" label: "+str(nodelabels[node_v]))
			logging.debug("target Node "+str(node_u)+" label: "+str(nodelabels[node_u]))
			#print ("Node labels of smallerlex_nodes: ")
			#for n in smallerlex_nodes:
				#print (str(n)+" : "+str(nodelabels[n]))
			if nx.has_path(G.subgraph(smallerlex_nodes),node_v, node_u):
				logging.debug("Add target node "+str(node_u)+" to set S")
				S.append(node_u)
		for node_u in S:
			nodelabels[node_u].append(i)
			if (node_v, node_u) not in G.edges:
				F.append((node_v, node_u))
				logging.debug("added edge: "+str((node_v, node_u)))
		logging.debug("End of iteration. all node labels:")
		logging.debug([str(n)+": "+str(nodelabels[n]) for n in G])		
	
	G.add_edges_from(F)
	if not nx.is_chordal(G):
		logging.error("Resulting graph is somehow not chordal!")
		return None
	return G#, alpha
	
def get_maxlex_node(G, alpha, nodelabels, randomize=False):
	'''
	Get an unnumbered vertex v of lexicograpohically maximum label from G

	Args:
		G : a graph in networkx format
		alpha : a dictionary of node numbers
		nodelabels : a dictionary of node labels
		randomize : if set to True and if there are multiple nodes with the max lex. label, one of these is returned at random

	Returns:
		v : an unnumbered vertex v of lexicograpohically maximum label from G
	'''
	
	logging.info("=== get_maxlex_node ===")
	
	current_max_label = ''
	current_best_node = None
	nodes = [n for n in G]
	if randomize:
		random.shuffle(nodes)
	for node in G: 
		if (node not in alpha) and ((current_best_node == None) or (list_lexicographic_is_less_than(current_max_label, nodelabels[node]))):
			current_best_node = node
			current_max_label = nodelabels[node]
	return current_best_node

def list_lexicographic_is_less_than(list_1, list_2):
	'''
	computes a lexicographic ordering relation of two lists
	if list_1 < list_2 returns True
	otherwise false
	
	Args:
		list_1 : a list of integers
		list_2 : a list of integers

	Return:
		True, if list_1 < list_2 as defined above, otherwise False
	'''
	#logging.info("=== list_lexicographic_is_less_than ===")
	
	n = min(len(list_1), len(list_2))
	for i in range(n):
		if list_1[i] < list_2[i]:
			return True
		elif list_1[i] > list_2[i]:
			return False
	if len(list_1) < len(list_2):
		return True
	elif len(list_1) > len(list_2):
		return False
	return False