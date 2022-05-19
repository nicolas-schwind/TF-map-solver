SOLUTION_FOR_TF = 1
SOLUTION_FOR_ROBUST_TF = 2
SOLUTION_FOR_PARTIAL_ROBUST_TF = 3
SOLUTION_FOR_RECOVERABLE_TF = 4


def save_solution_common(f, list_agent_ids, overall_cost, solving_time, per_worst, repair_cost=-1, time_out=None, cplex_size_limit_reached=False):
    f.write('sol')
    if not list_agent_ids:
        if cplex_size_limit_reached:
            f.write(f' NONE (CPLEX size limit reached)\n')
        else:
            f.write(f' NONE (time out: {time_out} seconds)\n')
    else:
        for ag in list_agent_ids:
            f.write(f' {ag}')
        f.write('\n')
        f.write(f'cost {overall_cost}\n')
        f.write(f'percentage_covered_worst {per_worst:.2f}\n')
        if repair_cost >= 0:
            f.write(f'repair_cost {repair_cost}\n')
        f.write(f'time {solving_time:.2f} seconds\n')


def save_solution_tf(instance_name, list_agent_ids, overall_cost, solving_time, per_worst, repair_cost=-1, time_out=None, cplex_size_limit_reached = False):
    f = open(instance_name + '-TF.sol', 'wt')
    f.write('type TF\n')
    save_solution_common(f, list_agent_ids, overall_cost, solving_time, per_worst, repair_cost, time_out, cplex_size_limit_reached)
    f.close()


def save_solution_ptf(instance_name, list_agent_ids, overall_cost, solving_time, k, t, per_worst, repair_cost=-1, time_out=None, cplex_size_limit_reached = False):
    f = open(instance_name + f'-PTF-k{k}-t{t}.sol', 'wt')
    f.write('type PTF\n')
    f.write(f'parameters {k} {t}\n')
    save_solution_common(f, list_agent_ids, overall_cost, solving_time, per_worst, repair_cost, time_out, cplex_size_limit_reached)
    f.close()


def save_results_for_all_instances_ptf(directory_name, k, t, nb_instances, nb_solved_instances, nb_repairable_solutions,
                                       total_cost, total_repair_cost, total_time, total_per_worst, time_out):
    f = open(directory_name + f'TF-all-PTF-k{k}-t{t}.txt', 'wt')
    f.write('type PTF\n')
    f.write(f'parameters {k} {t}\n')
    f.write(f'solved_instances {nb_solved_instances} / {nb_instances} (time out: {time_out} seconds)\n')
    if nb_solved_instances > 0:
        f.write(f'avg_deployment_cost_of_solved_instances {total_cost / nb_solved_instances:.2f}\n')
        f.write(f'avg_percentage_covered_worst_case {total_per_worst / nb_solved_instances:.2f}\n')
        f.write(f'avg_repair_cost_of_solved_instances ')
        if nb_repairable_solutions > 0:
            f.write(f'{total_repair_cost / nb_solved_instances:.2f}\n')
        else:
            f.write(f'(not computed)\n')
        f.write(f'avg_time_of_solved_instances {total_time / nb_solved_instances:.2f}\n')
    f.close()


# returns the list of all agents info from solution if specified, or all agents if solution is not specified
# an agent info is <id_agent> <cost1> <cost2> <range> <coordinate_x> <coordinate_y>
def read_agents_from_info_file(instance_name, solution_list_agent_ids=None):
    list_agents_info = []
    f = open(instance_name + '.info', 'r')
    line = f.readline()
    while line:
        agent_info = []
        split = line.split()
        len_split = len(split)
        if split[0] == 'a' and (not solution_list_agent_ids or int(split[1]) in solution_list_agent_ids):
            for i in range(1, len_split):
                agent_info.append(int(split[i]))
            list_agents_info.append(agent_info)
        line = f.readline()
    f.close()
    return list_agents_info


# reads agents solution:
# returns a tuple (<list_agents_ids>, <cost>, <list_parameters>)
# if solution_type = SOLUTION_FOR_TF: list_parameters = []
# if solution_type = SOLUTION_FOR_ROBUST_TF: list_parameters = [<k>]
# if solution_type = SOLUTION_FOR_PARTIAL_ROBUST_TF: list_parameters = [<k>, <t>]
# if solution_type = SOLUTION_FOR_RECOVERABLE_TF: list_parameters = [<k>]
def read_solution_file(solution_file_name):
    list_agents_ids = []
    cost = -1
    cost_repair = -1
    type_pb = None
    time = None
    parameters = []
    per_worst = None
    cut = None
    optimal = None
    f = open(solution_file_name, 'r')
    line = f.readline()
    while line:
        split = line.split()
        if split[0] == 'type':
            type_pb = split[1]
        elif split[0] == 'sol':
            len_split = len(split)
            if split[1] == 'None':
                return None
            for i in range(1, len_split):
                list_agents_ids.append(int(split[i]))
        elif split[0] == 'cost':
            cost = int(split[1])
        elif split[0] == 'repair_cost':
            cost_repair = int(split[1])
        elif split[0] == 'time':
            time = float(split[1])
        elif split[0] == 'parameters':
            len_split = len(split)
            for i in range(1, len_split):
                parameters.append(int(split[i]))
        elif split[0] == 'percentage_covered_worst':
            per_worst = float(split[1])
        elif split[0] == 'cut':
            cut = split[1]
        elif split[0] == 'optimal':
            if split[1] == 'YES':
                optimal = True
            else:
                optimal = False
        line = f.readline()
    f.close()
    return type_pb, list_agents_ids, cost, cost_repair, time, parameters, per_worst, cut, optimal
