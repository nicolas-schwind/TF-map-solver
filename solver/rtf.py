"""
This file is part of dreamTeam.

dreamTeam is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Foobar is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Foobar.  If not, see <https://www.gnu.org/licenses/>.
"""
from docplex.mp.model import Model
from solver import Solver


class RTf(Solver):
    """
    Rtf solver.
    """

    def createTheInitialFirstPlayerModel(self, problem):
        """
        Solve the problem of computing a rtf coalition using an iterative approach.
        Attributes:
        ----------
        problem : Problem
            the problem we want to modelize.

        Returns:
        -------
        the set of variables and the model
        """
        model = Model()
        agentsProp = [model.binary_var(str(i))
                      for i in range(problem.nbAgents)]

        # the set of constraints that ensure that each skill is supported by at least one agent
        for s in problem.mapOfSkills:
            model.add_constraint(
                model.sum(agentsProp[problem.mapOfAgents[a].id]
                          for a in problem.mapOfSkills[s].l) >= 1)

        # integrity constraints
        for cl in problem.eclauses:
            model.add_constraint(
                model.sum(agentsProp[problem.mapOfAgents[cl[i]].id]
                          for i in range(len(cl))) <= 1)

        # the function we search to minimize
        cost = model.sum(agentsProp[problem.mapOfAgents[a].id]
                         * problem.mapOfAgents[a].w1 for a in problem.mapOfAgents)

        model.minimize(cost)
        return agentsProp, model

    def computeWorstCase(self, mapOfAgents):
        """
        Go throw the set of agent and return the worst case in term of team.

        Attributes:
        ----------
        mapOfAgents : map
            for each id of agent we associate a structure that store data about it

        Returns:
        -------
        The worst case in term of weight.
        """
        tmp = 0
        for a in mapOfAgents:
            if mapOfAgents[a].w1 < 0 and mapOfAgents[a].w2 < 0:
                continue
            if mapOfAgents[a].w1 > mapOfAgents[a].w2:
                tmp += mapOfAgents[a].w1
            else:
                tmp += mapOfAgents[a].w2
        return tmp

    def searchToCompleteTeam(self, solListP1, lostAgent, problem, budget):
        """
        Check out if the solution found in phase 1 can be extended in phase 2.

        solPhase1 : list[str]
            the list of agents we are looking if they satisfy the rtf proterty.
        lostAgent : list[str]
            the list of agents we are looking if we can lost them.
        probme : Problem
            the problem we are modelizing.
        budget:
            the maximum cost for the rescue team

        Returns:
        -------
        True if the given solution is correct, false otherwise. Moreover, in the case where
        the given team is not a good candidate, then we return a set of agents if we lost
        them then we cannot restore with the given budget.
        """
        lostSkills = []

        # get the skills we lost once the agents of lostAgent disappear
        for s in problem.mapOfSkills:
            supported = False
            for a in set(problem.mapOfSkills[s].l):
                if problem.mapOfAgents[a].id in solListP1\
                        and problem.mapOfAgents[a].id not in lostAgent:
                    supported = True
                    break

            if supported is False:
                lostSkills.append((s))

        # it remains satisfied
        if len(lostSkills) == 0:
            return True, 0, []

        # create the model
        model = Model()
        agentsProp = [model.binary_var(str(i))
                      for i in range(problem.nbAgents)]

        # collect the set of usable agents
        presentAgent = set()

        # the set of constraints that ensure that each skill is supported by at least one agent
        for s in lostSkills:
            # collect the set of possible agent that support the skill s
            possibleAgent = [agentsProp[problem.mapOfAgents[a].id]
                             for a in problem.mapOfSkills[s].l
                             if problem.mapOfAgents[a].id not in solListP1
                             and problem.mapOfAgents[a].w2 != -1]

            # collect the agents
            for a in problem.mapOfSkills[s].l:
                if problem.mapOfAgents[a].id not in solListP1 and problem.mapOfAgents[a].w2 != -1:
                    presentAgent = presentAgent | set([a])

            # the team cannot be restored
            if len(possibleAgent) == 0:
                return False, 0, [s]

            # we add a constraint to ensure that s will cover in the solution
            model.add_constraint(model.sum(possibleAgent) >= 1)

        # integrity constraints
        for cl in problem.eclauses:
            model.add_constraint(
                model.sum(agentsProp[problem.mapOfAgents[cl[i]].id] for i in range(len(cl))) <= 1)

        # we want a solution with a cost less than the budget
        model.add_constraint(model.sum(
            agentsProp[problem.mapOfAgents[a].id] * problem.mapOfAgents[a].w2
            for a in presentAgent) <= budget)

        # solver the min problem.
        cost = model.sum(agentsProp[problem.mapOfAgents[a].id]
                         * problem.mapOfAgents[a].w2 for a in presentAgent)
        model.minimize(cost)
        solution = model.solve()

        # if we cannot find out a solution with less or equal than the given budget
        if solution is None:
            return False, 0, lostSkills
        return True, model.objective_value, lostSkills

    def canSecondPlayerRestoreInAllCases(self, solPhase1, problem, k, budget):
        """
        Check out if the solution found in phase 1 can be extended in phase 2.

        solPhase1 : list[str]
            the list of agents we are looking if they satisfy the ptf proterty.
        problem : Problem
            the problem we are modelizing.
        k : int
            in the worst case we can lose k agents.
        budget:
            the cost of the given team.

        Returns:
        -------
        True if the given solution is correct, false otherwise. Moreover, in the case where
        the given team is not a good candidate, then we return a set of agents if we lost
        them then we cannot restore with the given budget.
        """
        remains = list(solPhase1)
        current = []
        stack = [[] for i in range(k)]

        worstCost = 0
        if k >= len(solPhase1):
            res, val, lostSkills = self.searchToCompleteTeam(
                solPhase1, solPhase1, problem, budget)
            if res is False or val > budget:
                return False, val, lostSkills
            else:
                return True, val, None
        else:
            while len(remains) != 0:
                while len(remains) != 0:
                    current.append(remains.pop(0))

                    if len(current) == k:
                        res, val, lostSkills = self.searchToCompleteTeam(
                            solPhase1, current, problem, budget)

                        if res is False or val > budget:
                            return False, val, lostSkills
                        elif worstCost < val:
                            worstCost = val

                        if k > 1:
                            stack[k-2].append(current.pop())
                        else:
                            current.pop()

                while(len(remains) == 0 and len(current) != 0):
                    a = current.pop()
                    if len(current) != 0:
                        stack[len(current) - 1].append(a)
                    remains = stack[len(current)]
                    stack[len(current)] = []

        return True, worstCost, None

    def run(self, problem, options, verbose=True):
        """
        Run the solver.
        """
        assert len(options) >= 2
        k = int(options[0])
        cut = bool(options[1])

        print("c k:", k)
        print("c cut:", cut)
        agentsProp1, model1 = self.createTheInitialFirstPlayerModel(problem)

        isCompleted = False
        optFound = 1 + self.computeWorstCase(problem.mapOfAgents)
        solFound = []
        cpt = 0

        while not isCompleted:
            solution1 = model1.solve()
            cpt += 1

            if solution1 is not None:
                notInSolution = [
                    a for a in agentsProp1 if solution1[a] < 0.1]
                isCompleted = len(notInSolution) == 0

                # block the current solution for the player 1
                if model1.objective_value < optFound:
                    inSolution = [problem.mapOfAgents[a].id for a in problem.mapOfAgents if (
                        solution1[agentsProp1[problem.mapOfAgents[a].id]] > 0.9)]
                    assert len(notInSolution) + \
                        len(inSolution) == problem.nbAgents

                    print(cpt, optFound, inSolution,
                          int(model1.objective_value))
                    resP2, solP2, skills = self.canSecondPlayerRestoreInAllCases(
                        inSolution, problem, k, optFound - model1.objective_value)

                    if resP2 and solP2 + model1.objective_value < optFound:
                        optFound = model1.objective_value + solP2
                        solFound = [a for a in problem.mapOfAgents
                                    if problem.mapOfAgents[a].id in inSolution]
                        print("i", optFound, solFound)

                    # block the current solution1 for the next run
                    if len(notInSolution) > 0:
                        model1.add_constraint(model1.sum(notInSolution) >= 1)

                    # manage the case where we have to cut a set of solution
                    if cut and not resP2:

                        # collect the agent that can support the skills
                        assert skills is not None
                        sagents = []
                        for s in skills:
                            for a in problem.mapOfSkills[s].l:
                                if a not in sagents:
                                    sagents.append(a)

                        # add the constraint to avoid such situation again
                        model1.add_constraint(model1.sum(
                            agentsProp1[problem.mapOfAgents[a].id]
                            for a in sagents if problem.mapOfAgents[a].id not in inSolution) >= 1)
                else:
                    isCompleted = True
            else:
                isCompleted = True

        # print out the solution
        if verbose:
            print("c Number of iterations:", cpt)
            print("s", end=" ")
            if len(solFound) == 0:
                print("UNSAT")
            else:
                for a in solFound:
                    print(a, end=" ")
                print("")
                print("o", int(optFound))
        return (solFound, int(optFound))
