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


class KTf(Solver):
    """
    A tf solver.
    """

    def run(self, problem, options, verbose=True):
        """
        Solve the ktf problem given the input variables.

        Attributes:
        ----------
        problem : Problem
            the problem we want to solve
        option : list
            the list of parameter (option[0] is the number of agents which can be dropped out)
        """
        if verbose:
            print("c Run ktf:", options)
        k = int(options[0])
        model = Model()
        agentsProp = [model.binary_var(str(i))
                      for i in range(problem.nbAgents)]

        # the set of constraints that ensure that each skill is supported by at least one agent
        for s in problem.mapOfSkills:
            model.add_constraint(
                model.sum(agentsProp[problem.mapOfAgents[a].id]
                          for a in problem.mapOfSkills[s].l) >= k + 1)

        # integrity constraints
        for cl in problem.eclauses:
            model.add_constraint(
                model.sum(agentsProp[problem.mapOfAgents[cl[i]].id] for i in range(len(cl))) <= 1)

        # the function we search to minimize
        cost = model.sum(agentsProp[problem.mapOfAgents[a].id]
                         * problem.mapOfAgents[a].w1 for a in problem.mapOfAgents)

        # solve the problem
        model.minimize(cost)
        solution = model.solve()

        # print out the solution
        if solution is not None:
            if verbose:
                print("s", end=" ")
            solFound = []
            for a in agentsProp:
                if solution[a] == 1:
                    solFound.append(str(a))
                    if verbose:
                        print(a, end=" ")
            if verbose:
                print()
                print("o", int(model.objective_value))
            return (solFound, int(model.objective_value))
        else:
            if verbose:
                print("No folution found")
            return None
