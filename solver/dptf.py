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
from math import ceil

from docplex.mp.model import Model
from solver import Solver
import solverFactory
import time


class DPTf(Solver):
    """
    Decision Ptf solver.
    """

    def run(self, problem, options, verbose=True):
        """
        Run the solver.

        Attributes:
        ----------
        problem : Problem
            the problem we want to solve
        options : list
            the list of parameter (k = options[0], t = options[1], cut = options[2]).
        """
        print("c Run decision ptf:", options)
        k = int(options[0])
        t = int(options[1])
        optCut = int(options[2])
        start_time = time.time()

        tfSolver = solverFactory.makeSolver("tf")
        bestTeam, lowerBound = tfSolver.run(problem, [], False)
        assert len(bestTeam) > 0
        print("c Compute the best possible team:", lowerBound)

        ktfSolver = solverFactory.makeSolver("ktf")
        solKf = ktfSolver.run(problem, [options[0]], False)

        if solKf != None:
            solFound, optFound = solKf
        else:
            # optfound is all the agent
            solFound = []
            optFound = 0
            for a in problem.mapOfAgents:
                optFound += problem.mapOfAgents[a].w1
            optFound += 1

        print("c Compute the worst possible team:", optFound)

        sumWeightAll = 0
        for s in problem.mapOfSkills:
            sumWeightAll += problem.mapOfSkills[s].w

        tw = ceil(t * sumWeightAll / 100)
        print("c The sum of the weight is:", sumWeightAll)
        print("c The quantity of weighted skills satisfied must be at least:", tw)

        agentsProp1, model1, upperBound = self.createTheInitialFirstPlayerModel(
            problem, optFound)

        print("b Current bounds:", lowerBound, optFound)
        interval = time.time() - start_time

        if len(solFound):
            print("p", end=" ")
            for a in solFound:
                print(a, end=" ")
            print("")
            print('o', optFound)
            print('t', interval)

        cpt = 0
        target = lowerBound

        while optFound > lowerBound:
            # compute the next bound
            target = optFound - 1
            upperBound.set_ub(target)

            solution1 = model1.solve()
            cpt += 1

            if solution1 is not None:
                # get the agent of the computed solution
                inSolution = [a for a in problem.mapOfAgents if (
                    solution1[agentsProp1[problem.mapOfAgents[a].id]] > 0.9)]

                valFound = 0
                for a in inSolution:
                    valFound += problem.mapOfAgents[a].w1

                if False and verbose:
                    print(cpt, inSolution, valFound)

                # we check out that the returned solution can be returned                
                resP2, cutList, notInSolution = self.testPhase2(
                    inSolution, problem, k, tw, optCut)

                if resP2:
                    optFound = valFound
                    print("b Current bounds:", lowerBound, target)
                    interval = time.time() - start_time
                    print("p", end=" ")
                    for a in inSolution:
                        print(a, end=" ")
                    print("")
                    print('o', optFound)
                    print('t', interval)
                    solFound = inSolution
                    target = lowerBound
                else:
                    # notInSolutionProp = [
                    #    agentsProp1[problem.mapOfAgents[a].id] for a in notInSolution]

                    notInSolutionProp = [
                        a for a in agentsProp1 if solution1[a] < 0.1]
                    model1.add_constraint(model1.sum(notInSolutionProp) >= 1)

                
                    for cut in cutList:                
                        assert len(cut) > 0
                        model1.add_constraint(model1.sum(
                            [agentsProp1[a] for a in cut]) >= k + 1)


                    # update the target.
                    target += 1
                    if target >= optFound:
                        target = lowerBound
            else:
                lowerBound = target + 1
                target = lowerBound

                print("b Current bounds:", lowerBound, optFound, target)
                interval = time.time() - start_time
                print('t', interval)

        # print out the solution
        print("c Number of iterations:", cpt)
        print("s", end=" ")
        if len(solFound) == 0:
            print("UNSAT")
        else:
            for a in solFound:
                print(a, end=" ")
            print("")
            print("o", int(optFound))

    def createTheInitialFirstPlayerModel(self, problem, bestFound):
        """
        Solve the problem of computing a rtf coalition using an iterative approach.
        Attributes:
        ----------

        problem : Problem
            the problem we want to model.

        Returns:
        -------

        the set of variables and the model
        """
        model = Model()
        agentsProp = [model.binary_var(str(i))
                      for i in range(problem.nbAgents)]
        upperBound = model.integer_var(0, bestFound, "bound")

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

        # the best solution found so far.
        model.add_constraint(model.sum(agentsProp[problem.mapOfAgents[a].id]
                                       * problem.mapOfAgents[a].w1 for a in problem.mapOfAgents)
                             <= upperBound)

        return agentsProp, model, upperBound

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

    def testPhase2(self, solPhase1, problem, k, tw, cut):
        """
        Check out if the solution found in phase 1 can be extended in phase 2.

        solPhase1 : list[str]
            the list of agents we are looking if they satisfy the ptf property.
        problem : Problem
            the problem we are modelizing.
        k : int
            in the worst case we can lose k agents.
        tw : int
            in the worst case we have this value of skills (here we consider the weight).

        Returns:
        -------
        True if the given solution is correct, false otherwise. Moreover, in the case
        a solution is found a set of cut is returned.
        """
        # init the model and create the variables.
        model = Model()
        agentsProp = [model.binary_var(str(i))
                      for i in range(problem.nbAgents)]
        skillsProp = [model.binary_var(str(i + 1 + problem.nbAgents))
                      for i in range(problem.nbSkills)]

        # exactly k agent must be lost.
        if k < len(solPhase1):
            model.add_constraint(model.sum(
                [agentsProp[problem.mapOfAgents[a].id]
                 for a in solPhase1]) == len(solPhase1) - k)
        else:
            model.add_constraint(
                model.sum([agentsProp[problem.mapOfAgents[a].id]
                           for a in solPhase1]) == 0)

        # we search for a solution where we lose strictly more than tw quantity of skills
        model.add_constraint(model.sum(
            skillsProp[problem.mapOfSkills[s].id] * problem.mapOfSkills[s].w
            for s in problem.mapOfSkills) <= tw - 1)

        # we check out the skills that are now still satisfied
        for a in solPhase1:
            # search for the agents that have the id 'a'
            agent = problem.mapOfAgents[a]
            model.add_constraint(model.sum([-len(agent.l) * agentsProp[agent.id]] + [
                skillsProp[problem.mapOfSkills[s].id]
                for s in agent.l]) >= 0)

        # if a skill is activated then at least one agent must support it
        for s in problem.mapOfSkills:
            model.add_constraint(model.sum([-skillsProp[problem.mapOfSkills[s].id]] + [
                agentsProp[problem.mapOfAgents[a].id]
                for a in problem.mapOfSkills[s].l if a in solPhase1]) >= 0)

        # try to minimize the number of skills falsified
        cost = model.sum([skillsProp[problem.mapOfSkills[s].id]
                          for s in problem.mapOfSkills])
        model.maximize(cost)

        solution = model.solve()
        if solution is not None:
            # collect the skills that are no more supported
            skillList = [problem.mapOfSkills[s]
                         for s in problem.mapOfSkills
                         if solution[skillsProp[problem.mapOfSkills[s].id]] < 0.1]
            skillList.sort(key=lambda x: x.w, reverse=True)

            notInSolution = []
            
            # compute a cut
            sumSkillsWeight = 0
            for s in problem.mapOfSkills:
                sumSkillsWeight += problem.mapOfSkills[s].w

            cutList = []            
            if cut > 0:
                cutList = self.extractOneCut(
                    problem.mapOfAgents, skillList, sumSkillsWeight - tw, cut)
                assert len(cutList) > 0
            return False, cutList, notInSolution
        else:
            return True, None, None

    def extractOneCut(self, mapOfAgents, skillList, limit, cutLevel):
        """
        Extract a set of agents that have to be present in an enough number in the final solution.

        Attributes:
        ----------

        mapOfAgents : map
            for each id of agent we associate a structure that store data about it
        skillList : list of skill objects
            the set of agent we are looking for
        limit : int
            the threshold we cannot pass

        Returns:
        -------

        A list that contains potentially a set of cuts.
        """
        assert cutLevel != 0             
        csum = 0
        agentId = []     
        ret = []   

        start = 0
        i = 0        
        
        while i < len(skillList):            
            if csum > limit:                                
                ret.append(agentId)
                csum = 0
                agentId = []

                start += 1
                i = start
                if cutLevel == 1:
                    break
            
            s = skillList[i]  
            i += 1        
                        
            csum += s.w
            for a in s.l:
                if mapOfAgents[a].id not in agentId:
                    agentId.append(mapOfAgents[a].id)        
        
        if len(agentId) > 0 and csum > limit:
            ret.append(agentId)
        
        #print("nb cut = ", len(ret))
        return ret
