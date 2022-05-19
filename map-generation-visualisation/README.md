# Generation of instances based on the facility location problem

The Team Formation problem (TF) considers multiple individuals that match a required set of skills, and
consists in selecting a group of individuals that maximizes one or several social positive attributes.
This tool consists in generating structured TF instances modeling facility location problem instances.
Various types of instances can be generated according to a set of parameters.
The facility deployment problem consists in deploying a set of facilities (e.g., health centers, antennas, schools, shelters) on a populated map
so as to maximize a certain population coverage while minimizing the overall deployment cost.
The problem is of particular importance, e.g., for mobile phone operators which aim to deploy a set of cell towers in an urban environment.
In this context, finding an optimal efficient team corresponds to finding a facility deployment solution of minimal cost while providing a service coverage over
the whole population: facilities correspond to agents and the population to be covered in a certain area
corresponds to a weighted skill, where the weight depends on the density of the population at that specific location.
Indeed, this type of problems is perfectly suitable from the partial/full robustness analysis viewpoint:
when a number of cell towers suddenly becomes unfunctional,
one wants to ensure that a certain high percentage of the population is still provided with an access to the network before recovery.

For each generated instance, four files are generated:

* a .ppm file: a text file that can be also viewed as a two-dimensional colored grid representing the elevation map (each color ranges over [0, 255])
* a .png file: a hexagonal grid based on the .ppm file for visualizating the populated map
* a .tf file: the translation of the populated map into a TF instance: this is the actual instance file, similar to the DIMACS format, that can be used as an input for solving (TF, RecTF, RobTF, PRTF)
* a .info file: some additional information linking the map and the instance, e.g., the coordinate of each agent on the grid. This is used if one wants to represent a team on the map, where that said team corresponds to the solution according to one of the solution concepts above, for instance.

## Initialization

```console
$ pipenv install
$ pipenv shell
```

## Simple usage

The python file to execute is generate.py.

The only mandatory parameter is the base name of the instance:

* -f FILE_NAME

The following example generates a single map instance with base name 'my_map' and default parameters.

```console
$ python3.9 generate_map.py -f my_map
Parameters for map generation:
--> FILE_NAME = my_map
--> NB_INSTANCES = 1
--> RESOLUTION = 3
--> COMPLEXITY = 1
--> NB_CITIES = 4
--> TOTAL_POPULATION = 256
--> LOCAL_MAX_POPULATION = 20
--> NEIGHBORHOOD_PARSING = 3
--> LIST_FACILITY_COSTS = [1, 2, 3, 4]

****************************************
generation instance #1...
-> elevation map generation... 100%
-> preprocessing the map before populating... 100%
-> populating the map... 100%
-> converting map into Team Formation instance (agents and skills)... 100%
-> converting map into Team Formation instance (linking agents to skills)... 100%
instance #1 generated (instance name: my_map-1)
--> nb of agents: 562
--> nb of skills: 78
****************************************
```

Thus running this command generates four file, namely my_map-1.ppm, my_map-1.png, my_map-1.tf, and my_map-1.info.
This instance is available in the directory instances-examples.

## Optional parameters

Additional parameters can be used to tune the structure of the map, e.g., its size, the variation of the elevation, the way it is populated, the number of desired instances, etc.
To get a list of all optional parameters:

```console
$ python3.9 generate_map.py -h
usage: generate_map.py [-h] -f FILE_NAME [-n NB_INSTANCES] [-r RESOLUTION] [-c COMPLEXITY] [-l LOCAL_MAX_POPULATION] [-t NB_CITIES] [-p TOTAL_POPULATION] [-d NEIGHBORHOOD_PARSING] [-a LIST_FACILITY_COSTS [LIST_FACILITY_COSTS ...]]

optional arguments:
-h, --help            show this help message and exit
-f FILE_NAME, --file_name FILE_NAME
-n NB_INSTANCES, --nb_instances NB_INSTANCES
-r RESOLUTION, --resolution RESOLUTION
-c COMPLEXITY, --complexity COMPLEXITY
-l LOCAL_MAX_POPULATION, --local_max_population LOCAL_MAX_POPULATION
-t NB_CITIES, --nb_cities NB_CITIES
-p TOTAL_POPULATION, --total_population TOTAL_POPULATION
-d NEIGHBORHOOD_PARSING, --neighborhood_parsing NEIGHBORHOOD_PARSING
-a LIST_FACILITY_COSTS [LIST_FACILITY_COSTS ...], --list_facility_costs LIST_FACILITY_COSTS [LIST_FACILITY_COSTS ...]
```

List of optional parameters:

* -n NB_INSTANCES: the number desired instances based on the remaining parameters

The following two parameters are related to the generation of the elevation map before being populated:

