# ! /usr/local/bin/python3.7
# this file contains the executable procedure to generate a populated map together with its corresponding TF instance

from gridgen import random_noise_grid, compress_grid
from coloredmaptype import to_elevation_for_population_seed, to_elevation_for_population_iterate, \
    to_refined_type, merge_elevation_with_population, antenna_deployment_candidates
from gridtofile import grid_to_elevation_map_pic_file
from population import seed_population, add_one_guy, point_for_adding_new_guy, point_on_map_mask, \
    init_points_with_at_least_a_valid_neighbor, update_points_with_at_least_a_valid_neighbor
from maptoTF import get_list_agents, get_list_skills, get_agents_to_skills, \
    remove_agents_with_no_skill_from_list_agents, remove_agents_with_no_skill_from_agents_to_skills
from TFtofile import TFtofile
from map_visualisation import generate_png_maps_hexagonal
import progressbar
import argparse

'''
Depending on resolution, this function returns the default list of candidate facility types to be deployed
at each pixel, e.g., if resolution = 2 then (the map will be 8*8 and) the facility types will be [1, 2, 3]
'''
def get_default_list_facility_costs(resolution):
    if resolution <= 1:
        result = [1, 2]
    elif resolution == 2:
        result = [1, 2, 3]
    elif resolution == 3:
        result = [1, 2, 3, 4]
    elif resolution in (4, 5):
        result = [1, 3, 5]
    elif resolution == 6:
        result = [1, 4, 7]
    else:
        result = [1, 4, 7, 10]
    return result


parser = argparse.ArgumentParser()

# this parameter is the only required parameter
# the base file name, e.g., if file_name = 'test', then each instance #i file name will be test-i
parser.add_argument('-f', '--file_name', required=True)

# ALL FOLLOWING PARAMETER ARE OPTIONAL
# the number of instances to be generated, e.g., with the option '-n 10' and '-f test' then 10
# instances will be created, named test-1, ..., test-10
# DEFAULT VALUE: -n 1
parser.add_argument('-n', '--nb_instances', type=int)

#  the resolution of the map, ranging from 1 to 7. For -r <i>, the map will be a grid of size 2^(i + 1),
# e.g., for -r 3 the map will be a 16*16 grid (note: -r 3 is the resolution used in the AAMAS'21 paper)
# DEFAULT_VALUE: -r 3
parser.add_argument('-r', '--resolution', type=int)

# the variation of elevation in the map, ranging from 1 to 4. For instance, -c 4 will generate
# a map with very high variations of elevation, resulting in many small lakes and mountains, whereas
# -c 1 will generate a more uniform map
# DEFAULT VALUE: -c 1
parser.add_argument('-c', '--complexity', type=int)

# the maximum number of people that can be in the same `box`
# this number later corresponds to the 'weight' of the skill associated with the box
# DEFAULT VALUE: 20
parser.add_argument('-l', '--local_max_population', type=int)

# THE DEFAULT VALUE FOR THE REMAINING PARAMETERS BELOW DEPEND ON THE RESOLUTION (i.e., -r <i>)
# the number of starting points for populating the map
# the points are chosen according to a probability distribution,
# the closer to a water part the higher the probability
# DEFAULT VALUE: min((2 * RESOLUTION) - 1, 2^(RESOLUTION - 1))
parser.add_argument('-t', '--nb_cities', type=int)

# the total population, i.e., the map will be populated iteratively by adding people in the
# neighborhood of the initial points (the "starting cities") and according to some probability distribution
# DEFAULT_VALUE: 4^(RESOLUTION + 1)
parser.add_argument('-p', '--total_population', type=int)

# the maximum distance allowed to add a new resident compared to an existing resident,
# i.e., for -d 2 then a new resident can be added at point (i, j) only if there is already
# another resident at distance at most 2 from point (i, j)
# DEFAULT VALUE:
parser.add_argument('-d', '--neighborhood_parsing', type=int)

