#!usr/bin/python
# -*- coding: utf-8 -*-

def hashable_string_from_set(set):
	'''
	Sorts the item of the set an constructs a string
	
	Args:
		set: a list/set/multiset .... where the order of the elements is not important
	
	Return:
		A unique string based on the elements of the input set.
	'''
	
	logging.info("=== hashable_string_from_set ===")
	sorted_list_elements = sorted([x for x in set])
	logging.debug(sorted_list_elements)
	return str(sorted_list_elements)
	

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



