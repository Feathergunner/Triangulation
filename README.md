# Triangulation
Multiple algorithms for constructing a triangulation (i.e. chordal graph) from a given base graph.

Written in Python 3, using the package networkx 2.2.

Check out the jupyter notebook [TriangulationDemo](TriangulationDemo.ipynb).

## Content:

- experiments.py: main script to construct graphs and perform experiments.
- main_plots.py: Main scripts to construct plots and tables of evaluation data.
- tests.py: Basic unittests for most major methods.

### Triangulation Algorithms:
#### Feasible Algorithms that compute minimal triangulations:
- CMT.py: Create a minimal triangulation with the Clique Minimal Triangulation algorithm.
- EG.py: Create an arbitrary triangulation with the elimination game algorithm. Also contains a randomized version, and also a combined algorithm that minimizes a triangulation by EG with CMT.
- LEX_M.py: Create a minimal triangulation with the algorithm LEX-M. Also contains a randomized version.
- MCS_M.py: Create a minimal triangulation with the algorithm MCS-M. Also contains a randomized version.
- SMS.py: Create a minimal triangulation by saturating all minimal separators. Also contains a randomized version.
#### Algorithms with exponential complexity:
- MT.py: Create a minimum triangulation by checking all subsets of possible chord-edges.
#### Miscellaneous:
- TriangulationAlgorithm.py: A superclass for all of the triangulation algorithms above.
- graph_meta.py: a set of helper methods that are used in some of the algorithms.

### Evaluation:
- ExperimentManager.py: Datastructurs and Methods to evaluate runtime and results of the algorithms.
- GraphConstructionAlgorithms.py: Algorithms to construct different types of random graphs.
- GraphDataOrganizer.py: Datastructures and Methods to handle testdata.
- PlotConstructor.py: Methods to construct various plots that visualize the results of the experiments.
- StatisticsManager.py: Methods to organize the experiment data and compute some simple statistics.
- TableConstructor.py: Methods to construct tex-code of tables that display the results of the experiments.

### MetaScripts:
- global_settings.py: some global settings that define the scope of the experiments and the formatting of the plots and tables.
- meta.py: some minor helper methods.