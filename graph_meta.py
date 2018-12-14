#!usr/bin/python
# -*- coding: utf-8 -*-

import logging

class Cycle:
	def __init__(self, cyclenodes):
		self.cyclenodes = cyclenodes

	def __str__(self):
		return str(self.cyclenodes)	

	def __len__(self):
		return len(self.cyclenodes)

	def __getitem__(self, key):
		return self.cyclenodes[key]

	def __contains__(self, key):
		return key in self.cyclenodes

	def __hash__(self):
		# note that in case of comparability, the actual order of the nodes within the cycle does not matter
		# since the cycle-nodes and the edges of the graph define the cycle
		return hashable_from_set(self.cyclenodes)
		
	def __eq__(self, other):
		# we can simply use the hash-values to compare cycles, see comment at __hash__
		return hashable_from_set(self) == hashable_from_set(other)


def hashable_from_set(set):
	'''
	Sorts the item of the set an constructs a string
	
	Args:
		set: a list/set/multiset .... where the order of the elements is not important
	
	Return:
		A unique string based on the elements of the input set.
	'''	
	#logging.info("=== hashable_from_set ===")
	
	sorted_list_elements = sorted([x for x in set])
	#logging.debug(sorted_list_elements)
	return hash(str(sorted_list_elements))

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
	all_cycles = []
	for node in G:
		newcycles = get_all_cycles_single_startnode(G, node, min_cycle_length, only_base_cycles)
		for cycle in newcycles:
			if cycle not in all_cycles:
				all_cycles.append(cycle)
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
		for node in visited_neighbors:
			# add new cycle
			cycle = []
			current_cycle_node = current_dfs_node
			while not current_cycle_node == node:
				cycle.append(current_cycle_node)
				current_cycle_node = predecessors[current_cycle_node]
			cycle.append(current_cycle_node)				
			if len(cycle) > 3:
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
		if len(unvisited_neighbors) > 0:
			visited[current_dfs_node] = 1
			neighbor = unvisited_neighbors[0]
			predecessors[neighbor] = current_dfs_node
			successors[current_dfs_node].append(neighbor)
			current_dfs_node = neighbor
		else:
			visited[current_dfs_node] = 2
			#successors[current_dfs_node] = []
			current_dfs_node = predecessors[current_dfs_node]
	return cycles