# the list of facility 'types' (each type identifies its cost and its range: if type = i then the facility's
# initial deployment cost is i and its range is i - 1
# each facility type must be an integer ranging from 1 to 10
# Example: -a [1, 4, 7] will allow the deployment of three types of facilities (type 1, 4 and 7)
# at each point on the map
# DEFAULT VALUE depends on RESOLUTION (see the method get_default_list_facility_costs above to see the correspondence)
parser.add_argument('-a', '--list_facility_costs', type=int, nargs='+')

# parse the arguments
args = parser.parse_args()

# get the instance file name prefix
file_name = args.file_name

# check the range of each option and set default values if an option is not set
if not args.nb_instances:
    nb_instances = 1
elif args.nb_instances > 1000:
    print(f'WARNING: NB_INSTANCES too high (cannot exceed 1000): value set to 1')
    nb_instances = 1
else:
    nb_instances = args.nb_instances

if not args.resolution:
    final_resolution = 3
elif args.resolution > 7:
    print(f'WARNING: RESOLUTION too high (cannot exceed 7): value set to default value 3')
    final_resolution = 3
else:
    final_resolution = args.resolution
target_nb_pixels = 2 ** (final_resolution + 1)

if not args.complexity:
    nb_patterns = 1
elif args.complexity > 4:
    print(f'WARNING: COMPLEXITY too high (cannot exceed 4): value set to default value 1')
    nb_patterns = 1
else:
    nb_patterns = args.complexity

if not args.nb_cities:
    population_seed = min(2 * final_resolution - 1, 2 ** (final_resolution - 1))
elif args.nb_cities > (2 ** (final_resolution + 2)):
    print(f'WARNING: NB_CITIES too high: value set to {min(2 * final_resolution - 1, 2 ** (final_resolution - 1))}')
    population_seed = min(2 * final_resolution - 1, 2 ** (final_resolution - 1))
else:
    population_seed = args.nb_cities

if not args.total_population:
    total_population = 4 ** (final_resolution + 1)
elif args.total_population > (4 ** (final_resolution + 2)):
    print(f'WARNING: TOTAL_POPULATION too high: value set to 4 ** (RESOLUTION + 1) (= {4 ** (final_resolution + 1)})')
    total_population = 4 ** (final_resolution + 1)
else:
    total_population = args.total_population

if not args.local_max_population:
    max_pop_per_box = 20
else:
    max_pop_per_box = args.local_max_population

#print(f'np: {args.neighborhood_parsing}')
if not args.neighborhood_parsing:
    neighborhood_range = final_resolution + (max(0, final_resolution - 4) * 3)
elif args.neighborhood_parsing > 2 ** final_resolution:
    print(
        f'WARNING: NEIGHBORHOOD_PARSING too high: value set to {final_resolution + (max(0, final_resolution, - 4) * 3)})')
    neighborhood_range = final_resolution + (max(0, final_resolution - 4) * 3)
else:
    neighborhood_range = args.neighborhood_parsing
#print(f'nr: {neighborhood_range}')

if not args.list_facility_costs:
    list_facility_costs = get_default_list_facility_costs(final_resolution)
elif min(args.list_facility_costs) < 1 or max(args.list_facility_costs) > 10:
    list_facility_costs = get_default_list_facility_costs(final_resolution)
    print(f'WARNING: values in LIST_FACILITY_COSTS must be in [1, 10]]: list set to {list_facility_costs}')
else:
    list_facility_costs = args.list_facility_costs

# display all options
print('Parameters for map generation:')
print(f'--> FILE_NAME = {file_name}')
print(f'--> NB_INSTANCES = {nb_instances}')
print(f'--> RESOLUTION = {final_resolution}')
print(f'--> COMPLEXITY = {nb_patterns}')
print(f'--> NB_CITIES = {population_seed}')
print(f'--> TOTAL_POPULATION = {total_population}')
print(f'--> LOCAL_MAX_POPULATION = {max_pop_per_box}')
print(f'--> NEIGHBORHOOD_PARSING = {neighborhood_range}')
print(f'--> LIST_FACILITY_COSTS = {list_facility_costs}')

