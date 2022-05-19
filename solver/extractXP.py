#!/usr/bin/python3

import re
import os
import sys
from unicodedata import name

assert(len(sys.argv) == 2)

nameBench = os.path.splitext(os.path.basename(sys.argv[1]))[0]
pathBench = os.path.splitext(sys.argv[1])[0]
family = None
fullPath = None
method = None
solution = None
cost = None
isOptimal = None
status = None
time = None
k = None
t = None
cut = None

cpt = 0
list_solution = []

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


with open(pathBench + ".log") as f:
    lines = f.readlines()

    for i in range(len(lines)):
        line = lines[i]
        if re.search("Method we run:", line):
            l = line.split(':')[1].replace(" ", "").replace("\n", "").replace(
                "[", "").replace("]", "").replace("'", "").split(',')
            method = l[0]

            if method != "tf" and method != "trivial":
                k = int(l[1])

            if method == "dptf" or method == "ptf":
                t = int(l[2])
                cut = l[3] == "True"

            if method == "rtf":
                cut = l[2] == "True"

        elif re.search("^s ", line):
            solution = [int(val)
                        for val in line.split(' ')[1:-1]]
            isOptimal = True
        elif re.search("^o ", line):
            cost = int(line.split(' ')[1])
            if method == "dptf":
                if not isOptimal and lines[i-1][0] == 'p':
                    l = lines[i-1].replace("\n", "").split(' ')[1:]
                    while l[-1] == '':
                        l.pop()
                    solution = [int(val) for val in l]
                    isOptimal = False
                    list_solution.append(
                        (int(cost), float(lines[i+1].split()[1]), solution))
        elif re.search("2=/home/cril/lagniez/", line):
            fullPath = line.split('=')[1].replace("\n", "")
            family = line.split()[-1].split('/')[-2]


assert(method != None)
assert(family != None)
print("{")
print(" instance: " + nameBench + ", ")
print(" full-path-instance: " + fullPath + ", ")
print(" family: " + str(family) + ", ")
print(" method: " + method + ",")
print(" status: " + status + ",")
print(" time: " + str(time) + ",")

if method != "tf":
    print(" k: " + str(k) + ",")

if method == "dptf" or method == "ptf":
    print(" t: " + str(t) + ",")
    print(" cut: " + str(cut) + ",")

    ch = ""
    for c in list_solution:
        ch += "(" + str(c[0]) + ", " + str(c[1]) + ", " + str(c[2]) + ") * "
    ch = ch[:-2]

    print(" intermediate-solution: " + ch + ",")

if method == "rtf":
    print(" cut: " + str(cut) + ",")

print(" solution: " + str(solution) + ",")
print(" cost: " + str(cost) + ",")
print(" optimal: " + str(isOptimal) + "")
print("}")
