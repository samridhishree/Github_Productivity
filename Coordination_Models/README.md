# Computing Project Coordination

This folder contains an implementation of Socio-Technical Congruence adapted for GitHub projects along with the helper scripts needed to produce intermediate results. The details can be found in the paper. The sequence of running the scripts, along with a detailed description of its functionality can be found below. For details on the parameters needed to run each script, please look at the respective files.

## Dependencies
1. __Pandas__: https://pandas.pydata.org/
2. __Numpy__: http://www.numpy.org/
3. __NetworkX__: https://networkx.github.io/
4. __Community__: https://pypi.python.org/pypi/python-louvain/0.3


## Execution Steps
The execution is divided into three phases:
1. Pre-processing
2. Helper Structures
3. Congruence Computation

### Pre-processing
----
1. __*Extract bursty commits*__: This step groups together the commits that occur in a burst.
> Script: __extract_burst_commits.py__
2. __*Extract bursty issues*__: This step groups together the active issues per burst per project.
> Script: __extract_burst_issues.py__

### Helper Structures
---
1. __*Compute Pairwise Co-commit Frequency*__: Generates all the pair of files that are committed together along with the number of times that they are committed together.
> Script: __file_co_commit.py__
2. __*Co-commit Graph*__: Uses the pairwise co-commit counts built above to generate a co-commit graph for the project.
> Script: __build_co_commit_graph.py__
3. __*File Module Membership*__: Partitions the co-commit graphs built above to get clusters/modules of highly interdependent files. Computes the module class membership for each file and pickles it.
> Script: __file_module_dict.py__
4. __*User File Membership*__: Creates a dictionary of the list of files committed by the people in the project. Pickles the resultant dictionary per project.
> Script: __people_file_dict.py__
5. __*User Module Membership*__: Looks at the files committed by a person and then links it to the module number that the file belongs to. This transitive relation is stored as a dictionary containing people-module membership per project.
> Script: __people_module_dict.py__
6. __*User Component Experience*__: Calculates the component experience of the people in a project per burst.
> Script: __people_component_experience.py__
7. __*Reformat Co-commit Adjacency*__: Reformats the pairwise co-commit counts to a 2D adjacency matrix representation. 
> Script: __reformat_adjacency.py__

### Congruence Computation
---
1. __*Socio-Technical Congruence*__: Implementation of Socio-Technical Congruence Measure introduced by: "_Cataldo, Marcelo, et al. __"Identification of coordination requirements: implications for the Design of collaboration and awareness tools."__ Proceedings of the 2006 20th anniversary conference on Computer supported cooperative work. ACM, 2006._"
> Script: __burst_congruence.py__

2. __*Generate the final table*__: Generates the final table that acts as in input to the linear regression model by concatenating the individual project files.
> Script: __combine_congruence_data.py__

