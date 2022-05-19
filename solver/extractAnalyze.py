#!/usr/bin/python3

import re
import os
import sys
from unicodedata import name

assert(len(sys.argv) == 2)

nameBench = os.path.splitext(os.path.basename(sys.argv[1]))[0]
pathBench = os.path.splitext(sys.argv[1])[0]
family = None
method = None
cost = None
k = None
t = 0
percentLost = None
costRepair = None

listToken = nameBench.split('.')
pos = 1
method = listToken[0]
if method[0] == '1':
    method += listToken[1]
    pos += 1

k = int(listToken[pos])
if method != 'tf' and method != 'ktf':
    pos += 1
    t = int(listToken[pos + 1])

if method == 'tf':
    t = 0
if method == 'ktf':
    t = 100

nameBench = listToken[-2]

status = None
with open(pathBench + ".err") as f:
    lines = f.readlines()

    for line in lines:
        if re.search("status:", line):
            if re.search("out of time", line):
                status = "TO"
            else:
                status = "solved"

        if re.search(" real:", line):
            time = float(line.split(':')[1].split()[
                         0].replace(" ", "").replace("\n", ""))

assert status == "solved"


with open(pathBench + ".log") as f:
    lines = f.readlines()

    for i in range(len(lines)):
        line = lines[i]
        if re.search("^cost ", line):
            cost = line.split()[1]
        elif re.search("^repair_cost ", line):
            costRepair = line.split()[1]
        elif re.search("^percentage_covered_worst ", line):
            percentLost = line.split()[1]
        elif re.search("^c input file:", line):
            family = line.split()[-1].split('/')[-2]


assert(method != None)
assert(family != None)
print("{")
print(" instance: " + nameBench + ", ")
print(" family: " + str(family) + ", ")
print(" method: " + method + ",")
print(" k: " + str(k) + ",")
print(" t: " + str(t) + ",")
print(" cost: " + str(cost) + ",")
print(" cost_repair: " + str(costRepair) + ",")
print(" percent_lost: " + str(percentLost))
print("}")