# let's generate each instance
for id_instance in range(nb_instances):
    print('\n****************************************')
    print(f'generation instance #{id_instance + 1}...')

    file_name_without_extension = file_name + '-' + str(id_instance + 1)

    bar = progressbar.ProgressBar(max_value=10,
                                  widgets=[progressbar.FormatCustomText('  -> elevation map generation... '),
                                           progressbar.Percentage()])

    # computing an initial grid called 'source_grid' using Perlin noise
    # the size of the grid is fixed to 2048*2048 and each number ranges from 0 to 256
    # the grid only depends on the parameter 'complexity', i.e., if complexity is high
    # then the variations of numbers between a point on the grid will be high as well
    bar.start()
    source_grid = random_noise_grid(nb_patterns)
    bar.update(2)

    # computing another grid called 'target_grid', which converts the source_grid into a grid
    # with the chosen resolution. Note that source_grid is of size 2048*2048 so the target_grid
    # cannot have a size higher than 2048*2048. So, e.g., if the target_grid is chosen to be 256*256,
    # then each integer in target_grid will be the average of values from source_grid in the same relative position
    target_grid = compress_grid(source_grid, target_nb_pixels)
    bar.update(4)

    # format the target_grid so that each one of its point (an integer) is projected to a color according to some
    # threshold value (e.g., if the value is < 90 then the point will be a water (sea) part, so the color is blue)
    # in total, there are 5 types of lands: sea, desert, loosely / moderately / densely populated parts
    colored_grid = to_refined_type(target_grid)
    bar.update(5)

    # at this point, our target elevation map is generated, we are ready to populate it
    # first, we generate a probability distribution on each point of the grid depending on the type of the point,
    # e.g., densely populated parts are twice more likely to welcome a new resident than moderately populated parts
    elevation_prob_grid_seed = to_elevation_for_population_seed(colored_grid)
    bar.update(6)

    # second, we generate another probability distribution for a grid which will be used to populate the map
    # after the initialisation phase: a new resident will be added in the neighborhood of an already populated box
    # according to that probability distribution (so, e.g., a 'desert' part which cannot be populated in the
    # initialisation phase can be populated in the next phases, but with a low probability
    elevation_prob_grid_iterate = to_elevation_for_population_iterate(colored_grid)
    bar.update(7)

    # initialise the population with 'population_seed' residents
    population_grid = seed_population(elevation_prob_grid_seed, population_seed)
    bar.update(9)
    bar.finish()

    bar = progressbar.ProgressBar(
        widgets=[progressbar.FormatCustomText('  -> preprocessing the map before populating... '),
                 progressbar.Percentage()])
    bar.start()

    # now we generate a 0-1 grid called 'mask_grid' where mask[i][j] = 1 iff there is at least one resident at
    # point (i, j) and there is space its in neighborhood to add another potential resident (e.g., not
    # only water parts or when the maximum population per box is reached in its entire neighborhood)
    mask_grid = init_points_with_at_least_a_valid_neighbor(population_grid, elevation_prob_grid_iterate,
                                                           max_pop_per_box, neighborhood_range, bar)
    bar.finish()
    bar = progressbar.ProgressBar(max_value=total_population,
                                  widgets=[progressbar.FormatCustomText('  -> populating the map... '),
                                           progressbar.Percentage()])
    bar.start()

    # the initialisation phase is over, populate the map iteratively as follows:
    # 1) select first a populated point 'random_point1' which has at least one valid box in its neighborhood which
    # can be populated (this condition is given by mask_grid). Densely populated boxes are more likely to be chosen
    # 2) select a point in the neighborhood of random_point1, also according to a probability distribution given by
    # the grid elevation_prob_grid_iterate
    for i in range(total_population):
        bar.update(i)

        # 1) select first a populated point 'random_point1' which has at least one valid box in its neighborhood
        # which can be populated (this condition is given by mask_grid). Densely populated and more likely to be
        # chosen, this is given by population_grid
        random_point1 = point_on_map_mask(population_grid, mask_grid)

        # 2) select a point in the neighborhood of random_point1, also according to a probability distribution given by
        # the grid elevation_prob_grid_iterate (the grid population_grid is only used to double-check that
        # the box to add a new resident is not full yet)
        random_point2 = point_for_adding_new_guy(population_grid, elevation_prob_grid_iterate, random_point1,
                                                 max_pop_per_box, neighborhood_range)

        # 3) add a resident to the point random_point2 computed above
        if random_point2 != -1:
            add_one_guy(population_grid, random_point2)

        # check if the box where the new resident has been added has now become full (>= max_pop_per_box)
        # if this the case, update the mask_grid to exclude the box from being a potential candidate to add
        # a new resident at the next iteration
        if population_grid[random_point2[0]][random_point2[1]] >= max_pop_per_box:
            update_points_with_at_least_a_valid_neighbor(mask_grid, random_point2, population_grid,
                                                         elevation_prob_grid_iterate, max_pop_per_box,
                                                         neighborhood_range)

    # at this point, the map has been populated
    bar.finish()

    # generate a .ppm file which is a colored grid corresponding to the elevation map + population.
    # when a box is populated, the color is a grayscale, the darker the more densely populated
    # (a pitch black box corresponds to a fully populated box, i.e., that box contains max_pop_per_box residents)
    grid_to_elevation_map_pic_file(merge_elevation_with_population(colored_grid, population_grid, max_pop_per_box),
                                   str(file_name_without_extension))

    # according to the .ppm file generated (a colored grid), generate a .png file which corresponds to the same grid
    # but in a hexagonal form (the TF instance will respect the hexagonal form of the map, i.e., the range
    # of each facility will respect the distance in that hexagonal grid)
    generate_png_maps_hexagonal('.', file_name_without_extension)

    # facilities can be deployed on every land type except on sea and mountain types,
    # so the grid 'agent_grid' below corresponds to a Boolean grid where agent_grid[i][j] = true
    # iff a facility can be deployed on point (i, j)
    agent_grid = antenna_deployment_candidates(colored_grid)

    bar = progressbar.ProgressBar(
        widgets=[
            progressbar.FormatCustomText('  -> converting map into Team Formation instance (agents and skills)... '),
            progressbar.Percentage()])
    bar.start()

    # start the conversion of the map instance into a TF instance
    # first, generate the list of agents, one agent per facility type and per box where a facility can be deployed
    list_agents = get_list_agents(agent_grid, list_facility_costs, final_resolution, bar)
    bar.finish()

    # second, generate the list of weighted skills (a weight skill is a pair (point_coordinate, population)),
    # one weighted skill per populated box
    list_skills = get_list_skills(population_grid)
    bar = progressbar.ProgressBar(
        widgets=[progressbar.FormatCustomText(
            '  -> converting map into Team Formation instance (linking agents to skills)... '),
                 progressbar.Percentage()])
    bar.start()

    # associate each agent (a facility type located at a precise box) with its list of skills, i.e.,
    # with the populated boxes that are in its range
    agents_to_skills = get_agents_to_skills(agent_grid, population_grid, list_agents, list_skills, bar)
    bar.finish()

    # remove from the list of agents the agents that have no skill, and update the agents_to_skills mapping
    list_agents = remove_agents_with_no_skill_from_list_agents(list_agents, agents_to_skills)
    agents_to_skills = remove_agents_with_no_skill_from_agents_to_skills(agents_to_skills)

    # generate the TF instance and create a corresponding .tf file
    TFtofile(file_name_without_extension, list_agents, list_skills, agents_to_skills, len(colored_grid))

    # print some details about the generated map / TF instance
    print(f'instance #{id_instance + 1} generated (instance name: {file_name_without_extension})')
    print(f'--> nb of agents: {len(list_agents)}')
    print(f'--> nb of skills: {len(list_skills)}')
    print('****************************************')
