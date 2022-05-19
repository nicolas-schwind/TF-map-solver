import sys
import re
from unicodedata import name

MAX_K = 4
result = {}

families = set()
instances = set()
kValue = set()
ratio = set()
instanceToFamily = {}

repository = sys.argv[2]
assert(len(sys.argv) == 3)


def printInstance(nameFile, entry, k):
    with open(nameFile, "w+") as f:
        f.write("instance=" + entry['full-path-instance'] + "\n")
        team = ""
        for a in entry["solution"].split(','):
            team += a + " "
        team = team.replace("[", "").replace("]", "")
        f.write("team=" + team + "\n")
        f.write("k=" + k + "\n")


with open(sys.argv[1]) as f:
    lines = f.readlines()

    entry = {}
    for line in lines:
        if line[0] == '{':
            entry = {}
        elif line[0] == '}':
            families.add(entry['family'])
            instances.add(entry['instance'])
            instanceToFamily[entry['instance']] = entry['family']

            if entry['method'] not in result:
                result[entry['method']] = {}

            ptrMethod = result[entry['method']]

            if entry['method'] == 'tf':
                if entry['family'] not in ptrMethod:
                    ptrMethod[entry['family']] = {}
                ptrMethod[entry['family']][entry['instance']] = entry
            elif entry['method'] == 'ktf':
                kValue.add(entry['k'])
                if entry['k'] not in ptrMethod:
                    ptrMethod[entry['k']] = {}
                if entry['family'] not in ptrMethod[entry['k']]:
                    ptrMethod[entry['k']][entry['family']] = {}
                ptrMethod[entry['k']][entry['family']
                                      ][entry['instance']] = entry
            elif entry['method'] == 'rtf':
                if entry['k'] not in ptrMethod:
                    ptrMethod[entry['k']] = {}
                if entry['cut'] not in ptrMethod[entry['k']]:
                    ptrMethod[entry['k']][entry['cut']] = {}
                if entry['family'] not in ptrMethod[entry['k']][entry['cut']]:
                    ptrMethod[entry['k']][entry['cut']][entry['family']] = {}
                ptrMethod[entry['k']][entry['cut']
                                      ][entry['family']][entry['instance']] = entry
            else:
                ratio.add(entry['t'])

                if entry['k'] not in ptrMethod:
                    ptrMethod[entry['k']] = {}
                if entry['cut'] not in ptrMethod[entry['k']]:
                    ptrMethod[entry['k']][entry['cut']] = {}
                if entry['t'] not in ptrMethod[entry['k']][entry['cut']]:
                    ptrMethod[entry['k']][entry['cut']][entry['t']] = {}
                if entry['family'] not in ptrMethod[entry['k']][entry['cut']][entry['t']]:
                    ptrMethod[entry['k']][entry['cut']
                                          ][entry['t']][entry['family']] = {}
                ptrMethod[entry['k']][entry['cut']][entry['t']
                                                    ][entry['family']][entry['instance']] = entry
        else:
            key = line.split(':')[0].replace(" ", "")
            value = line.split(':')[1].replace(" ", "")[:-1]
            if value[-1] == ',':
                value = value[:-1]
            entry[key] = value


for method in result:
    if(method == "rtf" or method == "ktf"):
        continue

    if(method == "tf"):
        for k in range(1, MAX_K + 1):
            for family in result[method]:
                for instance in result[method][family]:
                    nameFile = method + "." + str(k) + "." + instance
                    printInstance(
                        repository + nameFile, result[method][family][instance], str(k))
    else:
        for k in result[method]:
            for cut in result[method][k]:
                if cut == "False":
                    continue
                for t in result[method][k][cut]:
                    for family in result[method][k][cut][t]:
                        for instance in result[method][k][cut][t][family]:
                            nameFile = method + "." + \
                                str(k) + "." + cut + "." + t + "." + instance
                            entry = result[method][k][cut][t][family][instance]
                            if(entry['cost'] == "None"):
                                continue

                            if method == "ptf":
                                printInstance(
                                    repository + nameFile, entry, k)
                            else:
                                # previous = [None, 10]
                                # for sol in entry['intermediate-solution'].split("*"):
                                #     time = float(sol.split(",")[1])
                                #     if time < previous[1]:
                                #         previous[0] = sol
                                #     else:
                                #         entryTmp = {
                                #             'full-path-instance': entry['full-path-instance'],
                                #             'k': k, 'solution': "[" + previous[0].split("[")[1][:-1]}
                                #         printInstance(
                                #             repository + str(previous[1]) + "." + nameFile, entryTmp, k)

                                #         previous[1] = previous[1] * 10
                                printInstance(
                                    repository + nameFile, entry, k)
