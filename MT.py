#!usr/bin/python
# -*- coding: utf-8 -*-

import logging

import networkx as nx

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

class MT_TooLargeCycleError(Exception):
	'''
	Custom error type that gets thrown when the input graph contains a cycle that is too large.
	This is intended to prevent running out of memory (and out of time),
	since memory requirement of this algorithm is in O(2^k), where k < |E(G)| is the length of the largest basic cycle in G.
	Time complexity is in O(2^n), with n = |G|.
	'''
	
class MT_Chordedge:
	'''
	Datastructure to represent a possible chord-edge of one (or more) cycles of the graph
	Stores all cycles for which this edge is a chord
	
	Args:
		node_v , node_u : two graph nodes in networkx-format that define the edge
		
	Attributes:
		node_v, node_u : the nodes that define the edge
		is_in_graph : a bool that describes whether this edge is currently contained in the triangulation or not
		cycle_indices : a list of ints that contains all indices of cycles (type MT_Cycle) for which this edge is a chord-edge
		induced_cycles : a list of integers that contains all indices of cycles that are not in the base graph but can appear once this edge is in the graph.
	'''
	def __init__(self, node_v, node_u):
		logging.info("=== MT_Chordedge.init ===")
		self.node_v = node_v
		self.node_u = node_u
		self.is_in_graph = False
		self.cycle_indices = []
		self.induced_cycles = []

	def add_cycle(self, cycle_id):
		self.cycle_indices.append(cycle_id)

	def get_edge(self):
		return (self.node_v, self.node_u)

	def __getitem__(self, key):
		if key == 0:
			return self.node_v
		elif key == 1:
			return self.node_u
		else:
			return None
	
	def __str__(self):
		return "("+str(self.node_v)+","+str(self.node_u)+")"

class MT_Cycle:
	'''
	Datastructure to represent a cycle of the graph
	Stores all possible chord-edges and the resulting subcycles once they have been computed
	
	Is hashable.
	
	Args:
		cyclenodes : a list of nodes in networkx-format that form a cycle in the original graph.
		
	Attributes:
		cyclenodes : the list of nodes that define this cycle
		chordedge_ids : a list of ints that contains all indices of chord-edges (type MT_Chordedge) that are chords for this cycle
		is_in_graph : a bool that describes whether this cycle is currently contained unsplit in the triangulation or not
		subcycles : a dict {chord_edge_id (int) : subcycle_ids(list(int))} that maps chordedge-indices to lists subcycle-indices, where each subcycle-indexdescribes a cycle that is created when this cycle is split by the chordedge defined by chord_edge_id
		required_chordedges : a list of ints that contain all indices of chordedges that have to be in the graph for this cycle to appear.
	'''
	def __init__(self, cyclenodes):
		logging.info("=== MT_Cycle.init ===")
		self.cyclenodes = cyclenodes
		self.chordedge_ids = []
		self.is_in_graph = True
		self.subcycles = {}
		self.required_chordedges = []

	def __len__(self):
		return len(self.cyclenodes)

	def __getitem__(self, key):
		return self.cyclenodes[key]

	def __contains__(self, key):
		return key in self.cyclenodes
		
	def __str__(self):
		return str(self.cyclenodes)
		
	def __hash__(self):
		# note that in case of comparability, the actual order of the nodes within the cycle does not matter
		# since the cycle-nodes and the edges of the graph define the cycle
		return hashable_from_set(self.cyclenodes)
		
	def __eq__(self, other):
		# we can simply use the hash-values to compare cycles, see comment at __hash__
		return hashable_from_set(self) == hashable_from_set(other)

	def add_chord(self, chord_id):
		self.chordedge_ids.append(chord_id)

	#def set_as_split(self, chord_id, list_of_subcycle_ids):
	#	self.subcycles[chord_id] = list_of_subcycle_ids

