#!usr/bin/python
# -*- coding: utf-8 -*-

import logging

import networkx as nx

class Cycle:
	def __init__(self, cyclenodes):
		# the order of the nodes of the cycle is rotated s.t. the cycle starts with the minimum node:
		min_node = min(cyclenodes)
		min_index = cyclenodes.index(min_node)
		self.cyclenodes = []
		for i in range(len(cyclenodes)):
			self.cyclenodes.append(cyclenodes[(i+min_index)%len(cyclenodes)])

	def __str__(self):
		return str(self.cyclenodes)	

	def __len__(self):
		return len(self.cyclenodes)

	def __getitem__(self, key):
		return self.cyclenodes[key]

	def __contains__(self, key):
		return key in self.cyclenodes

	def __hash__(self):
		return hash(str(self.cyclenodes))
		
	def __eq__(self, other):
		# we can simply use the hash-values to compare cycles
		return hash(str(self.cyclenodes)) == hash(str(other.cyclenodes))

def get_post_order(T, root=None):
	'''
	Get the post-order of the nodes of a tree
	running time in O(n), since each edge and each node is considered at most twice

	Args:
		T: a tree-graph in networkx format

	Return:
		post_order: a dictionary that maps each each node of T conform to a post-ordering-index
	'''
	
	logging.info("=== get_post_order ===")

	post_order = {}
	stack = []
	
	if root == None:
		root = T.nodes[1]
	
	stack.append(root)
	current_index = len(T.nodes())
	while len(stack) > 0:
		current_node = stack.pop()
		post_order[current_node] = current_index
		current_index -= 1
		for neighbor in G.neighbors(current_node):
			if neighbor not in post_order:
				stack.append(neighbor)
				
	return post_order
	
def get_maxlabel_neighborsets(G, labels):
	'''
	Construct vertex sets V_1,..., V_n, where V_i is the subset of the closed neighborhood of v_i
	with label(n) <= label(v_i) for all n in V_i.

	Args:
		G : a graph in netwokx format
		labels : a dictionary that contains labels for the nodes in G

	Return:
		vertexsets : a dictionary that maps each index i=1,...,n to the corresponding list of nodes V_1, ..., V_n
	'''
	logging.info("=== get_maxlabel_neighborsets ===")
	
	vertexsets = {}
	nodes_ordered_by_label = sorted([n for n in G.nodes()], key=lambda x: labels[x])
	n = len(G.nodes())
	for i in range(n,0,-1):
		current_node = nodes_ordered_by_label[n-i]
		vertexsets[i] = G.neighbors(current_node)
		vertexsets[i].append(current_node)
		G.remove_nodes_from(vertexsets[i])
		
	return vertexsets
	
def compute_perfect_elimination_ordering_planar(G):
	'''
	Compute a perfect elimination ordering of the nodes of a planar graph G
	see: Dahlhaus: An Improved Linear Time Algorithm for Minimal Elimination Ordering in Planar Graphs (1999)

	Args:
		G : a graph in networkx format

	Return:
		perfect_elimination_ordering : a dict mapping each node of G to its position in a perfect elimination ordering
	'''
	if not nx.check_planarity(G):
		logging.error("Input graph is not planar!")
		return None
		
	## TO DO
	
	perfect_elimination_ordering = {}
	i = 0
	for n in G.nodes():
		perfect_elimination_ordering[n] = i
		i += 1
	return perfect_elimination_ordering

def LEX_BFS(G):
	'''
	LEXICOGRAPHIC BFS
	If the input graph is chordal, this computes a perfect elimination ordering of G

	Args:
		G : a graph in networkx format

	Return:
		lex_bfs_order : a dict mapping each node to its position defined by the LEX-BFS
	'''
	
	logging.info("=== LEX_BFS ===")
	
	# initialize sigma to contain single set containing all vertices of G:
	sigma = [[n for n in G]]
	# initialize output to be empty:
	out = []
	while len(sigma) > 0:
		# chose a random node from the first set of sigma:
		node_v = sigma[0].pop()
		if len(sigma[0]) == 0:
			sigma.pop()
		out.append(node_v)
		i = 0
		while i < len(sigma):
			# split each set in sigma into neighbors and non-neighbors of v:
			S = sigma.pop(i)
			S_adj = [n for n in S if n in G.neighbors(node_v)]
			S_nonadj = [n for n in S if n not in S_adj]
			if len(S_adj) > 0:
				sigma.insert(i, S_adj)
				i += 1
			if len(S_nonadj) > 0:
				sigma.insert(i, S_nonadj)
				i += 1
	return {out[i]: i for i in range(len(out))}

