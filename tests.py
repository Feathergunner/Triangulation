#!usr/bin/python
# -*- coding: utf-8 -*-

'''
TESTS
'''

import logging
import sys

import networkx as nx

from Evaluation import GraphConstructionAlgorithms as gca
from Evaluation import GraphDataOrganizer as gdo

from TriangulationAlgorithms import EG
from TriangulationAlgorithms import SMS
from TriangulationAlgorithms import LEX_M
from TriangulationAlgorithms import MCS_M
from TriangulationAlgorithms import CMT
from TriangulationAlgorithms import MT
from TriangulationAlgorithms import MTA
from TriangulationAlgorithms import RAMT

log_format = ('[%(asctime)s] %(levelname)-8s %(name)-12s %(message)s')
logging.basicConfig(
	filename='logs/debug_tests.log',
	filemode='w',
	format=log_format,
	level=logging.DEBUG,
)

DO_TEST_FIO = True
DO_TEST_GGEN = True
DO_TEST_ALGO = True

# parse additional args:
for arg in sys.argv[1:]:
	if arg == "ALGO":
		DO_TEST_FIO = False
		DO_TEST_GGEN = False
	elif arg == "GGEN":
		DO_TEST_FIO = False
		DO_TEST_ALGO = False

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
MAX_DEGREE = 4
MAX_CLIQUE_SIZE = 4
logging.info("Parameters for graph construction:")
logging.info("NUM_NODES: "+str(NUM_NODES))
logging.info("PROB_EDGES: "+str(PROB_EDGES))
logging.info("NUM_EDGES_PLANAR: "+str(NUM_EDGES_PLANAR))
logging.info("MAX_DEGREE: "+str(MAX_DEGREE))
logging.info("MAX_CLIQUE_SIZE: "+str(MAX_CLIQUE_SIZE))

logging.info("Start tests")
print("Start tests")

# ======= Test file operations =======
if DO_TEST_FIO:
	logging.info("======= TEST FILE OPERATIONS =======")
	print("TEST FILE OPERATIONS")
	gdo.write_graphs_to_json([GRAPH_TEST], TEST_FILEPATH)
	gdo.load_graphs_from_json(TEST_FILEPATH)

if DO_TEST_GGEN:
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

	# ===== Random graph with max node degree =====
	logging.info("===== TEST RANDOM GRAPH WITH MAXIMUM NODE DEGREE =====")
	print("TEST RANDOM GRAPH WITH MAXIMUM NODE DEGREE")
	random_maxdeg = gg.construct_random_max_degree(NUM_NODES, PROB_EDGES, MAX_DEGREE)
	max_deg = max([random_maxdeg.degree(v) for v in random_maxdeg.nodes()])
	logging.debug("Constructed graph:")
	logging.debug("number of nodes: "+str(len(random_maxdeg.nodes())))
	logging.debug("number of edges: "+str(len(random_maxdeg.edges())))
	logging.debug("maximum node degree: "+str(max_deg))
	if max_deg > MAX_DEGREE:
		logging.debug("constructed graph not conform to requirements!")
		print ("NOT OKAY")
	else:
		print("ok")

	# ===== Random graph with max clique size =====
	logging.info("===== TEST RANDOM GRAPH WITH MAXIMUM CLIQUE SIZE =====")
	print("TEST RANDOM GRAPH WITH MAXIMUM CLIQUE SIZE")
	random_maxclique = gg.construct_random_max_degree(NUM_NODES, PROB_EDGES, MAX_CLIQUE_SIZE)
	max_clique = max([len(c) for c in nx.find_cliques(random_maxclique)])
	logging.debug("Constructed graph:")
	logging.debug("number of nodes: "+str(len(random_maxdeg.nodes())))
	logging.debug("number of edges: "+str(len(random_maxdeg.edges())))
	logging.debug("maximum clique size: "+str(max_clique))
	if max_clique > MAX_CLIQUE_SIZE:
		logging.debug("constructed graph not conform to requirements!")
		print ("NOT OKAY")
	else:
		print ("ok")
		
