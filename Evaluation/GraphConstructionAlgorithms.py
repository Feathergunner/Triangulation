#!usr/bin/python
# -*- coding: utf-8 -*-

import networkx as nx
import random
import logging
import math

class TooManyEdgesException(Exception):
	'''
	Custom error type that gets thrown from algorithms that construct planar graphs.
	Gets thrown when the specified number of edges is too large s.t. no planar graph can be constructed
	'''
	
class TooManyIterationsException(Exception):
	'''
	Custom Exception that gets thrown when after a significant number of iterations no planar graph has been found
	If n is small and m is large, the probability that a random er graph is planar is small

	The number of edges in the produced graph might be larger than required, because connectivity is enforced.
	'''

class NoEdgesLeftException(Exception):
	'''
	Custom Exception that gets thrown if during construction a maximum planar graph is constructed, but it contains less than the required number of edges
	'''

class WrongNetworkxVersion(Exception):
	'''
	Custom Exception that gets thrown if the installed version of networkx is below 2.2, because in these older versions check_planarity is not implemented.
	'''
	
class GraphGenerator:
	def construct_connected_er(self, n, p):
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
		#logging.info("=== construct_planar_er ===")
		
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
			try:
				is_planar = nx.check_planarity(G)[0]
			except AttributeError:
				raise WrongNetworkxVersion("Old version of networkx does not support planarity check")
			if is_planar:
				planar_graph_constructed = True

		if not planar_graph_constructed:
			raise TooManyIterationsException("Exceeded maximum number of iterations ("+str(max_number_of_iterations)+").")
			
		return self.ensure_connectivity(G)

	def construct_planar_random(self, n, p):
		'''
		Constructs a random planar graph with n nodes and m edges.
		Edges are introduced iteratively in batches. Each edge is chosen uniform from all possible remaining edges. A batch of edges is only added if the graph remains planar.
		Note that this algorithm differs significantly from the Erdös-Renyi random graph.
		'''
		#logging.info("=== construct_planar_random ===")
				
		m = int(p*n*(n-1)/2)
		
		if m > 3*n-6:
			# number of edges is too large: no planar graph possible
			raise TooManyEdgesException("Number of edges too large. No planar graph with these parameters can exist: n="+str(n)+", m="+str(m))

		G = nx.Graph()
		G.add_nodes_from([i for i in range(n)])

		edges_to_add = {(i,j) for i in range(n) for j in range(i+1,n)}
		
		batch_size = int(m/2)
		number_failed_attempts = 0
		while len(G.edges()) < m:
			#logging.debug ("edges to add:")
			#logging.debug (edges_to_add)
			if len(edges_to_add) == 0:
				raise NoEdgesLeftException("Graph is maximal planar: no more edges can be added.")
				
			current_batch_size = min((m - len(G.edges())), len(edges_to_add), batch_size)
			#logging.debug("Next iteration with batch size: "+str(current_batch_size))
			
			#while len(new_edges) < current_batch_size and len(edges_to_add) > 0:
			new_edges = random.sample(edges_to_add, current_batch_size)
			
			#logging.debug ("new edges:")
			#logging.debug (new_edges)
			G.add_edges_from(new_edges)
			
			try:
				is_planar = nx.check_planarity(G)[0]
			except AttributeError:
				raise WrongNetworkxVersion("Old version of networkx does not support planarity check")
				
			if not is_planar:
				#logging.debug("Graph is not planar after adding batch of edges.")
				G.remove_edges_from(new_edges)
				number_failed_attempts += 1
				if number_failed_attempts > 2 and batch_size > 1:
					#logging.debug("Decrease batch size.")
					batch_size = int(max(1, math.ceil(batch_size*0.5)))
					number_failed_attempts = 0
			else:
				for e in new_edges:
					#logging.debug ("remove edge "+str(e))
					edges_to_add.remove(e)

		return G

	def construct_random_max_degree(self, n, p, max_degree=4):
		V = [i for i in range(n)]
		E = []
		node_degrees = [0 for i in range(n)]
		for v in V:
			u = v+1
			while u < n and node_degrees[v] < max_degree:
				if node_degrees[u] < max_degree and random.random() < p:
					E.append((v,u))
					node_degrees[v] += 1
					node_degrees[u] += 1
				u += 1
		G = nx.Graph()
		G.add_nodes_from(V)
		G.add_edges_from(E)
		
		return G
	
	def construct_random_max_clique_size(self, n, p, max_clique_size=4):
		'''
		Construct a random graph conform to a maximum clique size.
		Note that the time complexity is exponential in the size of the maximum clique,
		i.e. only use to generate graphs with small maximum clique size.
		'''
		V = [i for i in range(n)]
		G = nx.Graph()
		G.add_nodes_from(V)
		adjacencies = {}
		for v in V:
			if v not in adjacencies:
				adjacencies[v] = []
			for u in range(v+1, n):
				if u not in adjacencies:
					adjacencies[u] = []
				if random.random() < p:
					# check for max clique if this edge gets inserted:
					common_neighbors = [n for n in V if n in adjacencies[v] and n in adjacencies[u]]
					if len(common_neighbors) < max_clique_size - 1:
						# large clique not possible
						# add edge
						G.add_edges_from([(v,u)])
						adjacencies[v].append(u)
						adjacencies[u].append(v)
					else:
						# check clique explicitly:
						# neighborhood:
						gn = G.subgraph(common_neighbors)
						max_neighbor_clique_size = max([len(c) for c in nx.find_cliques(gn)])
						if max_neighbor_clique_size < max_clique_size - 1:
							# with u,v new max clique is at most max_clique_size:
							# add edge
							G.add_edges_from([(v,u)])
							if v not in adjacencies:
								adjacencies[v] = []
							adjacencies[v].append(u)
							if u not in adjacencies:
								adjacencies[u] = []
							adjacencies[u].append(v)
		return G