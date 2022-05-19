import sys

DOMAIN_RES = 256


# This function just ensures that each number in the input grid is within the range [0, 255]
def check_grid_values(grid, colored):
    mini = sys.maxsize
    maxi = -sys.maxsize
    grid_length = len(grid)
    for x in range(grid_length):
        for y in range(grid_length):
            if not colored:
                val = grid[x][y]
                if mini > val:
                    mini = val
                if maxi < val:
                    maxi = val
            else:
                for z in range(3):
                    val = grid[x][y][z]
                    if mini > val:
                        mini = val
                    if maxi < val:
                        maxi = val
                    
    if mini >= 0 and maxi < DOMAIN_RES:
        return

    # Here the grid values are outside the required range [0-255]
    print("The values of the grid in a pgm / ppm file must be between 0 and 255")
    raise SystemExit


# This functions converts the input grid into a colored picture into the file file_name.ppm
# WARNING: the values of the grid should be in [0-255], otherwise an error will be raised
def grid_to_elevation_map_pic_file(grid, file_name):
    check_grid_values(grid,True)
    grid_length = len(grid)
    file_name = file_name + ".ppm"
    f = open(file_name, 'wt')
    f.write('P3\n')
    f.write('%s ' % int(grid_length))
    f.write('%s\n' % int(grid_length))
    f.write('%s\n' % int(DOMAIN_RES - 1))
    for x in range(grid_length):
        for y in range(grid_length):
            f.write("%s " % int(grid[x][y][0]))
            f.write("%s " % int(grid[x][y][1]))
            f.write("%s\n" % int(grid[x][y][2]))
    f.close()
