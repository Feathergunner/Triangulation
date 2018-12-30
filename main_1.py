#!usr/bin/python
# -*- coding: utf-8 -*-

import logging
import cProfile 

import networkx as nx
import matplotlib.pyplot as plt

import LEX_M
import EG
import MT
import graph_meta as gm
import run_time_eval as rte
import random_algos as ra

#import graph_construction as gc
import graph_meta as meta

log_format = ('[%(asctime)s] %(levelname)-8s %(name)-12s %(message)s')
logging.basicConfig(
	filename='logs/debug_tryout.log',
	filemode='w',
	format=log_format,
	level=logging.INFO,
)

def test_triangulation(G, algo=LEX_M.triangulate_Lex_M):
	edges_original = [e for e in G.edges()]
	H = algo(G)
	edges_added = [e for e in H.edges() if e not in edges_original]
	check_all_cycles(H)
	print ("Size of this minimal triangulation: "+str(len(edges_added)))
	draw_chordal_graph(H, edges_original, edges_added)
	return H

def test_EG(G):
	H = elimination_game_triangulation(G)
	edges_added = [e for e in H.edges() if e not in G.edges()]
	print ("Size of this triangulation by elimination game: "+str(len(H.edges())-len(G.edges())))
	draw_chordal_graph(H, edges_original, edges_added)
	
def check_all_cycles(G):
	all_cycles = nx.cycle_basis(G)
	for cycle in all_cycles:
		if len(cycle) > 3:
			cycle_subgraph = G.subgraph(cycle)
			print (cycle)
			print (nx.is_chordal(cycle_subgraph))

def test_poe(G):
	edges_original = [e for e in G.edges()]
	H = LEX_M.triangulate_LEX_M(G)
	edges_added = [e for e in H.edges() if e not in edges_original]
	poe = meta.LEX_BFS(H)
	draw_chordal_graph(H, edges_original, edges_added)
	print (poe)
	
def test_mt(G):
	mt = MT.MT_MinimumTriangulation(G)
	mt.find_minimum_triangulation()
	chord_edges = mt.edges_of_minimum_triangulation
	Triang = G.copy()
	Triang.add_edges_from(chord_edges)
	print ("Result is chordal: "+str(nx.is_chordal(Triang)))
	if not nx.is_chordal(Triang):
		for c in nx.cycle_basis(Triang):
			print (c)
	print ("Size of minimum triangulation: "+str(len(chord_edges)))
	#draw_chordal_graph(G)
	draw_chordal_graph(Triang, G.edges(), chord_edges)
	
	#draw_chordal_graph(G)
	#test_triangulation(H)
	#for c in nx.cycle_basis(H):
	#	print (c)

def test_random(G):
	ae_random = rte.AlgorithmEvaluator(ra.random_search_for_best_triangulation, G)
	ae_random.run()
	print (str(ae_random.results[0]))

def draw_chordal_graph(G, edges_original=None, edges_added=None):
	if edges_original == None:
		edges_original = G.edges()
	if edges_added == None:
		edges_added = []
	pos = nx.shell_layout(G)
	nx.draw_networkx_nodes(G, pos, node_color='r', node_size=50)
	nx.draw_networkx_edges(G, pos, edgelist=edges_original, width=1, edge_color='black')
	nx.draw_networkx_edges(G, pos, edgelist=edges_added, width=1, edge_color='red')
	labels = {}
	for n in G:
		labels[n] = n
	nx.draw_networkx_labels(G, pos, labels, font_size=16)
	plt.axis('off')
	plt.show()
	
def test_get_all_cycles(G):
	#gm.get_all_cycles(G)
	#gm.get_all_cycle_from_cycle_basis(G)
	ae_cycles_simple = rte.AlgorithmEvaluator(gm.get_all_cycles, G)
	ae_cycles_simple.run()
	result_cycle_simple = ae_cycles_simple.results[0]
	ae_cycles_basis = rte.AlgorithmEvaluator(gm.get_all_cycle_from_cycle_basis, G)
	ae_cycles_basis.run()
	result_cycle_basis = ae_cycles_basis.results[0]

	print ("Result:")
	print (str(result_cycle_simple))
	print ("Result:")
	print (str(result_cycle_basis))

def test_cprofile(G):
	cProfile.run("gm.get_all_cycles(G)")
	cProfile.run("gm.get_all_cycle_from_cycle_basis(G)")

if __name__=="__main__":
	number_of_nodes = 10

	#G = nx.cycle_graph(number_of_nodes)
	#G = nx.erdos_renyi_graph(number_of_nodes,0.6)
	
	# this graph is chordal after adding the single edge (4,0):
	E1 = [(0, 1), (0, 2), (0, 3), (0, 5), (1, 4), (2, 3), (2, 5), (3, 4), (3, 5), (4, 5)]#, (4,0)]

	# in this graph a new non-chordal cycle of length 4 is created by the minimum triangulation:
	E2 = [(0, 1), (0, 2), (0, 3), (0, 5), (0, 6), (1, 2), (1, 3), (1, 6), (2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (3, 4), (3, 5), (3, 6), (4, 5), (4, 7), (6, 7)]

	E3 = [(0,1), (1,2), (2,3), (3,0), (0,4), (1,4), (0,5), (3,5), (4,5), (0,6), (3,6), (2,7), (3,7), (6,7), (2,4), (2,5), (1,6), (1,7)]
	
	# graph to test get_all_cycles:
	E4 = [(0,1), (0,2), (0,3), (0,4), (1,2), (2,3), (3,4), (4,1)]

	G = nx.Graph()
	#G.add_nodes_from(V)
	G.add_edges_from(E2)
		
	logging.debug([n for n in G])
	logging.debug([e for e in G.edges()])
	
	#draw_chordal_graph(G)
	
	#test_cprofile(G)

	#test_random(G)
	#test_get_all_cycles(G)
	#print(nx.is_chordal(G))
	#G_POE = G.copy()
	#test_poe(G_POE)
	G_LEX = G.copy()
	test_triangulation(G_LEX)
	#G_MIN = G.copy()
	#test_mt(G_MIN)
	
	#test_triangulation(G)
	#H = test_triangulation(G)
	#test_poe(G)
	#test_triangulation(H, EG.elimination_game_triangulation)
	
	#test_random(10)
	#G = nx.erdos_renyi_graph(10,0.5)
	#T = nx.minimum_spanning_tree(G)
	