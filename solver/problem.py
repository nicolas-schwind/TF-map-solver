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
import parser


class Problem:
    """
    Class to store data about a given problem.
    """

    def __init__(self, inputFile):
        """
        Construct a problem from an input file.
        """
        self.nbAgents, self.nbSkills, self.mapOfAgents,\
            self.mapOfSkills, self.eclauses = parser.parse(inputFile)

    def display(self):
        """
        Display information about the problem.
        """
        print("c Information on the problem: ")
        print("c Number of agents:", self.nbAgents)
        print("c Number of skills:", self.nbSkills)
        print("c Number of clauses:", len(self.eclauses))
