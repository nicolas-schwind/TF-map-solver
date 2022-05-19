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
from solver import Solver


class Trivial(Solver):
    """
    A tf solver.
    """

    def run(self, problem, options, verbose=True):
        """
        Return all the agent as a solution.

        Attributes:
        ----------
        problem : Problem
            the problem we want to solve
        options : list
            the list of parameter (normally should be empty).
        """
        if verbose:
            print("c Run Trivial: ", options)

        solFound = [a for a in problem.mapOfAgents]
        print('s', end=" ")
        for a in solFound:
            print(a, end=' ')
        print()

        cost = 0
        for a in problem.mapOfAgents:
            cost += problem.mapOfAgents[a].w1

        print("o", cost)
        return (solFound, cost)
