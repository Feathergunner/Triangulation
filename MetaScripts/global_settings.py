# graph parameters:
GRAPH_SIZES = [20, 40, 60, 80, 100]
GRAPH_DENSITIY_P = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]

PLANAR_DENSITY_RELM = [1.5, 1.75, 2.0, 2.25, 2.5]

BOUNDEDGRAPHS_DENSITY_P = [0.1, 0.2, 0.3, 0.4, 0.5]
MAXDEGREE_SETTINGS = [3, 5, 10]
MAXCLIQUE_SETTINGS = [3, 4, 5]

# algorithm parameters:
RANDOMIZED_REPETITIONS = [3, 5, 10]
TIMELIMIT = 2

# plotting settings:
PLT_ALGO_COLORS = {
	"EG" : 'b',
	"EGPLUS" : 'c',
	"SMS" : 'g',
	"LexM" : 'm', 
	"MCSM" : '#ffa400', # orange
	"CMT" : 'r', 
	"MT" : 'k' # black
}

PLT_GRAPHSIZE_COLORS = {
	"n20" : 'b',
	"n40" : 'c',
	"n60" : 'g',
	"n80" : 'm',
	"n100" : 'r'
}