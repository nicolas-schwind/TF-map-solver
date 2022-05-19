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
import time
import argparse
from problem import Problem
import solverFactory

# options.
parser = argparse.ArgumentParser(
    description='dreamTeam is a tool to build good teams!')
parser.add_argument('--inputFile', metavar='inputFile', type=str, nargs=1, default='/dev/stdin',
                    help='the input file following the tf format (see README).')
parser.add_argument('--method', metavar='method', type=str, nargs='+', default='tf',
                    help='the method used (tf, robtf k, prtf k t, d-prtf k t, rectf).')
parser.add_argument('--cut', metavar='cut', type=int, nargs='?', default=0, help='the cut level (0 = no cut, 1 = simple cut or 2 = multiple cut')
args = parser.parse_args()
args.method.append(args.cut)

start_time = time.time()

fileName = args.inputFile[0]
print("c Dream Team in construction:")
print("c Method we run:", args.method)
print("c input file:", fileName)

p = Problem(fileName)
p.display()

solver = solverFactory.makeSolver(args.method[0])
solver.run(p, args.method[1:])

interval = time.time() - start_time
print('t', interval)
