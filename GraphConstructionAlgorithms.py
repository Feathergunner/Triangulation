#!usr/bin/python
# -*- coding: utf-8 -*-

import networkx as nx
import random

class TooManyEdgesException(Exception):
	'''
	Custom error type that gets thrown from algorithms that construct planar graphs.
	Gets thrown when the specified number of edges is too large s.t. no planar graph can be constructed
	'''

class GraphGenerator:
	def construct_conneted_er(self, n, p):
		'''
		Constructs a random graph that is guaranteed to be connected.
		At first, a random erdös-renyi-graph G is constructed. If G contains more than
		one connected component, each componted is connected to the first one by a random edge

		Note that this implies that there might be significantly more edges than 0.5*n(n-1)p.

		Args:
			n : the number of nodes of the constructed graph.
			p : the edge-probability as required by the erdös-renyi random graph model.

		Return:
			G : a random graph that is guaranteed to be connected.
		'''
		G = nx.erdos_renyi_graph(n,p)
		return self.ensure_connectivity(G)

	def ensure_connectivity(self, G):
		num_components = nx.number_connected_components(G)
		if num_components > 1:
			components = [c for c in nx.connected_components(G)]
			edges_to_add = []
			for i in range(1,num_components):
				edges_to_add.append((random.sample(components[0],1)[0], random.sample(components[i],1)[0]))
			G.add_edges_from(edges_to_add)
		return G

	def construct_planar_er(self, n, m, max_number_of_iterations=1000):
		'''
		Constructs random er-graphs until a planar graph is found.
		Note that for m < 3n, the probability that G is planar converges to 1 if n is large
		(citation needed)
		'''

		class TooManyIterationsException(Exception):
			'''
			Custom Exception that gets thrown when after a significant number of iterations no planar graph has been found
			If n is small and m is large, the probability that a random er graph is planar is small

			The number of edges in the produced graph might be larger than required, because connectivity is enforced.
			'''

		if m > 3*n-6:
			# number of edges is too large: no planar graph possible
			raise TooManyEdgesException("Number of edges too large. No planar graph with these parameters can exist.")
		p = (2.0*m)/(n*(n-1))

		planar_graph_constructed = False
		G = None
		iterations = 0
		while iterations < max_number_of_iterations and not planar_graph_constructed:
			iterations += 1
			G = nx.erdos_renyi_graph(n, p)
			if nx.check_planarity(G)[0]:
				planar_graph_constructed = True

		if not planar_graph_constructed:
			raise TooManyIterationsException("Exceeded maximum number of iterations ("+str(max_number_of_iterations)+").")
			
		return self.ensure_connectivity(G)

	def construct_planar_random(self, n, m):
		'''
		Constructs a random planar graph with n nodes and m edges.
		Edges are introduced iteratively. Each edge is chosen uniform from all possible remaining edges. The edge is only added if the graph remains planar.
		Note that this algorithm differs significantly from the Erdös-Renyi random graph.
		'''

		class NoEdgesLeftException(Exception):
			'''
			Custom Exception that gets thrown if during construction a maximum planar graph is constructed, but it contains less than the required number of edges
			'''

		if m > 3*n-6:
			# number of edges is too large: no planar graph possible
			raise TooManyEdgesException("Number of edges too large. No planar graph with these parameters can exist.")

		G = nx.Graph()
		G.add_nodes_from([i for i in range(n)])

		edges_to_add = {(i,j) for i in range(n) for j in range(i+1,n)}
		
		for i in range(m):
			found_edge_to_add = False
			while not found_edge_to_add:
				if len(edges_to_add) == 0:
					raise TooManyEdgesException("Graph is maximal planar: no more edges can be added.")

				new_edge = random.sample(edges_to_add, 1)[0]
				print (new_edge)
				G.add_edges_from([new_edge])
				if not nx.check_planarity(G)[0]:
					print ("Graph is not planar. remove this edge")
					G.remove_edges_from([new_edge])
				else:
					found_edge_to_add = True
				edges_to_add.remove(new_edge)

		return G