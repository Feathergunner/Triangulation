# Triangulation
Multiple algorithms for constructing a triangulation (i.e. chordal graph) from a given base graph.

Written in Python 3, using the package networkx 2.2.

Check the jupyter notebook [TriangulationDemo](TriangulationDemo.ipynb).

## Content:

### Triangulation Algorithms:
- EG.py: Create an arbitrary triangulation with the elimination game algorithm. Also contains a randomized version.
- LEX_M.py: Create a minimal triangulation with the algorithm LEX-M. Also contains a randomized version.
- MT.py: Create a minimum triangulation by checking all subsets of possible chord-edges.
- Random_Approx_MT: Randomized search for a good triangulation.

### Other Stuff:
- GraphConstructionAlgorithms.py: Algorithms to construct different types of random graphs
- GraphDataOrganizer.py: Datastructures and Methods to handle test- and evaluation data
- Tests.py: Basic unittests for most major methods.
