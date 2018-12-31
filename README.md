# Triangulation
Multiple algorithms for constructing a triangulation (i.e. chordal graph) from a given base graph.

Written in Python 3, using the package networkx 2.2.

Check the jupyter notebook [TriangulationDemo](TriangulationDemo.ipynb).

## Content:

### Triangulation Algorithms:
- EG.py: Create an arbitrary Triangulation with the elimination game algorithm.
- LEX_M.py: Create a minimal Triangulation with the algorithm LEX-M.
- MT.py: Create a minimum Triangulation by checking all subsets of possible chord-edges (not yet fully implemented).

### Other Stuff:
- GraphConstructionAlgorithms.py: Algorithms to construct different types of random graphs
- GraphDataOrganizer.py: Datastructures and Methods to handle test- and evaluation data