def get_all_cycles(G, min_cycle_length=4, only_base_cycles=True):
	'''
	Constructs a list of all cycles of a minimum length of a graph G
	Args:
		G : a graph in networkx format
		min_cycle_length : the minimum length of cycles that are considered
		only_base_cycles : if true, this method returns only chordless cycles. Otherwise, all cycles will be returned
	'''
	logging.info("=== MT_MinimumTriangulation.get_all_cycles ===")
	# use depth-first-search at each node
	startnode = [n for n in G.nodes][0]
	all_cycles = get_all_cycles_single_startnode(G, startnode, min_cycle_length, only_base_cycles)
	'''
	for node in G:
		newcycles = get_all_cycles_single_startnode(G, node, min_cycle_length, only_base_cycles)
		for cycle in newcycles:
			if cycle not in all_cycles:
				all_cycles.append(cycle)
		break
	'''
	return all_cycles

def get_all_cycles_single_startnode(G, startnode, min_cycle_length=4, only_base_cycles=True):
	'''
	Performs a DFS (depth-first-search) from a specific starting node and adds all new found cycles to the data structure
	Args:
		startnode : the starting node for the DFS
		min_cycle_length : the minimum length of cycles that are considered
		only_base_cycles : if true, this method returns only chordless cycles. Otherwise, all cycles will be returned
	Return:
		returns the number of added cycles
	'''
	logging.info("=== MT_MinimumTriangulation.get_all_cycles_single_startnode ===")
	logging.debug("Considering start node "+str(startnode))

	logging.debug("Graph "+str(G.edges()))

	cycles = []
	visited = {n : 0 for n in G}
	visited[startnode] = 1
	predecessors = {}
	successors = {n : [] for n in G}
	predecessors[startnode] = None
	current_dfs_node = startnode		
	number_of_added_cycles = 0
	while not current_dfs_node == None:
		logging.debug("Current node: "+str(current_dfs_node))
		visited_neighbors = [n for n in G.neighbors(current_dfs_node) if visited[n] == 1]
		logging.debug("visited neighbors: "+str(visited_neighbors))
		for node in visited_neighbors:
			# add new cycle
			cycle = []
			current_cycle_node = current_dfs_node
			while not current_cycle_node == node:
				cycle.append(current_cycle_node)
				current_cycle_node = predecessors[current_cycle_node]
			cycle.append(current_cycle_node)
			if len(cycle) >= min_cycle_length:
				logging.debug("Found a cycle of length > 3")
				logging.debug(str(cycle))
				add_this_cycle = True
				if only_base_cycles:
					subgraph = G.subgraph(cycle)
					if len(subgraph.edges()) > len(cycle):
						add_this_cycle = False
						logging.debug("Cycle contains a chord!")
				if add_this_cycle:
					new_cycle = Cycle(cycle)
					logging.debug("Cycle: "+str(new_cycle))
					if new_cycle not in cycles:
						logging.debug("Cycle is new!")
						cycles.append(new_cycle)
						number_of_added_cycles += 1
					else:
						logging.debug("Cycle already exists!")
		unvisited_neighbors = [n for n in G.neighbors(current_dfs_node) if (visited[n] == 0) or (visited[n] == 2 and not n in successors[current_dfs_node])]
		logging.debug("unvisited neighbors: " +str(unvisited_neighbors))
		logging.debug("visited successor: "+str([n for n in G.neighbors(current_dfs_node) if visited[n] == 2 and n in successors[current_dfs_node]]))
		if len(unvisited_neighbors) > 0:
			visited[current_dfs_node] = 1
			neighbor = unvisited_neighbors[0]
			predecessors[neighbor] = current_dfs_node
			successors[current_dfs_node].append(neighbor)
			current_dfs_node = neighbor
		else:
			visited[current_dfs_node] = 2
			#successors[current_dfs_node] = []
			successors[current_dfs_node] = []
			current_dfs_node = predecessors[current_dfs_node]
			
	return cycles
	
def get_all_cycle_from_cycle_basis(G, min_cycle_length=4):
	bcc = Basic_Cycle_Constructor(G)
	cycles = bcc.get_all_cycles_from_cyclebasis()
	return cycles
	
