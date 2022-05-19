# this file contains the procedures to generate an initial grid with Perlin noise

import random
from noise import snoise2

SPEED = 5
NB_OCTAVES = 2
DOMAIN_RES = 256


# This function creates a random grid of numbers based on Perlin noise
# The grid has size (nb_pixels * nb_pixels), where nb_pixels is characterized by speed as follows:
# speed = 1 -> nb_pixels = 128, speed = 2 -> 256, nb_pixels = , ..., speed = 5 -> nb_pixels = 2048
# must set speed = 5 for best results
# In the matrix there are (nb_patterns * nb_patterns) atomic "boxes" of noise
# --> Note: an atomic box of Perlin noise is meaningless if zoomed in
# The output of the matrix will be values ranging from 0 to domain_res
def random_noise_grid(nb_patterns, speed=SPEED, nb_octaves=NB_OCTAVES, domain_res=DOMAIN_RES):
    nb_pixels = 2 ** (speed + 6)
    seed = random.random()
    freq = nb_pixels / nb_patterns
    
    result = []
    for x in range(nb_pixels):
        line = []
        for y in range(nb_pixels):
            line.append(int(snoise2(x / freq, y / freq, nb_octaves, base=seed) * ((domain_res / 2) -1) + (domain_res / 2)))
        result.append(line)
    
    return result


# This function associates with an input of numbers a target "compressed" grid numbers
# Each value of the target grid is the average of the associated values in the source grid
# target_nb_pixels should be lower than the resolution of the source grid
# If not, then target_nb_pixels is set to source_nb_pixels and the target grid will be identical to the source grid
def compress_grid(source_grid, target_nb_pixels):
    source_nb_pixels = len(source_grid)
    if target_nb_pixels > source_nb_pixels:
        print("WARNING: nb pixels is automatically set to ", target_nb_pixels)
        return source_grid

    nb_pixels_per_box = source_nb_pixels // target_nb_pixels
    result = []
    for box_x in range(target_nb_pixels):
        line = []
        for box_y in range(target_nb_pixels):
            avg = 0
            for x in range(nb_pixels_per_box):
                for y in range(nb_pixels_per_box):
                    avg += source_grid[(box_x * nb_pixels_per_box) + x][(box_y * nb_pixels_per_box) + y]
            avg = avg / (nb_pixels_per_box ** 2)
            line.append(int(avg))
        result.append(line)

    return result
