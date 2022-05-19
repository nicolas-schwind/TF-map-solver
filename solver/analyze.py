from docplex.mp.model import Model
import re
from agent import *
from parser import *

import sys
import os


def help():
    print("USAGE: ./analyze.py INPUT_FILE")
    exit(1)


if len(sys.argv) <= 1 or sys.argv[1] in ["-h", "-help"]:
    help()

fileName = None
team = None
k = None

with open(sys.argv[1]) as f:
    lines = f.readlines()

    for line in lines:
        if re.search("instance=", line):
            fileName = line.replace("\n", "").split('=')[1]

        if re.search("team=", line):
            team = line.replace("\n", "").split('=')[1].split()

        if re.search("k=", line):
            k = int(line.replace("\n", "").split('=')[1])


assert k != None and team != None and fileName != None

# parse the file
nbAgents, nbSkills, mapOfAgents, mapOfSkills, eclauses = parse(fileName)


def computPercentageCoveredWorst(nbAgents, nbSkills, mapOfAgents, mapOfSkills, eclauses, k, team):
    """
    Attributes:
    ----------

    nbAgents : int
        the number of agents
    nbSkills : int
        the number of skills
    mapOfAgents : map
        for each id of agent we associate a structure that store data about it
    mapOfSkills : map
        for each id of skill we associate a structure that store data about it
    eclause : list
        each element containt an exclusion list
    k : int
        in the worst case we can lose k agents
    team : list(str)
        the list of agents that are in the current team

    Returns:
    -------

    the amount of skills that are covered whatever the k agents we lose
    """
    # init the model and create the variables.
    model = Model()
    agentsProp = [model.binary_var(str(i)) for i in range(nbAgents)]
    skillsProp = [model.binary_var(str(i + 1 + nbAgents))
                  for i in range(nbSkills)]

    # all the agents are lost
    if k >= len(team):
        return 0

    # we want to lose exactly k agent
    model.add_constraint(
        model.sum([agentsProp[mapOfAgents[a].id] for a in team]) == len(team) - k)

    # we check out the skills that are now still satisfied
    for a in team:
        # search for the agents that have the id 'a'
        agent = mapOfAgents[a]
        model.add_constraint(model.sum([-len(agent.l) * agentsProp[agent.id]] + [
                             skillsProp[mapOfSkills[s].id] for s in agent.l]) >= 0)

    # if a skill is activated then at least one agent must support it
    sumSkillsWeight = 0
    for s in mapOfSkills:
        sumSkillsWeight += mapOfSkills[s].w
        model.add_constraint(model.sum([-skillsProp[mapOfSkills[s].id]] + [
                             agentsProp[mapOfAgents[a].id] for a in mapOfSkills[s].l if a in team]) >= 0)

    # we want to minimize the weighted coverage of skills
    cost = model.sum([skillsProp[mapOfSkills[s].id] *
                     mapOfSkills[s].w for s in mapOfSkills])
    model.minimize(cost)
    solution = model.solve()

    assert solution != None
    return model.objective_value / sumSkillsWeight