class Basic_Cycle_Constructor:
	def __init__(self, G):
		logging.debug("=== Basic_Cycle_Constructor.init ===")
		self.G = G
		self.edges = [e for e in self.G.edges()]
		#logging.debug(self.G.nodes())
		logging.debug("edges: "+str(self.edges))
		self.cycle_basis = [c for c in nx.cycle_basis(self.G)]
		logging.debug("cycle_basis: "+str([str(c) for c in self.cycle_basis]))
		cycle_basis_edges = [self.cycle_node_to_edges(c) for c in self.cycle_basis]
		#logging.debug("cycle_basis_edges: "+str(cycle_basis_edges))
		self.cycle_basis_binaries = [self.cycle_edges_to_binary(c) for c in cycle_basis_edges]
		self.cycle_edge_graph = self.construct_cycle_edge_graph()
		self.all_cycles = self.compute_all_cycles_from_cyclebasis()
	
	def cycle_node_to_edges(self, cycle):
		edges = []
		for i in range(len(cycle)):
			edges.append((cycle[i], cycle[(i+1)%len(cycle)]))
		return edges
		
	def cycle_edges_to_binary(self, cycle):
		logging.info("=== Basis_Cycle_Constructor.cycle_edges_to_binary ===")
		logging.debug("cycle: "+str(cycle))
		binary = 0
		index = 0
		for edge in self.edges:
			#logging.debug("Check edge: "+str(edge))
			if edge in cycle or (edge[1], edge[0]) in cycle:
				binary += 2**index
			index += 1
		logging.debug("Binary representation for cycle "+str(cycle)+" : "+str(binary))
		return binary
		
	def binary_to_cycle_edges(self, binary):
		cycle_edge_indices = []
		for i in range(len(self.edges)):
			if binary & 2**i > 0:
				cycle_edge_indices.append(i)
		logging.debug("cycle_edge_indices: "+str(cycle_edge_indices))
		cycle_edges = [self.edges[i] for i in cycle_edge_indices]
		logging.debug(str([str(e) for e in cycle_edges]))
		return cycle_edges
		
	def construct_cycle_edge_graph(self):
		'''
		Constructs a graph that has a node for each cycle of the cycle basis of in the original graph,
		and an edge between two nodes if the corresponding cycles have a common edge.
		This datastructure is used to determine if a set ob base cycles is connected
		'''
		logging.info("=== Basis_Cycle_Constructor.construct_cycle_edge_graph ===")
		V = [i for i in range(len(self.cycle_basis))]
		E = []
		for i in range(len(self.cycle_basis)):
			for j in range(i+1, len(self.cycle_basis)):
				if self.cycle_basis_binaries[i] & self.cycle_basis_binaries[j] > 0:
					E.append((i,j))
		cycle_edge_graph = nx.Graph()
		cycle_edge_graph.add_nodes_from(V)
		cycle_edge_graph.add_edges_from(E)
		return cycle_edge_graph
	
	def compute_all_cycles_from_cyclebasis(self):
		logging.info("=== Basis_Cycle_Constructor.get_all_cycles_from_cyclebasis ===")
	
		all_cycles_edges = []
		# iterate through all possible subsets of cycles from the cycle basis:
		number_of_subsets = 2**len(self.cycle_basis)
		for i in range(number_of_subsets):
			# get next subset:
			this_iteration_cyclesubset = []
			for j in range(len(self.cycle_basis)):
				# check next cycle:
				if 2**j & i > 0:
					this_iteration_cyclesubset.append(j)
			# check if subset is not trivial
			if len(this_iteration_cyclesubset) > 1:
				# check if subset is not disjunct:
				cycle_subgraph = self.cycle_edge_graph.subgraph(this_iteration_cyclesubset)
				if nx.is_connected(cycle_subgraph):
					# construct binary representation of new cycle:
					combined_cycle_binary = self.cycle_basis_binaries[this_iteration_cyclesubset[0]]
					for j in range(1,len(this_iteration_cyclesubset)):
						combined_cycle_binary = combined_cycle_binary^self.cycle_basis_binaries[this_iteration_cyclesubset[j]]
						
					# decode binary to set of edges:
					new_cycle = self.binary_to_cycle_edges(combined_cycle_binary)
					all_cycles_edges.append(new_cycle)
		
		# decode cycles from sets of edges to sets of nodes
		all_cycles = []
		for cycle_edges in all_cycles_edges:
			used_edges = [False for e in cycle_edges]
			cycle_nodes = [cycle_edges[0][0], cycle_edges[0][1]]
			used_edges[0] = True
			for i in range(1, len(cycle_edges)-1):
				for j in range(len(cycle_edges)):
					if not used_edges[j]:
						if cycle_edges[j][0] == cycle_nodes[-1]:
							cycle_nodes.append(cycle_edges[j][1])
							used_edges[j] = True
							break
						elif cycle_edges[j][1] == cycle_nodes[-1]:
							cycle_nodes.append(cycle_edges[j][0])
							used_edges[j] = True
							break
			all_cycles.append(cycle_nodes)
		
		return all_cycles+self.cycle_basis
		
	def get_all_cycles_from_cyclebasis(self, min_cycle_length=4, only_base_cycles=True):
		cycles = []
		for cycle in self.all_cycles:
			if len(cycle) >= min_cycle_length:
				add_this_cycle = True
				if only_base_cycles:
					subgraph = self.G.subgraph(cycle)
					if len(subgraph.edges()) > len(cycle):
						add_this_cycle = False
				if add_this_cycle:
					cycles.append(cycle)
		return cycles