* -r RESOLUTION: an integer within range [1, 7] that determines the size of the map
* -c COMPLEXITY: an integer within range [1, 4]. The higher the value c, the shorter the variation of the map in terms of elevation.

Given these two parameters, an n x n map is generated, with n = 2^{r+1}.
The grid is interpreted as follows: each cell is associated with a 'type' depending on its value in the grid.
A low (resp., mid, high) value is interpreted as a water cell (resp., a land cell, a mountain cell).

The following parameters are related to the population of the map. If not specified, these parameters are set with a default value which directly depend on the two previous parameters RESOLUTION and COMPLEXITY:

* -l LOCAL_MAX_POPULATION: the maximum density, i.e., the maximum number of inhabitants in the same cell
* -t NB_CITIES: an integer specifying the number of 'starting cities', i.e., the number of cells used as a starting point for populating
* -p TOTAL_POPULATION: the total number of inhabitants in the map
* -d NEIGHBORHOOD_PARSING: the distance within which a new inhabitant can be added nearby an already populated cell. The higher the value d, the more spread out the population on the map.

Thus, initially t individuals are added in t different land cells randomly chosen, provided that the cell is next to a water cell. Then, a new individual is added at random following a probability distribution that depends on d and such that the closer to an already populated cell, the higher its probability to welcome a new individual.
The water cells and the cells that already host l individuals cannot host a new individual.
The process is repeated p times which at last corresponds to the total population in the map.
Blue (resp. brown, white) cells are of water type (resp. land, mountain type). Different scales
of brown correspond to different elevation degrees of land, only used to tune the probability of adding an individual to a land cell.
The gray scales represent the number of individuals in a cell. The darker a cell, the more densely populated, so a pitch black cell contains l individuals.

Lastly, the following parameter is used to select the types of facilities that one wants to be considered in the .tf instance. This is only reflected in the .tf instance, not on the generated map:

* -a LIST_FACILITY_COSTS: a list of numbers ranging in [1, 10] describing the type of each facility to be used as candidate agents to be deployed on the map. A facility of type i has a deployment cost i and a cover range of i-1, i.e., if deployed on a cell C, it provides the required service to anyone that is in a cell C' such that the distance between C and C' is at most i-1.

## Examples

The following generates 3 instances, named map-r4-1, map-r4-2, map-r4-3, each of which associated with four files (.ppm, .png, .tf, .info), thus generating 12 files.
Each instance has a RESOLUTION 4 and a COMPLEXITY 2. The remaining parameters are set by default according to RESOLUTION and COMPLEXITY.

```console
$ python3.9 generate_map.py -f map-r4 -n 3 -r 4 -c 2
Parameters for map generation:
--> FILE_NAME = map-r4
--> NB_INSTANCES = 3
--> RESOLUTION = 4
--> COMPLEXITY = 2
--> NB_CITIES = 7
--> TOTAL_POPULATION = 1024
--> LOCAL_MAX_POPULATION = 20
--> NEIGHBORHOOD_PARSING = 4
--> LIST_FACILITY_COSTS = [1, 3, 5]

****************************************
generation instance #1...
-> elevation map generation... 100%
-> preprocessing the map before populating... 100%
-> populating the map... 100%
-> converting map into Team Formation instance (agents and skills)... 100%
-> converting map into Team Formation instance (linking agents to skills)... 100%
instance #1 generated (instance name: map-r4-1)
--> nb of agents: 1526
--> nb of skills: 268
****************************************

****************************************
generation instance #2...
-> elevation map generation... 100%
-> preprocessing the map before populating... 100%
-> populating the map... 100%
-> converting map into Team Formation instance (agents and skills)... 100%
-> converting map into Team Formation instance (linking agents to skills)... 100%
instance #2 generated (instance name: map-r4-2)
--> nb of agents: 1900
--> nb of skills: 375
****************************************

****************************************
generation instance #3...
-> elevation map generation... 100%
-> preprocessing the map before populating... 100%
-> populating the map... 100%
-> converting map into Team Formation instance (agents and skills)... 100%
-> converting map into Team Formation instance (linking agents to skills)... 100%
instance #3 generated (instance name: map-r4-3)
--> nb of agents: 1325
--> nb of skills: 269
****************************************
```

The following generates one instance, named another_map-1, with all parameters specified.
This instance is available in the directory instances-examples.

