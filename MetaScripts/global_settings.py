# graph parameters:
# defines major graph classes. Each class will be evaluated separately.
GRAPH_CLASSES = ["general", "planar", "maxdeg", "maxclique"]

# defines the numbers of nodes:
GRAPH_SIZES = [20, 40, 60, 80, 100]

# defines the relative edge-probability p for dense graphs constructed by the erdös-renyi-model:
GRAPH_DENSITIY_P = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
# defines the relative amount of edges for sparse graphs as multiple of n:
SPARSE_DENSITY_RELM = [1.5, 1.75, 2.0, 2.25, 2.5]

# defines the parameter maximum_degree for the class of graphs with bounded degree:
MAXDEGREE_SETTINGS = [5]#[3, 5, 10]
# defines the parameter maximum_clique_size for the class of graphs with bounded clique size:
MAXCLIQUE_SETTINGS = [4]#[3, 4, 5]


# algorithm parameters:
# defines the number of randomized repetitions for randomized algorithms:
RANDOMIZED_REPETITIONS = [3, 5, 10]

# experiment settings:
# defines the maximum time in second before an algorithm is stopped without result:
TIMELIMIT = 4
# defines the number of threads used for parallel experiments:
MAX_NUM_THREADS = 10
# defines all algorithms, this is used by some of the experiment and evaluation scripts:
BASE_ALGO_CODES = ["EG", "EGPLUS", "SMS", "LexM", "MCSM", "CMT", "MT"]

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

PLT_DPI = 500

# misc:
EASTER_EGG = "{\\tiny \\color{white} BATMAN!}"