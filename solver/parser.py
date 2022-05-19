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
from agent import Agent
from skill import Skill


def parse(fileName):
    """
    Parse the file needed to construct a problem.
    """
    mapOfAgents = {}
    mapOfSkills = {}
    listOfExclusion = []

    # collect the data
    with open(fileName, "r") as fichier:
        contain = fichier.read()
        lines = contain.split('\n')

        firstLine = 0
        while firstLine < len(lines) and lines[firstLine][0] != 'P' and lines[firstLine][0] != 'p':
            assert lines[firstLine][0] == 'c'  # normally it is a comment line
            firstLine += 1

        idAgent = 0
        idSkill = 0

        for line in lines:
            if len(line) == 0:
                continue
            typeLine = line[0]

            if typeLine == 'P' or typeLine == 'p':
                elts = [int(i) for i in line[1:].split()]
                nbAgents = elts[0]
                nbSkills = elts[1]
            elif typeLine == 'c':
                continue
            elif typeLine == 'a':
                cline = line[1:].split()
                mapOfAgents[cline[0]] = Agent(
                    cline[0], idAgent, int(cline[1]), int(cline[2]), cline[3:])
                idAgent += 1

                # get the skills: we create a empty skill
                for s in cline[3:]:
                    if s not in mapOfSkills:
                        mapOfSkills[s] = Skill(s, idSkill, -1, [cline[0]])
                        idSkill += 1
                    else:
                        (mapOfSkills[s].l).append(cline[0])
            elif typeLine == 's':
                cline = line[1:].split()

                if cline[0] not in mapOfSkills:
                    mapOfSkills[cline[0]] = Skill(
                        cline[0], idSkill, int(cline[1]), [])
                    idSkill += 1
                else:
                    mapOfSkills[cline[0]].w = int(cline[1])
            elif typeLine == 'e':
                listOfExclusion.append(line[1:].split())
            else:
                raise IOError("Invalid input line: " + line)

        fichier.close()

    return nbAgents, nbSkills, mapOfAgents, mapOfSkills, listOfExclusion
