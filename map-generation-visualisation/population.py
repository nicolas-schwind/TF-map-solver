import random

'''
initialise a grid of size grid_length to 0
'''
def initialize_grid(grid_length):
    result = []
    for x in range(grid_length):
        line = []
        for y in range(grid_length):
            line.append(0)
        result.append(line)
    return result

'''
sum all values of the grid of dimension 2
'''
def sum_values(grid):
    result = 0
    grid_length = len(grid)
    for x in range(grid_length):
        for y in range(grid_length):
            result += grid[x][y]
    return result

def number_to_point(source_grid, rand_point_one_dim):
    grid_length = len(source_grid)
    counter = 0
    for x in range(grid_length):
        for y in range(grid_length):
            if source_grid[x][y] > 0:
                counter += source_grid[x][y]
                if counter >= rand_point_one_dim:
                    result = []
                    result.append(x)
                    result.append(y)
                    return result
    print('Error in number_to_point from population.py')
    raise SystemExit

'''
Returns a random point (in 2D) on the map source_grid
where the values of source_grid give a weight to the uniform distribution
'''
def point_on_map(source_grid):
    total_number = sum_values(source_grid)
    if total_number > 0:
        return number_to_point(source_grid, random.randint(0, total_number - 1))
    return -1

'''
Same as point_on_map but with a mask
'''
def point_on_map_mask(source_grid, mask_grid):
    new_source_grid = []
    grid_length = len(source_grid)
    for x in range(grid_length):
        line = []
        for y in range(grid_length):
            line.append(source_grid[x][y] * mask_grid[x][y])
        new_source_grid.append(line)

    # new source grid done!
    total_number = sum_values(new_source_grid)
    if total_number == 0:
        print(new_source_grid)

    result = number_to_point(new_source_grid, random.randint(0, total_number - 1))
    return result

'''
Initialize nb_seeds seeds of population 1 somewhere in the map
according to a probability distribution of elevation map from source_grid
and 0 everywhere else
bar is a progress bar for display
'''
def seed_population(source_grid, nb_seeds):
    result = []
    grid_length = len(source_grid)
    
    for x in range(grid_length):
        line = []
        for y in range(grid_length):
            line.append(0)
        result.append(line)

    for it in range(nb_seeds):
        random_point = point_on_map(source_grid)
        result[random_point[0]][random_point[1]] = 1

    return result

'''
Add one guy on source_grid at the coordinates point_on_map
'''
def add_one_guy(source_grid, point_on_map):
    source_grid[point_on_map[0]][point_on_map[1]] += 1


'''
Return the distance between two points
By default hexagonal=True, so the hexagonal distance between two points is considered (odd-r version of hexagonal grid)
If hexagonal=False, then the Manhattan distance is used
'''
def distance(point1, point2, hexagonal=True):
    if hexagonal:
        return hexagonal_dist(point1, point2)
    else:
        return manhattan_dist(point1, point2)


'''
Return the Manhattan distance between two points
'''
def manhattan_dist(point1, point2):
    return abs(point1[0] - point2[0]) + abs(point1[1] - point2[1])


