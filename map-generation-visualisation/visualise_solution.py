# ! /usr/local/bin/python3.7

import sys
import os
from map_visualisation import generate_png_maps_hexagonal

# the argument sys.argv[1] must be the only argument and contain a directory name to treat all instances + solution
if len(sys.argv) != 2:
    print("ERROR: there must be exactly one argument, i.e., the directory name where the instances + solutions are located")
    raise SystemExit

directory_name = sys.argv[1]
if not os.path.isdir(directory_name):
    print(f'ERROR: {directory_name} is not a directory')
    raise SystemExit

# each valid instance + solution pair must contain three files .ppm, .sol, and .info
# get all instance names from directory
all_files_in_directory = [solution_file for solution_file in os.listdir(directory_name)]
all_instances = [solution_file[:-4] for solution_file in os.listdir(directory_name) if solution_file.endswith('.ppm')]
nb_potential_instances = len(all_instances)
print(f'all instance names: {all_instances}')
print(f'nb potential instances: {nb_potential_instances}')
for instance in all_instances:
    print(f'--> dealing with instance {instance}')
    if f'{instance}.ppm' in all_files_in_directory and f'{instance}.info' in all_files_in_directory:
        print(f'    --> valid instance (has .ppm and .info files)')
        all_solutions_for_this_instance = [solution for solution in os.listdir(directory_name) if
                                           solution.startswith(instance + '.') and solution.endswith('.sol')]
        if all_solutions_for_this_instance:
            for solution in all_solutions_for_this_instance:
                print(f'    --> treatment of solution {solution}')
                generate_png_maps_hexagonal(directory_name, instance, solution_name=solution, with_text=False)
                print(f'    --> png file generated!')
        else:
            print(f'    --> no solution found for this instance')
