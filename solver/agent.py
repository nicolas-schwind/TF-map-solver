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


class Agent:
    """
    Class used to store information about an agent.
    """
    # parameterized constructor

    def __init__(self, name, idAgent, w1, w2, l):
        """
        Constructor.
        """
        self.name = name
        self.id = idAgent
        self.w1 = w1
        self.w2 = w2
        self.l = l

    def display(self, outputFile=None):
        """
        Print out an agent.
        """
        if outputFile is None:
            print("c agent " + str(self.name) + ", id =  " + str(self.id) +
                  ", weight phase 1 = " + str(self.w1) +
                  ", weight phase 2 = " + str(self.w2) + ", skills = " + str(self.l))
        else:
            print("c agent " + str(self.name) + ", id =  " + str(self.id) +
                  ", weight phase 1 = " + str(self.w1) +
                  ", weight phase 2 = " + str(self.w2) + ", skills = " +
                  str(self.l), file=outputFile)
