#!usr/bin/python
# -*- coding: utf-8 -*-

'''
TESTS
'''

import logging

import networkx as nx

import GraphConstructionAlgorithms as gca
import GraphDataOrganizer as gdo

import EG
import LEX_M
import MT
import Random_Approx_MT as ramt

log_format = ('[%(asctime)s] %(levelname)-8s %(name)-12s %(message)s')
logging.basicConfig(
	filename='logs/debug_tests.log',
	filemode='w',
	format=log_format,
	level=logging.DEBUG,
)

logging.info("Initialization")
print("Initialization")

TEST_FILEPATH = "test/testgraph.json"

# simple graph for testing triangulation algorithms:
GRAPH_TEST_EDGES = [(0,1), (1,2), (2,3),(3,0)]
GRAPH_TEST = nx.Graph()
GRAPH_TEST.add_edges_from(GRAPH_TEST_EDGES)
logging.info("Graph for testing:")
logging.info(GRAPH_TEST)

# parameters for testing graph construction algorithms:
NUM_NODES = 50
PROB_EDGES = 0.3
NUM_EDGES_PLANAR = int(1.5 * NUM_NODES)
logging.info("Parameters for graph construction:")
logging.info("NUM_NODES: "+str(NUM_NODES))
logging.info("PROB_EDGES: "+str(PROB_EDGES))
logging.info("NUM_EDGES_PLANAR: "+str(NUM_EDGES_PLANAR))

logging.info("Start tests")
print("Start tests")

# ======= Test file operations =======
logging.info("======= TEST FILE OPERATIONS =======")
print("TEST FILE OPERATIONS")
gdo.write_graphs_to_json([GRAPH_TEST], TEST_FILEPATH)
gdo.load_graphs_from_json(TEST_FILEPATH)

# ======= Test graph construction algorithms =======
logging.info("======= TEST GRAPH CONSTRUCTION ALGORITHMS =======")
print("TEST GRAPH CONSTRUCTION ALGORITHMS")
gg = gca.GraphGenerator()

# ===== Connected Erdös-Renyi-Graph =====
logging.info("===== TEST CONNECTED ER-GRAPH =====")
print("TEST CONNECTED ER-GRAPH")
connected_er = gg.construct_connected_er(NUM_NODES, PROB_EDGES)
logging.debug("Constructed graph:")
logging.debug("number of nodes: "+str(len(connected_er.nodes())))
logging.debug("number of edges: "+str(len(connected_er.edges())))
print("ok")

# ===== Planar Erdös-Renyi-Graph =====
logging.info("===== TEST PLANAR ER-GRAPH =====")
print("TEST PLANAR ER-GRAPH")
try:
	planar_er = gg.construct_planar_er(NUM_NODES, NUM_EDGES_PLANAR)
	logging.debug("Constructed graph:")
	logging.debug("number of nodes: "+str(len(planar_er.nodes())))
	logging.debug("number of edges: "+str(len(planar_er.edges())))
except gca.TooManyIterationsException:
	logging.debug("No graph was constructed (TooManyIterationsException).")
except gca.WrongNetworkxVersion:
	logging.debug("No graph was constructed (WrongNetworkxVersion).")
print("ok")

# ===== Planar random Graph =====
logging.info("===== TEST PLANAR RANDOM GRAPH =====")
print("TEST PLANAR RANDOM GRAPH")
try:
	planar_random = gg.construct_planar_random(NUM_NODES, NUM_EDGES_PLANAR)
	logging.debug("Constructed graph:")
	logging.debug("number of nodes: "+str(len(planar_random.nodes())))
	logging.debug("number of edges: "+str(len(planar_random.edges())))
except gca.NoEdgesLeftException:
	logging.debug("No graph was constructed (NoEdgesLeftException).")
except gca.WrongNetworkxVersion:
	logging.debug("No graph was constructed (WrongNetworkxVersion).")
print("ok")
	
# ======= Test triangulation algorithms =======
logging.info("======= TEST TRIANGULATION ALGORITHMS =======")
print("TEST TRIANGULATION ALGORITHMS")
# ===== Elimination Game =====
logging.info("===== TEST ELIMINATION GAME =====")
print("TEST ELIMINATION GAME")
eg_triangulation_size = EG.evaluate_elimination_game(GRAPH_TEST.copy())
logging.debug("Size of triangulation by elimination game: "+str(eg_triangulation_size))
print("ok")

# ===== LEX M =====
logging.info("===== TEST LEX M =====")
print("TEST LEX M")
lexm_triangulation_size = LEX_M.evaluate_LEX_M(GRAPH_TEST.copy())
logging.debug("Size of triangulation by Lex M: "+str(lexm_triangulation_size))
print("ok")

# ===== Randomized LEX M =====
logging.info("===== TEST RANDOMIZED LEX M =====")
print("TEST RANDOMIZED LEX M")
randomized_lexm_triangulation_size = LEX_M.evaluate_randomized_LEX_M(GRAPH_TEST.copy())
logging.debug("Size of triangulation by randomized Lex M: "+str(randomized_lexm_triangulation_size))
print("ok")

# ===== Minimum Triangulation =====
logging.info("===== TEST MINIMUM TRIANGULATION =====")
print("TEST MINIMUM TRIANGULATION")
mt_triangulation_size = MT.get_minimum_triangulation_size(GRAPH_TEST.copy())
logging.debug("Size of minimum triangulation "+str(mt_triangulation_size))
print("ok")

# ===== Randomized Approximation Minimum Triangulation =====
logging.info("===== TEST RANDOMIZED APPROXIMATION FOR MINIMUM TRIANGULATION =====")
print("TEST RANDOMIZED APPROXIMATION FOR MINIMUM TRIANGULATION")
random_approx_mt_size = len(ramt.random_search_for_minimum_triangulation(GRAPH_TEST.copy()))
logging.debug("Size of rand. approx. for minimum triangulation "+str(random_approx_mt_size))
print("ok")