'''
Return the hexagonal distance between two points
odd-r version of hexagonal grid
OLD / WRONG VERSION
'''
def hexagonal_dist_old(point1, point2):
    dx = point2[0] - point1[0]
    dy = point2[1] - point1[1]
    x = abs(dx)
    y = abs(dy)
    if dx < 0 or point1[1] & 1 == 1:
        x = max(0, x - (y + 1) // 2)
    else:
        x = max(0, x - y // 2)
    return x + y


'''
Return the hexagonal distance between two points
odd-r version of hexagonal grid
'''
def hexagonal_dist(point1, point2):
    dx = point2[0] - point1[0]
    dy = point2[1] - point1[1]
    x = abs(dx)
    y = abs(dy)
    if x % 2 == 1 and ((point1[0] % 2 == 0 and dy < 0) or (point1[0] % 2 == 1 and dy > 0)):
        y = max(0, y - (x // 2) - 1)
    else:
        y = max(0, y - (x // 2))
    return x + y


'''
Returns a list of points within distance dist from ref_point, but excluding ref_point,
given that the size of the grid is is grid_length (no need for the grid itself)
Only points in the range of a map are listed
'''
def points_around(ref_point, dist, grid_length, includes_self):
    if dist == 0:
        result = []
        point = []
        point.append(ref_point[0])
        point.append(ref_point[1])
        result.append(point)
        return result

    result = []
    start_x = max(0, ref_point[0] - dist)
    end_x = min(grid_length, ref_point[0] + dist + 1)
    start_y = max(0, ref_point[1] - dist)
    end_y = min(grid_length, ref_point[1] + dist + 1)

    for x in range(start_x, end_x):
        for y in range(start_y, end_y):
            if x != ref_point[0] or y != ref_point[1] or includes_self:
                candidate_point = []
                candidate_point.append(x)
                candidate_point.append(y)
                if distance(candidate_point, ref_point) <= dist:
                    result.append(candidate_point)
    return result


'''
Returns a map valued at 1 if there is a least one point in the neighborhood where
a guy can be added, 0 otherwise
'''
def init_points_with_at_least_a_valid_neighbor(population_grid, elevation_prob_grid, max_pop_per_box, neighborhood_range, bar):
    result = []
    grid_length = len(population_grid)
    bar.max_value = grid_length
    for x in range(grid_length):
        bar.update(x)
        line = []
        for y in range(grid_length):
            current_point = []
            current_point.append(x)
            current_point.append(y)
            neighbor_points = points_around(current_point, neighborhood_range, grid_length, False)
            # if every point from neighbor_points is eith water / mountain or has already reached
            # mam_pop_per_box people, put 0 on the coordinates of current_point
            for neighbor_point in neighbor_points:
                found = False
                if elevation_prob_grid[neighbor_point[0]][neighbor_point[1]] > 0 and population_grid[neighbor_point[0]][neighbor_point[1]] < max_pop_per_box:
                    line.append(1)
                    found = True
                    break
            if found == False:
                line.append(0)
        result.append(line)
    return result

'''
Similar to the function init_points_with_at_least_a_valid_neighbor above,
but update in mask_grid only the values in the neighborhood of point
'''
def update_points_with_at_least_a_valid_neighbor(mask_grid, point, population_grid, elevation_prob_grid, max_pop_per_box, neighborhood_range):
    grid_length = len(population_grid)
    start_x = max(0, point[0] - neighborhood_range)
    end_x = min(grid_length, point[0] + neighborhood_range + 1)
    start_y = max(0, point[1] - neighborhood_range)
    end_y = min(grid_length, point[1] + neighborhood_range + 1)

    for x in range(start_x, end_x):
        for y in range(start_y, end_y):
            if x != point[0] or y != point[1]:
                # check if the mask at the point (x, y) must be updated, i.e.,
                # if the point (x, y) has at least one valid neighbor
                current_point = []
                current_point.append(x)
                current_point.append(y)
                neighbor_points = points_around(current_point, neighborhood_range, grid_length, False)
                # if every point from neighbor_points is eith water / mountain or has already reached
                # max_pop_per_box people, put 0 on the coordinates of current_point
                for neighbor_point in neighbor_points:
                    found = False
                    if elevation_prob_grid[neighbor_point[0]][neighbor_point[1]] > 0 and population_grid[neighbor_point[0]][neighbor_point[1]] < max_pop_per_box:
                        mask_grid[x][y] = 1
                        found = True
                        break
                if found == False:
                    # print('new forbidden point: ', current_point)
                    mask_grid[x][y] = 0

'''
Select a point around ref_point according to the distribution given by
both population_grid and elevation_prob_grid
'''
def point_for_adding_new_guy(population_grid, elevation_prob_grid, ref_point, max_pop_per_box, neighborhood_range):
    # new_prob_grid is defined as follows
    # prob is 4, 2, 1 around the ref_point resp. according to Manhattan distance,
    # multiplied by 8, 4, 2 or 1 depending on the landscape
    # if the new point is already equal to max_pop, select new_point as new
    # ref_point and iterate. After 100 times, stop and return -1
    # because we are stuck in an island or something

    grid_length = len(population_grid)

    # Initialise new_prob_grid to 0 everywhere
    new_prob_grid = initialize_grid(grid_length)
    #print('initial prob grid')
    #print(new_prob_grid)
    # Compute the list of points in the neighborhood of ref_point
    # Here we should have at least a point in neighbor_points where we can add a guy
    neighbor_points = points_around(ref_point, neighborhood_range, grid_length, False)
    #print('neighborhood')
    #print(neighbor_points)
    # Put a prob value on new_prob_grid on neighbor_points
    #print('\niterations:')
    for current_point in neighbor_points:
        #print('current point:')
        #print(current_point)
        elevation_prob_value = elevation_prob_grid[current_point[0]][current_point[1]]
        #print('elevation value:')
        #print(elevation_prob_value)
        # distance_prob_value = 4 // (2 ** (manhattan_dist(current_point, ref_point) - 1))
        distance_prob_value = neighborhood_range - distance(current_point, ref_point) + 1
        #print('distance value:')
        #print(distance_prob_value)
        not_full_yet = 1
        if population_grid[current_point[0]][current_point[1]] >= max_pop_per_box:
            not_full_yet = 0
        new_prob_value = int(elevation_prob_value * distance_prob_value * not_full_yet)
        new_prob_grid[current_point[0]][current_point[1]] = new_prob_value

    #print(new_prob_grid)
    # here the new_prob_grid is correct!
    # select the next point according to the new probability distribution from new_prob_grid
    if sum_values(new_prob_grid) == 0:
        print('blocked at point ', ref_point)
    candidate_point = point_on_map(new_prob_grid)

    return candidate_point


    # THE FOLLOWING IS NOT NECESSARY: THE MAX POPULATION
    # test if the max population is reached on candidate_point. If yes, select
    # a point in the neighborhood (dist = 1) that is not sea or mountain
    # Do it iteratively until success
##    if population_grid[candidate_point[0]][candidate_point[1]] < max_pop_per_box:
##        return candidate_point
##
##    for i in range(10000):
##        neighbor_points = points_around(candidate_point, 1, grid_length)
##        if len(neighbor_points) == 0:
##            return -1
##        candidate_point = neighbor_points[random.randint(0, len(neighbor_points) - 1)]
##        if population_grid[candidate_point[0]][candidate_point[1]] < max_pop_per_box:
##            return candidate_point
##
##    return -1

'''
for x1 in range(8):
    for y1 in range(8):
        for x2 in range(8):
            for y2 in range(8):
                print(f'distance ({x1}, {y1}) ~ ({x2}, {y2}) = {hexagonal_dist((x1, y1), (x2, y2))}')
'''
