#!usr/bin/python
# -*- coding: utf-8 -*-

import logging

import random
import networkx as nx

import TriangulationAlgorithm as ta

class Algorithm_FMT(ta.TriangulationAlgorithm):
	def __init__(self, G):
		logging.info("=== FMT.Algorithm_FMT.init ===")
		super().__init__(G)

	def run(self):
		self.triangulate(self.G)

	def get_alpha(self):
		return self.alpha

	def get_triangulated(self):
		return self.H

	def triangulate(self):
		'''
		Implementation of the algorithm FMT (Fast Minimal Triangulation)
			Heggernes, Telle, Villanger: Computing minimal triangulations in time O(n^alpha log n) = o(n^2.376)
			https://www.researchgate.net/publication/228637910_Computing_minimal_triangulations_in_time_O_n_a_log_n_o_n_2376
		to construct a minimal triangulation G_prime
		
		Args:
			G : a graph in netwokx format
		
		Returns:
			G_prime : a minimal triangulation of G.
		'''
		logging.info("=== triangulate_FMT ===")
		
		Q1 = [self.G]
		Q2 = []
		Q3 = []
		
		G_prime = self.G.copy()
		finished = False
		while not finished:
			# construct a zero matrix M with a row for each vertec in V:
			M = {v : [] for v in G.nodes()}
			while len(Q1) > 0:
				H = Q1.pop(0)
				A = self.partition(H)
				Q3.append(A)
				# consider the subgraph H(U\A):
				U_minus_A = [n for n in H.nodes() if n not in A]
				H_sub = H.subgraph(U_minus_A)
				components_of_H_sub = list(nx.connected_component_subgraphs(H_sub))
				for c in components_of_H_sub:
					
		
			if len(Q1) > 0:
				finished = True
				
	def partition(self, H):
		'''
		Args:
			H : A graph H = (U,D) (a subproblem popped from Q1)
		Returns:
			A subset A of U such that either A = N[K] for some connected H(K) or A is a pmc of H (and G_prime)
		'''
		
		# INITIALIZATION:
		# construct H_bar: the inverse graph of H
		H_bar = nx.complete_graph(len(H.nodes()))
		H_bar.remove_edges_from(H.edges())
		
		epsilon_limit = (2.0/5.0)*(len(H_bar.edges()))
		
		# PART 1:
		mark = {v: "unmarked" for v in H.nodes()}
		k = 1
		unmarked_nodes = [v for v in H.nodes() if mark[v] == "unmarked"]
		node_associations = {}
		C = [[]]
		while len(unmarked_nodes) > 0:
			u = unmarked_nodes[0]
			neighbors_of_u = [n for n in H.neighbors(u)]
			espilon_Hbar_u = sum([len(H_bar.neighbors(v)) for v in H.nodes() if v not in neighbors_of_u])
			if espilon_Hbar < epsilon_limit:
				mark[u] = "stop_vertex"
			else:
				C.append(Set([u]))
				mark[u] = "component_vertex"
				neighbors_of_Ck = Set()
				for v in C[k]:
					for n in H.neighbors(v):
						if n not in C[k]:
							neighbors_of_Ck.add(n)
				restricted_neighbors_of_Ck = [n for n in neighbors_of_Ck if mark[n] == "unmarked" or mark[n] == "stop_vertex"]
				while len(restricted_neighbors_of_Ck) > 0:
					v = restricted_neighbors_of_Ck[0]
					adp_neighbors_of_Ck = neighbors_of_Ck
					adp_neighbors_of_Ck.union(Set([n for n in H.neighbors(v)]))
					espilon_Hbar_Ck = sum([len(H_bar.neighbors(v)) for v in H.nodes() if v not in adp_rest_neighbors_of_Ck])
					if espilon_Hbar_Ck >= epsilon_limit:
						C[k].add(v)
						mark[v] = "component_vertex"
					else:
						mark[v] = "pmc_vertex"
						# associate v with Ck:
						node_associations[v] = k
			k += 1
		P = [v for v in H.nodes() if mark[v] == "pmc_vertex" or mark[v] == "stop_vertex"]
		
		# PART 2:
		A = []
		U_minus_P = [v for v in H.nodes() if not u in P]
		H_sub = H.subgraph(U_minus_P)
		components_of_H_sub = list(nx.connected_component_subgraphs(H_sub))
		# assume "full component" means "clique"
		H_sub_has_full_component = False
		C_full = None
		for c in components_of_H_sub:
			c_n = len(c.nodes())
			c_m = len(c.edges())
			if (c_m == c_n*(c_n-1)/2):
				H_sub_has_full_component = True
				C_full = c
		if H_sub_has_full_component:
			neighbots_of_C_full = Set()
			for n in C_full:
				neighbors_of_n = H.neighbors(n)
				neighbots_of_C_full.union(Set([u for u in H if u in neighbors_of_n]))
			A = list(neighbots_of_C_full)
		else:
			p_vertices = [v for v in H.nodes() if mark[v] == "pmc_vertex"]
			s_vertices = [v for v in H.nodes() if mark[v] == "stop_vertex"]
			
			# condition 1: there exist two non-adjacent vertices u, v such that u is s-vertex and v is s- or p-vertex
			cond_1 = False
			result_u = None
			i = 0
			while not cond_1 and i < len(H.nodes()):
				j = i+1
				while not cond_1 and j < len(H.nodes()):
					u = H.nodes()[i]
					v = H.nodes()[j]
					if u not in H.neighbors(v):
						if mark[u] == "stop_vertex" or mark[u] == "pmc_vertex":
							cond_1 = True
							result_u = u
					j += 1
				i += 1
			if cond_1:
				A = H.neighbors(result_u)
				
			else:
				# condition 2: there exits two non-adjacent vertices u, v where u is associated with C_i and v is associated with C_j and u is not in N[C_j] and v is not in N[C_i]
				cond_2 = False
				result_Ciu = None
				
				n_i = 0
				while not cond_2 and n_i < len(H.nodes()):
					n_j = n_i+1
					while not cond_2 and n_j < len(H.nodes()):
						u = H.nodes()[i]
						v = H.nodes()[j]
						if u in node_associations and v in node_associations:
							C_i = C[node_associations[u]]
							C_j = C[node_associations[v]]
							neighbors_of_Ci = Set()
							for n in C_i:
								neighbors_of_n = H.neighbors(n)		
								neighbors_of_Ci.union(Set([w for w in H if w in neighbors_of_n]))
							neighbors_of_Cj = Set()
							for n in C_j:
								neighbors_of_n = H.neighbors(n)		
								neighbors_of_Cj.union(Set([w for w in H if w in neighbors_of_n]))
							if u not in neighbors_of_Cj and v not in neighbors_of_Ci:
								cond_2 = True
								result_Ciu = C_i
								result_Ciu.append(u)
								
				if cond_2:
					neighbors_of_Ciu = Set()
					for n in result_Ciu:
						neighbors_of_n = H.neighbors(n)			
						neighbors_of_Ciu.union(Set([w for w in H if w in neighbors_of_n]))
					A = list(neighbors_of_Ciu)
				else:
					A = P
	
		return A