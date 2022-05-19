# these constants consist of predefined colors for landscapes (LAND and BEACH are currently not used)
SEA = [65, 105, 225]
LAND = [34, 139, 34]
BEACH = [238, 214, 175]
DENSELY_POPULATED = [178, 154, 115]
MODERATELY_POPULATED = [198, 174, 135]
LOOSELY_POPULATED = [218, 194, 155]
DESERT = [238, 214, 175]
MOUNTAIN = [235, 235, 235]

# these constants are used as weights for computing some initial probability distributions (for the new resident seeds)
PROB_DENSELY = 4
PROB_MODERATELY = 2
PROB_LOOSELY = 1
PROB_NO_POPULATION = 0

# these constants are used as weights for computing the probability distributions to add new residents in the
# neighborhood of already existing residents, i.e., in the "iterated phase" (e.g., a resident cannot initially
# be deployed in a desert area, whereas it can be in the iteration phase)
PROB_DENSELY_ITERATE = 8
PROB_MODERATELY_ITERATE = 4
PROB_LOOSELY_ITERATE = 2
PROB_DESERT_ITERATE = 1


# This function projects the source_grid into another grid where each color
# is mapped to another color
def to_refined_type(source_grid):
    result = []
    grid_length = len(source_grid)
    for x in range(grid_length):
        line = []
        for y in range(grid_length):
            if source_grid[x][y] < 90:
                line.append(SEA)
            elif source_grid[x][y] < 100:
                line.append(DENSELY_POPULATED)
            elif source_grid[x][y] < 120:
                line.append(MODERATELY_POPULATED)
            elif source_grid[x][y] < 140:
                line.append(LOOSELY_POPULATED)
            elif source_grid[x][y] < 180:
                line.append(DESERT)
            elif source_grid[x][y] < 200:
                line.append(LOOSELY_POPULATED)
            else:
                line.append(MOUNTAIN)
        result.append(line)
    return result


# This function converts a colored grid into an elevation_for_population_seed grid
# used to initialise the population seeds
# Each box of an elevation_for_population grid is valued at
# 0 if cannot be populated (water / mountain / desert)
# 1 if loosely populated
# 2 if moderately populated
# 4 if densely populated
def to_elevation_for_population_seed(source_grid):
    result = []
    grid_length = len(source_grid)
    for x in range(grid_length):
        line = []
        for y in range(grid_length):
            if source_grid[x][y] == DENSELY_POPULATED:
                line.append(PROB_DENSELY)
            elif source_grid[x][y] == MODERATELY_POPULATED:
                line.append(PROB_MODERATELY)
            elif source_grid[x][y] == LOOSELY_POPULATED:
                line.append(PROB_LOOSELY)
            else:
                line.append(PROB_NO_POPULATION)
        result.append(line)
    return result


# This function converts a colored grid into an elevation_for_population_iterate grid
# used to iterate and make the population grow
# Each box of an elevation_for_population grid is valued at
# 0 if cannot be populated (river / mountain)
# 1 if desert
# 2 if loosely populated
# 4 if moderately populated
# 8 if densely populated
def to_elevation_for_population_iterate(source_grid):
    result = []
    grid_length = len(source_grid)
    for x in range(grid_length):
        line = []
        for y in range(grid_length):
            if source_grid[x][y] == DENSELY_POPULATED:
                line.append(PROB_DENSELY_ITERATE)
            elif source_grid[x][y] == MODERATELY_POPULATED:
                line.append(PROB_MODERATELY_ITERATE)
            elif source_grid[x][y] == LOOSELY_POPULATED:
                line.append(PROB_LOOSELY_ITERATE)
            elif source_grid[x][y] == DESERT:
                line.append(PROB_DESERT_ITERATE)
            else:
                line.append(PROB_NO_POPULATION)
        result.append(line)
    return result


# This function returns a grayscale color according to the amount of residents ('population')
# normalized by the maximum number of residents that can be in a box ('max_pop_per_box')
# This color ranges from 0 to 180 by steps depending on max_pop_per_box
# 0 is max_pop_per_box people, value close to 180 is 1 resident
def population_density_number_to_color(population_count, max_pop_per_box):

    scaled_population_count = (population_count * 180) // max_pop_per_box

    return 180 - scaled_population_count


# This function integrates population (given by 'population_grid') to a non-populated colored
# grid (given by source_grid), and returns a colored (populated) grid
def merge_elevation_with_population(source_grid, population_grid, max_pop_per_box):
    result = []
    grid_length = len(source_grid)
    for x in range(grid_length):
        line = []
        for y in range(grid_length):
            if population_grid[x][y] == 0:
                line.append(source_grid[x][y])
            else:
                color_number = population_density_number_to_color(population_grid[x][y], max_pop_per_box)
                color = []
                color.append(color_number)
                color.append(color_number)
                color.append(color_number)
                line.append(color)
        result.append(line)
    return result


# This function maps a colored_grid to a True-False grid stating whether a facility can be deployed or not.
# A facility cannot be deployed iff the box is a SEA or MOUNTAIN type
def antenna_deployment_candidates(colored_grid_no_population):
    result = []
    grid_length = len(colored_grid_no_population)
    for x in range(grid_length):
        line = []
        for y in range(grid_length):
            if colored_grid_no_population[x][y] in (MOUNTAIN, SEA):
                line.append(False)
            else:
                line.append(True)
        result.append(line)
    return result