```console
$ python3.9 generate_map.py -f another_map -r 5 -c 4 -t 10 -p 5000 -l 25 -d 3 -a 1 3 5 7
Parameters for map generation:
--> FILE_NAME = another_map
--> NB_INSTANCES = 1
--> RESOLUTION = 5
--> COMPLEXITY = 4
--> NB_CITIES = 10
--> TOTAL_POPULATION = 5000
--> LOCAL_MAX_POPULATION = 25
--> NEIGHBORHOOD_PARSING = 3
--> LIST_FACILITY_COSTS = [1, 3, 5, 7]

****************************************
generation instance #1...
-> elevation map generation... 100%
-> preprocessing the map before populating... 100%
-> populating the map... 100%
-> converting map into Team Formation instance (agents and skills)... 100%
-> converting map into Team Formation instance (linking agents to skills)... 100%
instance #1 generated (instance name: another_map-1)
--> nb of agents: 5627
--> nb of skills: 691
****************************************
```

## How the .tf file (the TF instance) is generated

For each type of facility i and each grid cell C that is not of water type,
one considers an agent a_i^C of cost f(a_i^C) = i which corresponds to a facility of type i to be potentially deployed in the cell C.
This defines the set A of agents and the cost function f.
The set of skills S and the skill weight function w_\Sigma (we considered a normalized weighted sum function)
are simply defined as follows.
One associates with each populated grid cell P (i.e., a cell that hosts at least one individual)
a skill s_P; and the weight of each skill w_\Sigma(s_P) is defined as the number of individuals in the grid cell P.
Then, the agent-to-skill mapping \alpha is defined as follows. An agent a_i^C has the skill s_P if the grid
cell P is within the reach of the facility a_i^C, i.e., if the distance between
the grid cells C and P is less than or equal to i-1.
Lastly, we have added for each instance a set of constraints forbidding the joint deployment of two facilities a_i^C, a_j^C located at the same cell C.

The generated .tf file is similar to the DIMACS format.
IT begins with a header line of the form p <#agents> <#skills>,
where <#agents> and <#skills> are respectively integers indicating the number of agents and skills in the TF formulation of the map.
Agents will be given by lines of the form a <id_agent> <cost_deployment> <cost_repair> <list_of_skills>.
Where <id_agent>, <cost_deployment>, <cost_repair> and <list_of_skills> represent respectively
the agent ID, the initial deployment cost of the agent, the deployment cost of the agent when it is considered
to replace a defective agent, and the list of skills supported by the agent.
Skills will be given by lines of the form s <id_skill> <weight_skill>,
where <id_skill> and <weight_skill> respectively correspond to the skill ID and the weight of the skill (the number of inhabitants in the cell represented by that skill).
Finally, forbidding the joint deployment of facilities located at the same cell is done
by adding lines of the form e <id_agent1>, ... where each <id_agenti> is an agent identifier.

## How to visualize a solution on the map once computed

This tool generates a .png file representing a deployment of facilities on a map, given a given map and a solution for this map.
To generate such visualization, one needs the <instance_name>.ppm and <instance_name>.info files obtained when when the map was generated.
A solution consists of a file <instance_name>.<arbitrary_solution_description>.sol, that must contain a line of the form: sol <list_agent_ids>,
Where list_agent_ids is a series of agent identifiers corresponding in the original .tf file to the agents selected in the solution.

Hence, if the two files <instance_name>.ppm and <instance_name>.info exist in the directory together with a file <instance_name>.<arbitrary_solution_description>.sol, then
a file <instance_name>.<arbitrary_solution_description>.png will be generated representing the solution team on the map.

Several .sol files can exist for the same instance, in that case a .png file will be generated for each .sol file.

The python file to execute is visualise_solution.py.

The following example was executed on the directory instance-examples. This directory, together with the map examples generated above, also contains an instance named r3-default-1 with three solutions files:

```console
$ python3.9 visualise_solution.py instances-examples/
all instance names: ['map-r4-1', 'map-r4-3', 'another_map-1', 'map-r4-2', 'r3-default-1', 'my_map-1']
nb potential instances: 6
--> dealing with instance map-r4-1
    --> valid instance (has .ppm and .info files)
    --> no solution found for this instance
--> dealing with instance map-r4-3
    --> valid instance (has .ppm and .info files)
    --> no solution found for this instance
--> dealing with instance another_map-1
    --> valid instance (has .ppm and .info files)
    --> no solution found for this instance
--> dealing with instance map-r4-2
    --> valid instance (has .ppm and .info files)
    --> no solution found for this instance
--> dealing with instance r3-default-1
    --> valid instance (has .ppm and .info files)
    --> treatment of solution r3-default-1.KTF-k2.sol
    --> png file generated!
    --> treatment of solution r3-default-1.PTF_ANYTIME-k2-t99-CUT+.sol
    --> png file generated!
    --> treatment of solution r3-default-1.PTF_ANYTIME-k1-t90-CUT.sol
    --> png file generated!
    --> treatment of solution r3-default-1.TF.sol
    --> png file generated!
--> dealing with instance my_map-1
    --> valid instance (has .ppm and .info files)
    --> no solution found for this instance
```