class MT_MinimumTriangulation:
	'''
	This class contains the methods to compute a minimum triangulation and handles all the neccessary datastructures.
	Note that the current working graph is not explicitly stored, as it follows from G and the subset of chordedges of F that are flagged with is_in_graph = True.
	
	Args:
		G : a graph in networkx-format for which a minimum triangulation should be computed
		
	Attributes:
		G : the graph
		F : a list of edges in networkx-format. This list contains all the possible chord-edges (type MT_Chordedge) that can be added to G
		cycles : a list of cycles (type MT_Cycle) that are contained in G or in any graph constructed from G by inserting chordedges
		cycle_ids : a dict {cycle (MT_Cycle) : cycle_id(int)} that maps each cycle to its id in the list of cycles.
		number_of_nonchordal_cycles : an int describing the number of cycles of length > 3 that are contained in the current working graph.
		chord_adjacencies : a dict {node, node : chord_id} that maps tuples of nodes to indices of chords, if the two nodes are connected by a possible chord-edge from the set F.
	'''
	def __init__(self, G):
		logging.info("=== MT_MinimumTriangulation.init ===")
		self.G = G

		self.F = []
		self.cycles = []
		self.cycle_ids = {}
		self.number_of_nonchordal_cycles = 0
		self.chord_adjacencies = {}

		self.edges_of_minimum_triangulation = None

	def find_minimum_triangulation(self):
		'''
		Finds a minimum triangulation of G, by checking each possible order of inserting chord-edges into the graph G until G is chordal.
	
		Running time in O(poly(n) * 2^n), where n = |G|.
		'''
		logging.info("=== MT_MinimumTriangulation.find_minimum_triangulation ===")
		
		# initialize a database
		self.init_cycle_chord_database()
		
		# initialize stack of currently considered edges:
		current_edge_stack = []
		# initialize map of edgesets:
		chordality_check = {}
        
		# initialize stack of added chord-edges
		chord_stack = []
		
		# initialize minimum triangulation chordset:
		minimum_triangulation_size = -1
		minimum_triangulation_chordset = []
        
		#current_cycle_id = 0
		#current_chord_in_cycle_id = 0
		current_chord_id = 0
		terminated = nx.is_chordal(self.G) or len(self.cycles) == 0
		while not terminated:
			logging.debug("=*= NEXT ITERATION =*=")
			logging.debug("Current cycles in the graph:")
			for cycle_id in range(len(self.cycles)):
				logging.debug(" "+str(cycle_id)+" : "+str(self.cycles[cycle_id])+" ["+str(self.cycles[cycle_id].is_in_graph)+"]")
			logging.debug("Current number of nonchordal cycles: "+str(self.number_of_nonchordal_cycles))
			
			logging.debug("Current chords in the graph:")
			for chord in [e for e in self.F if e.is_in_graph]:
				logging.debug(chord)
				
			# get next chord that is
			# a) not in graph and
			# b) would split a cycle
			current_chord_id = self.get_next_chord(current_chord_id)
			logging.debug("Current chord: "+str(current_chord_id)+": "+str(self.F[current_chord_id]))
        
			# if such a chord exist, set the current_chord_id to this chord
			#	split all cycles that contain this chord
			#	check if graph is chordal.
			#		if chordal, check if current edge set is minimum
			# 		else add current_chord_id and a list of all split cycles to chord_stack
			# otherwise
			#	pop the next tuple from the stack
			#	merge all cylces that were split by that last operation from the stack
			
			if current_chord_id >= len(self.F):
				terminated = True
				logging.debug("Current id larger than total number of chords. Terminate.")
				break
				
			elif current_chord_id >= 0:
				logging.debug("Add this chord to graph.")
				cycles_to_split = [cycle_id for cycle_id in self.F[current_chord_id].cycle_indices if self.cycles[cycle_id].is_in_graph]
				chord_stack.append((current_chord_id, cycles_to_split))
				for cycle_id in cycles_to_split:
					self.split_cycle(cycle_id, current_chord_id)
					# set chord as added:
					self.F[current_chord_id].is_in_graph = True
					## TO DO: check if a new cycle was constructed:
					'''
					for induced_cycle_id in self.F[current_chord_id].induced_cycles:
						for required_edge_id in self.cycles[induced_cycle_id].required_chordedges:
							if self.F[required_edge_id].is_in_graph:
								logging.debug("Cycle "+str(induced_cycle_id)+" has to be added!")
								self.cycles[induced_cycle_id].is_in_graph = True
								# check if cycle is already split:
					'''
					number_of_added_cycles = self.get_all_cycles_single_startnode(self.F[current_chord_id][0])
					if number_of_added_cycles > 0:
						print ("Add new cycles with chord "+str(current_chord_id))
						print ([self.F[edge_id].get_edge() for (edge_id, cyclelist) in chord_stack])
						num_cycles = len(self.cycles)
						for cycle_id in range(num_cycles-number_of_added_cycles,num_cycles):
							print ("Add a new cycle: "+str(self.cycles[cycle_id]))
							self.F[current_chord_id].induced_cycles.append(cycle_id)
							self.init_cycle_chord_database_for_cycle(cycle_id)					

					# check if graph is chordal:
					if self.number_of_nonchordal_cycles == 0:
						# check if current edge set has minimum size so far:
						currently_included_chordedges = [e for e in self.F if e.is_in_graph]
						if minimum_triangulation_size < 0 or minimum_triangulation_size > len(currently_included_chordedges):
							minimum_triangulation_size = len(currently_included_chordedges)
							minimum_triangulation_chordset = currently_included_chordedges
						
			elif len(chord_stack) > 0:
				logging.debug("Remove last chord from graph.")
				(current_chord_id, last_split_cycles) = chord_stack.pop()
				logging.debug("Last added chord: "+str(current_chord_id)+": "+str(self.F[current_chord_id]))

				# merge previously split cycles:
				for cycle_id in last_split_cycles:
					self.merge_cycle(current_chord_id, cycle_id)
				# remove induced cycles:
				for cycle_id in self.F[current_chord_id].induced_cycles:
					print ("Remove cycle: "+str(self.cycles[cycle_id]))
					self.cycles[cycle_id].is_in_cycle = False
					for chord_id in self.cycles[cycle_id].chordedge_ids:
						self.F[chord_id].cycle_indices.remove(cycle_id)
				self.F[current_chord_id].induced_cycles = []
				
				self.F[current_chord_id].is_in_graph = False
				current_chord_id += 1
				
			else:
				logging.warning("All possibilities are evaluated. Terminate.")
				terminated = True
		
		self.edges_of_minimum_triangulation = [e.get_edge() for e in minimum_triangulation_chordset]

	def init_cycle_chord_database(self):
		'''
		Initialized the database containing all cycles and possible chord-edges
		as well as the information which chord is contained in which cycles.
		'''
		logging.info("=== MT_MinimumTriangulation.init_cycle_chord_database ===")
		
		# Get all chordless cycles of G:
		self.get_all_cycles()
		logging.debug("All cycles of G:")
		for c in self.cycles:
			logging.debug(c)
		
		self.cycle_ids = {self.cycles[i] : i for i in range(len(self.cycles))}
		
		# Check the maximum cycle length. If the largest cycle contains more than 16 nodes, abort.
		if len(self.cycles) > 0:
			maximum_cycle_length = max([len(c) for c in self.cycles])
			if maximum_cycle_length > 16:
				raise MT_TooLargeCycleError("Maximum cycle length too large")
		
		self.number_of_nonchordal_cycles = len(self.cycles)
		# Construct set of all possible chord edges for G:
		# and the database describing chord-cycle-relationships
		for cycle_id in range(len(self.cycles)):
			logging.debug("Current chord_id data:")
			for key in self.chord_adjacencies:
				logging.debug(str(key)+ " : " +str(self.chord_adjacencies[key]))
			self.init_cycle_chord_database_for_cycle(cycle_id)
	
	def init_cycle_chord_database_for_cycle(self, cycle_id):
		'''
		Initialize the database for a single cycle.
		
		Args:
			cycle_id : The id of the cycle for which the database is initialized.
		'''
		logging.info("=== MT_MinimumTriangulation.init_cycle_chord_database_for_cycle ===")
		logging.info("Init cycle chord database for cycle "+str(cycle_id)+": "+str(self.cycles[cycle_id]))
		
		#logging.debug("Current chord_id data:")
		#for key in self.chord_adjacencies:
		#	logging.debug(str(key)+ " : " +str(self.chord_adjacencies[key]))
		
		cycle = self.cycles[cycle_id]
		for i in range(len(cycle)):
			if cycle[i] not in self.chord_adjacencies:
				self.chord_adjacencies[cycle[i]] = {}
			for j in range(i+2, len(cycle)):
				if i == 0 and j == len(cycle)-1:
					break
				if cycle[j] not in self.chord_adjacencies[cycle[i]]:
					if cycle[j] not in self.chord_adjacencies:
						self.chord_adjacencies[cycle[j]] = {}
					current_chord_id = len(self.F)
					self.chord_adjacencies[cycle[i]][cycle[j]] = current_chord_id
					self.chord_adjacencies[cycle[j]][cycle[i]] = current_chord_id
					self.F.append(MT_Chordedge(cycle[i],cycle[j]))
				else:
					current_chord_id = self.chord_adjacencies[cycle[i]][cycle[j]]
				logging.debug("Add chord "+str(current_chord_id)+" ("+str(cycle[i])+","+str(cycle[j])+") to this cycle.")
				self.F[current_chord_id].add_cycle(cycle_id)
				self.cycles[cycle_id].add_chord(current_chord_id)

	def split_cycle(self, cycle_id, chord_id):
		'''
		Splits a cycle into two subcycles by a given edge.
		
		Args:
			cycle_id : the cycle to split
			chord_id : the chord that splits the cycle
		'''
		logging.info("=== MT_MinimumTriangulation.split_cycle ===")
		logging.info("split cycle "+str(cycle_id)+": "+str(self.cycles[cycle_id])+" at chord "+str(chord_id)+": "+str(self.F[chord_id]))

		if chord_id in self.cycles[cycle_id].subcycles:
			# get ids of subcycles
			for subcycle_id in self.cycles[cycle_id].subcycles[chord_id]:
				self.cycles[subcycle_id].is_in_graph = True
				self.number_of_nonchordal_cycles += 1
		else:
			# compute new subcycles:
			nodes_new_cycles = self.get_subcycles(cycle_id, chord_id)
			
			if chord_id not in self.cycles[cycle_id].subcycles:
				self.cycles[cycle_id].subcycles[chord_id] = []
			
			for i in range(2):
				if len(nodes_new_cycles[i]) > 3:
					subcycle = MT_Cycle(nodes_new_cycles[i])
					if subcycle not in self.cycle_ids:
						logging.debug("create new cycle for subsycle "+str(i+1)+": "+str(subcycle))
						subcycle_id = len(self.cycles)
						self.cycles.append(subcycle)
						self.cycle_ids[subcycle] = subcycle_id
						self.init_cycle_chord_database_for_cycle(subcycle_id)
						self.number_of_nonchordal_cycles += 1
					else:
						subcycle_id = self.cycle_ids[subcycle]
						if not self.cycles[subcycle_id].is_in_graph:
							self.cycles[subcycle_id].is_in_graph = True
							self.number_of_nonchordal_cycles += 1
					logging.debug("Add subcycle "+str(subcycle_id)+" to chord "+str(chord_id)+" of cycle "+str(cycle_id))
					self.cycles[cycle_id].subcycles[chord_id].append(subcycle_id)

		# set cycle as removed:
		self.cycles[cycle_id].is_in_graph = False
		self.number_of_nonchordal_cycles -= 1
			
	def merge_cycle(self, chord_id, cycle_id):
		'''
		Merges two cycle along a chord, removes the chord from the graph
		
		Args:
			chord_id : the chord that is removed from the graph
			cycle_id : the cycle that is recreated by merging its subcycles
		'''
		logging.info("=== MT_MinimumTriangulation.merge_cycle ===")
		logging.info("Merge cycles into cycle "+str(cycle_id)+" at chord "+str(chord_id))
		
		self.cycles[cycle_id].is_in_graph = True
		self.number_of_nonchordal_cycles += 1
		for subcycle_id in self.cycles[cycle_id].subcycles[chord_id]:
			self.cycles[subcycle_id].is_in_graph = False
			self.number_of_nonchordal_cycles -= 1
			
	def get_subcycles(self, cycle_id, chord_id):
		'''
		Constructs the lists of nodes that define the subcycles of a cycle
		
		Args:
			cycle_id : the index of the parent cycle
			chord_id : the index of the chord that splits the cycle
			
		Return:
			A list of lists of integer, each containing the nodes of a subcycle
		'''
		logging.info("=== MT_MinimumTriangulation.get_subcycles ===")
		
		nodes_new_cycles = [[],[]]
		id_v = -1
		id_u = -1
		i = -1
		cycle = self.cycles[cycle_id]
		for node in cycle:
			i += 1
			if node == self.F[chord_id][0]:
				id_v = i
			if node == self.F[chord_id][1]:
				id_u = i
		nodes_new_cycles[0] = cycle[:min(id_v,id_u)+1]+cycle[max(id_v,id_u):]
		nodes_new_cycles[1] = cycle[min(id_v,id_u):max(id_v,id_u)+1]
		logging.debug("nodes first subcycle: "+str(nodes_new_cycles[0]))
		logging.debug("nodes second subcycle: "+str(nodes_new_cycles[1]))
			
		return nodes_new_cycles
		
	def get_next_chord(self, current_chord_id):
		'''
		Get the id of the next chord that is not in the graph and would still split a cycle
		
		Args:
			current_chord_id : the current chord id, from which the search starts
			
		Return:
			A valid chord index conform to the specification above, if it exists. -1 otherwise.
		'''
		logging.info("=== MT_MinimumTriangulation.get_next_chord ===")
		found_next_chord = False
		while current_chord_id < len(self.F):
			if not self.F[current_chord_id].is_in_graph:
				for cycle_id in self.F[current_chord_id].cycle_indices:
					if self.cycles[cycle_id].is_in_graph:
						return current_chord_id
			current_chord_id += 1
		return -1
		
	def get_all_cycles(self, min_cycle_length=4, only_base_cycles=True):
		'''
		Constructs a list of all cycles of a minimum length of the graph G

		Args:
			min_cycle_length : the minimum length of cycles that are considered
			only_base_cycles : if true, this method returns only chordless cycles. Otherwise, all cycles will be returned
		'''
		logging.info("=== MT_MinimumTriangulation.get_all_cycles ===")

		# use depth-first-search at each node
		for node in self.G:
			self.get_all_cycles_single_startnode(node, min_cycle_length, only_base_cycles)

	def get_all_cycles_single_startnode(self, startnode, min_cycle_length=4, only_base_cycles=True):
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
		
		G_temp = self.G.copy()
		G_temp.add_edges_from([e.get_edge() for e in self.F if e.is_in_graph])
		logging.debug("Graph "+str(G_temp.edges()))

		visited = {n : 0 for n in G_temp}
		visited[startnode] = 1
		predecessors = {}
		successors = {n : [] for n in G_temp}
		predecessors[startnode] = None
		current_dfs_node = startnode
		
		number_of_added_cycles = 0

		while not current_dfs_node == None:
			logging.debug("Current node: "+str(current_dfs_node))
				
			visited_neighbors = [n for n in G_temp.neighbors(current_dfs_node) if visited[n] == 1]
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
						subgraph = G_temp.subgraph(cycle)
						if len(subgraph.edges()) > len(cycle):
							add_this_cycle = False
							logging.debug("Cycle contains a chord!")							
					if add_this_cycle:
						new_cycle = MT_Cycle(cycle)
						logging.debug("Cycle: "+str(new_cycle))
						if new_cycle not in self.cycles:
							logging.debug("Cycle is new!")
							self.cycles.append(new_cycle)
							number_of_added_cycles += 1
						else:
							logging.debug("Cycle already exists!")
			unvisited_neighbors = [n for n in G_temp.neighbors(current_dfs_node) if (visited[n] == 0) or (visited[n] == 2 and not n in successors[current_dfs_node])]
			if len(unvisited_neighbors) > 0:
				visited[current_dfs_node] = 1
				neighbor = unvisited_neighbors[0]
				predecessors[neighbor] = current_dfs_node
				successors[current_dfs_node].append(neighbor)
				current_dfs_node = neighbor
			else:
				visited[current_dfs_node] = 2
				successors[current_dfs_node] = []
				current_dfs_node = predecessors[current_dfs_node]


		return number_of_added_cycles