def searchToCompleteTeam(team, lostAgent, nbAgents, nbSkills, mapOfAgents, mapOfSkills, eclauses):
    """
    Check out if we can restore the current team solListP1 once we lose the agent given in lostAgent.
    """
    """
    Check out if the solution found in phase 1 can be extended in phase 2.

    solPhase1 : list[str]
        the list of agents we are looking if they satisfy the rtf proterty
    lostAgent : list[str]
        the list of agents we are looking if we can lost them
    nbAgents : int
        the number of agents
    nbSkills : int
        the number of skills
    mapOfAgents : map
        for each id of agent we associate a structure that store data about it
    mapOfSkills : map
        for each id of skill we associate a structure that store data about it
    eclause : list
        each element containt an exclusion list
    k : int
        in the worst case we can lose k agents

    Returns:
    -------

    True if the given solution is correct, false otherwise.
    We also return the budget we need in the positive case.
    """
    lostSkills = []

    # get the skills we lost once the agents of lostAgent disappear
    for s in mapOfSkills:
        supported = False
        for a in set(mapOfSkills[s].l):
            if a in team and a not in lostAgent:
                supported = True
                break

        if(supported == False):
            lostSkills.append((s))

    # it remains satisfied
    if (len(lostSkills) == 0):
        return True, 0

    # create the model
    model = Model()
    agentsProp = [model.binary_var(str(i)) for i in range(nbAgents)]

    # collect the set of usable agents
    presentAgent = set()

    # the set of constraints that ensure that each skill is supported by at least one agent
    for s in lostSkills:
        # collect the set of possible agent that support the skill s
        possibleAgent = [agentsProp[mapOfAgents[a].id]
                         for a in mapOfSkills[s].l if a not in team and mapOfAgents[a].w2 != -1]

        # collect the agents
        for a in mapOfSkills[s].l:
            if a not in team and mapOfAgents[a].w2 != -1:
                presentAgent = presentAgent | set([a])

        # the team cannot be restored
        if len(possibleAgent) == 0:
            return False, 0

        # we add a constraint to ensure that s will cover in the solution
        model.add_constraint(model.sum(possibleAgent) >= 1)

    # integrity constraints
    for cl in eclauses:
        model.add_constraint(
            model.sum(agentsProp[mapOfAgents[cl[i]].id] for i in range(len(cl))) <= 1)

    # solver the min problem.
    cost = model.sum(agentsProp[mapOfAgents[a].id]
                     * mapOfAgents[a].w2 for a in presentAgent)
    model.minimize(cost)
    solution = model.solve()

    # if we cannot find out a solution with less or equal than the given budget
    if solution == None:
        return False, 0
    return True, model.objective_value


def computeRepairCost(nbAgents, nbSkills, mapOfAgents, mapOfSkills, eclauses, k, team):
    """
    Attributes:
    ----------

    nbAgents : int
        the number of agents
    nbSkills : int
        the number of skills
    mapOfAgents : map
        for each id of agent we associate a structure that store data about it
    mapOfSkills : map
        for each id of skill we associate a structure that store data about it
    eclause : list
        each element containt an exclusion list
    k : int
        in the worst case we can lose k agents
    team : list(str)
        the list of agents that are in the current team

    Returns:
    -------

    the cost to restore the coalition whatever the k agents we lose
    """
    remains = list(team)
    current = []
    stack = [[] for i in range(k)]

    worstCost = 0
    worstSkills = []

    if(k >= len(team)):
        return searchToCompleteTeam(team, team, nbAgents, nbSkills, mapOfAgents, mapOfSkills, eclauses)
    else:
        while len(remains) != 0:
            while len(remains) != 0:
                current.append(remains.pop(0))

                if len(current) == k:
                    res, val = searchToCompleteTeam(
                        team, current, nbAgents, nbSkills, mapOfAgents, mapOfSkills, eclauses)

                    if res == False:
                        return False, 0
                    elif worstCost < val:
                        worstCost = val

                    if k > 1:
                        stack[k-2].append(current.pop())
                    else:
                        current.pop()

            while(len(remains) == 0 and len(current) != 0):
                a = current.pop()
                if (len(current) != 0):
                    stack[len(current) - 1].append(a)
                remains = stack[len(current)]
                stack[len(current)] = []

    return True, worstCost


# print information about the probem
print("c Information on the problem: ")
print("c input file:", fileName)
print("c Number of agents:", nbAgents)
print("c Number of skills:", nbSkills)
print("c Number of clauses:", len(eclauses))

print("sol", end=" ")
cost = 0
for a in team:
    print(a, end=" ")
    cost += mapOfAgents[a].w1
print()

print("cost", cost)
print("percentage_covered_worst", computPercentageCoveredWorst(
    nbAgents, nbSkills, mapOfAgents, mapOfSkills, eclauses, k, team))

res, val = computeRepairCost(
    nbAgents, nbSkills, mapOfAgents, mapOfSkills, eclauses, k, team)
if not res:
    print("repair_cost", "infinity")
    print("total cost", "infinity")
else:
    print("repair_cost", val)
    print("total cost", cost + val)
