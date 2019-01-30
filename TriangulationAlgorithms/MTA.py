#!usr/bin/python
# -*- coding: utf-8 -*-

import logging

import networkx as nx

from TriangulationAlgorithms import graph_meta as gm
from TriangulationAlgorithms import TriangulationAlgorithm as ta
from TriangulationAlgorithms import StupidMT
from TriangulationAlgorithms import LEX_M

def triangulate_MTA(G):
	algo = Algorithm_MinimumTriangulationApproximation(G)
	algo.run()
	return {
		"H" : algo.get_triangulated(),
		"size" : len(algo.get_triangulation_edges()),
		"mean" : len(algo.get_triangulation_edges()),
		"variance" : 0,
		"repetitions" : 1
		}

class Algorithm_MinimumTriangulationApproximation(StupidMT.Algorithm_MinimumTriangulation):
	def __init__(self, G):
		logging.info("=== MTA.Algorithm_MinimumTriangulationApproximation.init ===")
		super().__init__(G)
		
	def run(self):
		'''
		Finds an approximation of a minimum triangulation of G, by checking each possible order of inserting chord-edges into the graph G until G is chordal.
	
		Mostly equivalent to MT, but does not check for new cycles each iteration. Instead, the resulting graph might have still non-chordal cycles, which are triangulated in a final iteration by LEX-M.
		'''
		logging.info("=== MT_MinimumTriangulation.run ===")
		
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
					# compute current set of cycles:
					G_temp = self.G.copy()
					G_temp.add_edges_from([e.get_edge() for e in self.F if e.is_in_graph])

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
					self.cycles[cycle_id].is_in_cycle = False
					for chord_id in self.cycles[cycle_id].chordedge_ids:
						self.F[chord_id].cycle_indices.remove(cycle_id)
				self.F[current_chord_id].induced_cycles = []
				
				self.F[current_chord_id].is_in_graph = False
				current_chord_id += 1
				
			else:
				logging.debug("All possibilities are evaluated. Terminate.")
				terminated = True
		
		self.edges_of_triangulation = [e.get_edge() for e in minimum_triangulation_chordset]
		self.H = self.G.copy()
		self.H.add_edges_from(self.edges_of_triangulation)
		
		results_lexm = LEX_M.triangulate_LexM(self.H)
		self.H = results_lexm["H"]
		self.edges_of_triangulation = [e for e in self.H.edges() if e not in self.G.edges()]