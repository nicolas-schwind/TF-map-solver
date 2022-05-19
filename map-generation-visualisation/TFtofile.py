##'''
##converts the input lists into a TF instance in a file (new version)
##'''
##def TFtofile(file_name, list_agents, list_skills, agents_to_skills, dim):
##    nb_agents = len(list_agents)
##    nb_skills = len(list_skills)
##    file_name = "TF-" + file_name + ".txt"
##    f = open(file_name, 'wt')
##    f.write('P ')
##    f.write('%s %s %s\n' % (int(nb_agents), int(nb_skills), int(dim)))
##    # print skills
##    for id_skill in range(nb_skills):
##        f.write('%s (%s %s) %s\n' % (int(id_skill), int(list_skills[id_skill][0][0]), int(list_skills[id_skill][0][1]), int(list_skills[id_skill][1])))
##    # print agents to costs and skills
##    for id_agent in range(nb_agents):
##        f.write('%s ' % int(id_agent))
##        f.write('(%s %s)' % (int(list_agents[id_agent][0][0]), int(list_agents[id_agent][0][1])))
##        # cost1 (deployment cost)
##        f.write(' %s' % int(list_agents[id_agent][2]))
##        # cost2 (repair cost)
##        f.write(' %s' % int(list_agents[id_agent][3]))
##        for id_skill in agents_to_skills[id_agent]:
##            f.write(' %s' % int(id_skill))
##        f.write('\n')
##    f.close()

'''
returns the number of different points on the map where an antenna can be deployed
'''
def get_nb_id_points(list_agents):
    length_list = len(list_agents)
    return list_agents[length_list - 1][1] + 1

'''
returns the list of agents placed at the same point on the map, where the id of the point is id_point
'''
def get_list_agents_at_id_point(list_agents, id_point):
    nb_agents = len(list_agents)
    result = []
    for id_agent in range(nb_agents):
        if list_agents[id_agent][1] == id_point:
            result.append(list_agents[id_agent])
    return result

'''
converts the input lists into a TF instance in a file .tf (last version)
in addition, it creates another file .info which gives the correspondence
between each agent id and its coordinates on the map: each line is
a <id_agent> <cost1> <cost2> <range> <num_line> <num_col>
Recall that list_agents is an array where each agent is a 6-vector: (point, id_point, cost1, cost2, range, id_agent)
'''
def TFtofile(file_name, list_agents, list_skills, agents_to_skills, dim):
    nb_agents = len(list_agents)
    nb_skills = len(list_skills)
    f = open(file_name + '.tf', 'wt')
    f.write('c This file contains the team formation instance in the following format:\n')
    f.write('c p <number_of_agents>\n')
    f.write('c a <id_agent> <cost_deployment> <cost_repair> <list_of_skills>\n')
    f.write('p ')
    f.write('%s %s\n' % (int(nb_agents), int(nb_skills)))
    f_info = open(file_name + '.info', 'wt')
    f_info.write('c This file contains info about each agent / facility\n')
    f_info.write('c The syntax of each line is as follows:\n')
    f_info.write('c p <number_of_agents>\n')
    f_info.write('c a <id_agent> <cost_deployment> <cost_repair> <range> <y_coordinate> <x_coordinate>\n')
    f_info.write(f'p {int(nb_agents)}\n')
    # agents
    for id_agent in range(nb_agents):
        f.write('a %s %s %s' % (int(id_agent), int(list_agents[id_agent][2]), int(list_agents[id_agent][3])))
        for id_skill in agents_to_skills[id_agent]:
            f.write(' %s' % int(id_skill))
        f.write('\n')
        f_info.write(f'a {int(id_agent)} {int(list_agents[id_agent][2])} {int(list_agents[id_agent][3])} {int(list_agents[id_agent][4])} {list_agents[id_agent][0][0]} {list_agents[id_agent][0][1]}\n')
    # skills
    f_info.close()
    for id_skill in range(nb_skills):
        f.write('s %s %s\n' % (int(id_skill), int(list_skills[id_skill][1])))
    # exclusion constraints
    nb_id_points = get_nb_id_points(list_agents)
##    print('nb_id_points: ', nb_id_points)
    if nb_id_points != nb_agents:
        for id_point in range(nb_id_points):
            list_agents_at_id_point = get_list_agents_at_id_point(list_agents, id_point)
            nb_agents_at_id_point = len(list_agents_at_id_point)
            if nb_agents_at_id_point > 1:
                f.write('e')
                for id_agent in range(nb_agents_at_id_point):
                    f.write(' %s' % int(list_agents_at_id_point[id_agent][5]))
                f.write('\n')
    f.close()

'''
converts the input lists into a TF instance in a file (simple version)
'''
def TFtofilesimple(file_name, list_agents, list_skills, agents_to_skills, dim):
    nb_agents = len(list_agents)
    nb_skills = len(list_skills)
    file_name = file_name + ".tf.txt"
    f = open(file_name, 'wt')
    f.write('P ')
    f.write('%s %s\n' % (int(nb_agents), int(nb_skills)))
    for id_agent in range(nb_agents):
        f.write('%s' % int(list_agents[id_agent][2]))
        for id_skill in agents_to_skills[id_agent]:
            f.write(' %s' % int(id_skill))
        f.write('\n')
    f.close()

'''
file to save the points according to agent ids
The format is:
First line: <nb_agents> <dim_grid>
For each subsequent line: x_coord y_coord range
'''
def TFtomapagentidstopointsrange(file_name, list_agents, dim):
    nb_agents = len(list_agents)
    file_name = file_name + ".idtoinfo.txt"
    f = open(file_name, 'wt')
    f.write('%s %s\n' % (len(list_agents), dim))
    for id_agent in range(nb_agents):
        f.write('%s %s %s\n' % (int(list_agents[id_agent][0][0]), int(list_agents[id_agent][0][1]), int(list_agents[id_agent][4])))
    f.close()
