# Dream Team

The Team Formation problem (TF) considers multiple individuals that match a required set of skills, and
consists in selecting a group of individuals that maximizes one or several social positive attributes.
Additionally to the team formation problem, this tool has been designed to compute teams in the case
where some of the agents considered at start may be finally defective and some skills may become uncovered.
More precisely, we are able to handle the following problems:

* TF: search for an efficient team, that is a team such that all skills are covered;
* RobTF(k): search for a robust team for a given integer k, that is a team so that after k agent losses, all skills remain covered;
* RecTF(k): search for a recoverable team for a given integer k, that is a team so that after k agent losses, all skills can be covered by repairing the team while keeping the overall deployment cost minimal (by hiring new agents if required);
* PRTF(k, t): search for a partial robust team for a given integer k and a threshold t,
that is an efficient team, and if after removing k agents from it, the residual team covers at least t% of the set
of all skills.

## How to init

You first need to install CPLEX from the official website, and then
update the PYTHONPATH in a such a way:

```console
export PYTHONPATH=/opt/ibm/ILOG/CPLEX_Studio201/cplex/python/3.7/x86-64_linux/
```

Additionally you also need *docplex*. If you use Anaconda you can use the *dream_team.yml* file to set up your environment (warning: take care of the python version of your cplex version).

```console
$ conda env create -f dream_team.yml
$ conda activate dream_team
(dream_team) $ python main.py --help
usage: main.py [-h] [--inputFile inputFile] [--method method [method ...]]
               [--cut cut]

dreamTeam is a tool to build good teams!

optional arguments:
  -h, --help            show this help message and exit
  --inputFile inputFile
                        the input file following the tf format (see README).
  --method method [method ...]
                        the method used (tf, ktf k, ptf k t, dptf k t, rtf).
  --cut cut             the cut level (0 = no cut, 1 = simple cut or 2 =
                        multiple cut

$ conda deactivate 
```

## Input File Format

To represent a TF instance we use something similar to the DIMACS format.
A file begins with a header line of the form **p <#agents> <#skills>**.
Where **<#agents>** and **<#skills>** are replaced with decimal numbers indicating the number of agents and skills
in the TF formulation. Lines starting with character **c** are comments and can occur anywhere in the file.
Agents will be given by lines of the form **a <id_agent> <cost_deployment> <cost_repair> <list_of_skills>**.
Where **<id_agent>**, **<cost_deployment>**, **<cost_repair>** and **<list_of_skills>** represent respectively
the agent ID, the initial deployment cost of the agent, the deployment cost of the agent when it is considered
to replace a defective agent, and the list of skills supported by the agent.
Skills will be given by lines of the form **s <id_skill> <weight_skill>**.
Where **<id_skill>** and **<weight_skill>** respectively correspond to the skill ID and the weight of the skill.
Finally, it is also possible to enforce binary constraints that allow for avoiding some combination of agents
by adding lines of the form **e <id_agent1> <id_agent2>**.
Where **<id_agent1>** and **<id_agent2>** are two agent identifiers. Here is an example of TF benchmark:

```console
$ cat r1-default-1.tf
c comments
p 16 6
a 0 1 1 0
a 1 2 -1 0 1 3
a 2 1 1 1
a 3 2 -1 0 1 2 3 4
a 4 1 1 2
a 5 2 -1 1 2 4
a 6 1 1 3
a 7 2 -1 0 1 3 4 5
a 8 1 1 4
a 9 2 -1 1 2 3 4
a 10 2 -1 2 4
a 11 1 1 5
a 12 2 -1 3 5
a 13 2 -1 3 4 5
a 14 2 -1 4
a 15 2 -1 5
s 0 5
s 1 2
s 2 1
s 3 7
s 4 1
s 5 1
e 0 1
e 2 3
e 4 5
e 6 7
e 8 9
e 11 12
```


## How to run TF

To search for efficient team please use the following command line.

```console
(dream_team) $ python main.py --inputFile r1-default-1.tf --method tf
c Dream Team in construction:
c Method we run: ['tf', 0]
c input file: r1-default-1.tf
c Information on the problem: 
c Number of agents: 16
c Number of skills: 6
c Number of clauses: 6
c [FACTORY] Method:  tf
c Run TF:  [0]
s 4 7 
o 3
t 0.07737970352172852
```

The output gives information about what has been solved and it also gives the team
(line starting with the character **s**), the cost of the optimal team
(line starting with the character **o**) and the time needed to compute this team
(line starting with the character **t**).

## How to run RobTF(k)

```console
(dream_team) $ python main.py --inputFile r1-default-1.tf --method ktf 2
c Dream Team in construction:
c Method we run: ['ktf', '2', 0]
c input file: r1-default-1.tf
c Information on the problem: 
c Number of agents: 16
c Number of skills: 6
c Number of clauses: 6
c [FACTORY] Method:  ktf
c Run ktf: ['2', 0]
s 0 3 4 7 9 11 13 
o 11
t 0.07725667953491211
```

As for the previous example, the output gives information about what has been solved and it also gives 
at the end the team (line starting with the character **s**), the cost of the optimal team
(line starting with the character **o**) and the time needed to compute this team
(line starting with the character **t**).

## How to run RecTF(k)

