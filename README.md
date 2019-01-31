# Triangulation
Multiple algorithms for constructing a triangulation (i.e. chordal graph) from a given base graph.

Written in Python 3, using the package networkx 2.2.

Check out the jupyter notebook [TriangulationDemo](TriangulationDemo.ipynb).

## Content:

### Triangulation Algorithms:
#### Feasible Algorithms that compute minimal triangulations:
- EG.py: Create an arbitrary triangulation with the elimination game algorithm. Also contains a randomized version.
- SMS.py: Create a minimal triangulation by saturating all minimal separators. Also contains a randomized version.
- LEX_M.py: Create a minimal triangulation with the algorithm LEX-M. Also contains a randomized version.
- CMT.py: Create a minimal triangulation with the Clique Minimal Triangulation algorithm.
- RAMT.py: Randomized greedy search for a good triangulation.
#### Algorithms with exponential complexity:
- MT.py: Create a minimum triangulation by checking all subsets of possible chord-edges.
#### Unfinished algorithms:
- FMT.py: An unfinished FastMinimalTriangulation algorithm.

### Other Stuff:
- GraphConstructionAlgorithms.py: Algorithms to construct different types of random graphs
- GraphDataOrganizer.py: Datastructures and Methods to handle testdata
- ExperimentManager.py: Datastructurs and Methods to evaluate runtime and results of the algorithms.
- Tests.py: Basic unittests for most major methods.
