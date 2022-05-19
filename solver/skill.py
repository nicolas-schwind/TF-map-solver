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


class Skill:
    """
    Class used to store skills.
    """

    def __init__(self, name, idSkill, w, l):
        """
        Constructor.
        """
        self.name = name
        self.id = idSkill
        self.w = w
        self.l = l

    def display(self, outputFile=None):
        """
        Display the skill.
        """
        if outputFile is None:
            print("c skill " + self.name + ", id = " + str(self.id) +
                  ", weight = " + str(self.w) + ", agents = " + str(self.l))
        else:
            print("c skill " + self.name + ", id = " + str(self.id) + ", weight = " +
                  str(self.w) + ", agents = " + str(self.l), file=outputFile)