# ======= Test triangulation algorithms =======
if DO_TEST_ALGO:
	logging.info("======= TEST TRIANGULATION ALGORITHMS =======")
	print("TEST TRIANGULATION ALGORITHMS")
	# ===== Elimination Game =====
	logging.info("===== TEST ELIMINATION GAME =====")
	print("TEST ELIMINATION GAME")
	triangulation_eg = EG.triangulate_EG(GRAPH_TEST.copy())
	logging.debug("Size of triangulation by elimination game: "+str(triangulation_eg["size"]))
	print("ok")

	logging.info("===== TEST RANDOMIZED ELIMINATION GAME =====")
	print("TEST RANDOMIZED ELIMINATION GAME")
	triangulation_eg_r = EG.triangulate_EG(GRAPH_TEST.copy(), randomized=True)
	logging.debug("Size of triangulation by randomized elimination game: "+str(triangulation_eg_r["size"]))
	print("ok")
	
	# ===== Elimination Game Plus =====
	logging.info("===== TEST ELIMINATION GAME PLUS =====")
	print("TEST ELIMINATION GAME PLUS")
	triangulation_egp = EG.triangulate_EGPLUS(GRAPH_TEST.copy())
	logging.debug("Size of triangulation by elimination game plus: "+str(triangulation_egp["size"]))
	print("ok")

	logging.info("===== TEST RANDOMIZED ELIMINATION GAME PLUS =====")
	print("TEST RANDOMIZED ELIMINATION GAME PLUS")
	triangulation_egp_r = EG.triangulate_EGPLUS(GRAPH_TEST.copy(), randomized=True)
	logging.debug("Size of triangulation by randomized elimination game plus: "+str(triangulation_egp_r["size"]))
	print("ok")

	# ===== Saturate Minimal Separators =====
	logging.info("TEST SATURATE MINIMAL SEPARATORS")
	print ("TEST SATURATE MINIMAL SEPARATORS")
	triangulation_sms = SMS.triangulate_SMS(GRAPH_TEST.copy())
	logging.debug("Size of triangulation by saturating minimal separators: "+str(triangulation_sms["size"]))
	print("ok")

	# ===== Randomized Saturate Minimal Separators =====
	logging.info("TEST RANDOMIZED SATURATE MINIMAL SEPARATORS")
	print ("TEST RANDOMIZED SATURATE MINIMAL SEPARATORS")
	triangulation_sms_r = SMS.triangulate_SMS(GRAPH_TEST.copy(), randomized=True)
	logging.debug("Size of triangulation by randomized saturating minimal separators: "+str(triangulation_sms_r["size"]))
	print("ok")

	# ===== LEX M =====
	logging.info("===== TEST LEX M =====")
	print("TEST LEX M")
	triangulation_lexm = LEX_M.triangulate_LexM(GRAPH_TEST.copy())
	logging.debug("Size of triangulation by Lex M: "+str(triangulation_lexm["size"]))
	print("ok")

	# ===== Randomized LEX M =====
	logging.info("===== TEST RANDOMIZED LEX M =====")
	print("TEST RANDOMIZED LEX M")
	triangulation_lexm_r = LEX_M.triangulate_LexM(GRAPH_TEST.copy(), randomized=True)
	logging.debug("Size of triangulation by randomized Lex M: "+str(triangulation_lexm_r["size"]))
	print("ok")
	
	# ===== MCS M =====
	logging.info("===== TEST MCS M =====")
	print("TEST MCS M")
	triangulation_mcsm = MCS_M.triangulate_MCSM(GRAPH_TEST.copy())
	logging.debug("Size of triangulation by MCS M: "+str(triangulation_mcsm["size"]))
	print("ok")

	# ===== Randomized MCS M =====
	logging.info("===== TEST RANDOMIZED MCS M =====")
	print("TEST RANDOMIZED MCS M")
	triangulation_mcsm_r = MCS_M.triangulate_MCSM(GRAPH_TEST.copy(), randomized=True)
	logging.debug("Size of triangulation by randomized MCS M: "+str(triangulation_mcsm_r["size"]))
	print("ok")

	# ===== CMT =====
	logging.info("===== TEST CMT =====")
	print("TEST CMT")
	triangulation_cmt = CMT.triangulate_CMT(GRAPH_TEST.copy())
	logging.debug("Size of triangulation by CMT: "+str(triangulation_cmt["size"]))
	print("ok")

	# ===== Randomized CMT =====
	logging.info("===== TEST RANDOMIZED CMT =====")
	print("TEST RANDOMIZED CMT")
	triangulation_cmt_r = CMT.triangulate_CMT(GRAPH_TEST.copy(), randomized=True)
	logging.debug("Size of triangulation by randomized CMT: "+str(triangulation_cmt_r["size"]))
	print("ok")

	# ===== Minimum Triangulation =====
	logging.info("===== TEST MINIMUM TRIANGULATION =====")
	print("TEST MINIMUM TRIANGULATION")
	triangulation_mt = MT.triangulate_MT(GRAPH_TEST.copy())
	logging.debug("Size of minimum triangulation "+str(triangulation_mt["size"]))
	print("ok")

	# ===== Approximative Minimum Triangulation =====
	logging.info("===== TEST APPROX MINIMUM TRIANGULATION =====")
	print("TEST APPROX MINIMUM TRIANGULATION")
	triangulation_mta = MTA.triangulate_MTA(GRAPH_TEST.copy())
	logging.debug("Size of approximative minimum triangulation "+str(triangulation_mta["size"]))
	print("ok")

	# ===== Randomized Approximation Minimum Triangulation =====
	logging.info("===== TEST RANDOMIZED APPROXIMATION FOR MINIMUM TRIANGULATION =====")
	print("TEST RANDOMIZED APPROXIMATION FOR MINIMUM TRIANGULATION")
	triangulation_ramt = RAMT.triangulate_RAMT(GRAPH_TEST.copy())
	logging.debug("Size of rand. approx. for minimum triangulation "+str(triangulation_ramt["size"]))
	print("ok")