```console
(dream_team) $ python main.py --inputFile r1-default-1.tf --method rtf 2 --cut 1

c Dream Team in construction:
c Method we run: ['rtf', '2', 1]
c input file: r1-default-1.tf
c Information on the problem: 
c Number of agents: 16
c Number of skills: 6
c Number of clauses: 6
c [FACTORY] Method:  rtf
c k: 2
c cut: True
1 27 [4, 7] 3
2 27 [3, 11] 3
3 27 [3, 7] 4
i 10.0 ['3', '7']
4 10.0 [5, 7] 4
5 10.0 [7, 9] 4
6 10.0 [3, 13] 4
7 10.0 [7, 10] 4
8 10.0 [3, 12] 4
9 10.0 [3, 15] 4
10 10.0 [0, 3, 7] 5
11 10.0 [3, 4, 7] 5
12 10.0 [0, 7, 9] 5
13 10.0 [1, 5, 7] 6
i 9.0 ['1', '5', '7']
14 9.0 [1, 10, 15] 6
15 9.0 [1, 5, 13] 6
16 9.0 [3, 5, 15] 6
17 9.0 [3, 9, 15] 6
18 9.0 [3, 9, 12] 6
19 9.0 [3, 5, 7] 6
20 9.0 [3, 7, 9] 6
i 8.0 ['3', '7', '9']
21 8.0 [1, 9, 12] 6
22 8.0 [1, 5, 15] 6
23 8.0 [1, 5, 12] 6
24 8.0 [1, 7, 9] 6
25 8.0 [1, 10, 13] 6
26 8.0 [3, 10, 13] 6
27 8.0 [3, 9, 13] 6
28 8.0 [3, 5, 13] 6
29 8.0 [1, 7, 10] 6
30 8.0 [3, 7, 10] 6
31 8.0 [1, 9, 13] 6
32 8.0 [1, 5, 7, 8] 7
33 8.0 [3, 5, 7, 8] 7
34 8.0 [3, 7, 9, 11] 7
35 8.0 [1, 2, 10, 13] 7
36 8.0 [0, 3, 5, 15] 7
37 8.0 [1, 5, 11, 13] 7
38 8.0 [1, 2, 5, 15] 7
39 8.0 [1, 2, 5, 13] 7
40 8.0 [1, 2, 9, 13] 7
41 8.0 [1, 4, 9, 13] 7
c Number of iterations: 42
s 3 7 9 
o 8
t 1.5027105808258057
```

As for the previous examples, the output gives information about what has been solved and it also gives
at the end the team (line starting with the character **s**), the cost of the optimal team
(line starting with the character **o**) and the time needed to compute this team
(line starting with the character **t**).


## How to run PRTF(k,t)

There exists two approaches to compute partially robust teams. The first one consists in
incrementally starting from the most efficient team and then test if the team is robust.
The following command line search for a team where two agents can be defective and where
the want to satisfy at least 90% of the skills whatever the agent lost.

```console
(dream_team) $ python main.py --inputFile r1-default-1.tf --method ptf 2 90 --cut 2
c Dream Team in construction:
c Method we run: ['ptf', '2', '90', 2]
c input file: r1-default-1.tf
c Information on the problem: 
c Number of agents: 16
c Number of skills: 6
c Number of clauses: 6
c [FACTORY] Method:  ptf
c Run ptf: ['2', '90', 2]
c The sum of the weight is: 17
c The quantity of weighted skills satisfied must be at least: 16
1 ['4', '7'] 3
2 ['0', '3', '7', '9'] 7
c Number of iterations: 2
s 0 3 7 9 
o 7
t 0.11099791526794434
```

As for the previous examples, the output gives information about what has been solved and it also gives
at the end the team (line starting with the character **s**), the cost of the optimal team
(line starting with the character **o**) and the time needed to compute this team
(line starting with the character **t**). We also report team tested as candidate for being robust
(**<cpt> <list_agent> <cost>**).

It is also possible to search for a team that is better than the upper bound (without searching in computing the
most efficient team) and then updating the upper bound. We stop when no better team can be found.
Again, with the following command line, we search for a team where two agents can be defective and where
we want to satisfy at least 90% of the skills whatever the agent lost.

```console
(dream_team) $ python main.py --inputFile r1-default-1.tf --method dptf 2 90 --cut 2
c Dream Team in construction:
c Method we run: ['dptf', '2', '90', 2]
c input file: r1-default-1.tf
c Information on the problem: 
c Number of agents: 16
c Number of skills: 6
c Number of clauses: 6
c [FACTORY] Method:  dptf
c Run decision ptf: ['2', '90', 2]
c [FACTORY] Method:  tf
c Compute the best possible team: 3
c [FACTORY] Method:  ktf
c Compute the worst possible team: 27
c The sum of the weight is: 17
c The quantity of weighted skills satisfied must be at least: 16
b Current bounds: 3 27
b Current bounds: 3 26
p 1 3 5 7 
o 8
t 0.13973736763000488
b Current bounds: 3 7
p 0 3 7 9 
o 7
t 0.18639063835144043
b Current bounds: 7 7 7
t 0.19492506980895996
c Number of iterations: 6
s 0 3 7 9 
o 7
t 0.1952223777770996
```

As for the previous examples, the output gives information about what has been solved and it also gives at the end
the team (line starting with the character **s**), the cost of the optimal team
(line starting with the character **o**) and the time needed to compute this team
(line starting with the character **t**). We also report team tested as candidate for being robust
(**<cpt> <list_agent> <cost>**). Additionally, because this approach is incremental, it is also reported
intermediate solution. We consider blocks of three lines starting with the line that commences with a character **p**
and that gives the intermediate team, following by the cost of the intermediate team and finishing with the time
needed to compute this team.
