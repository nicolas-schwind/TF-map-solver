"""
Takes in input an instance name, possibly a solution and output an image file with the solution displayed
"""
from PIL import Image, ImageDraw, ImageFont
import common_tools
import math
import os

COLOR_RANGE0 = (255, 255, 255)
COLOR_RANGE1 = (0, 255, 0)
COLOR_RANGE2 = (0, 0, 255)
COLOR_RANGE3 = (255, 0, 0)
COLOR_RANGE4 = (255, 255, 0)
COLOR_RANGE0 = COLOR_RANGE1
COLOR_RANGE2 = COLOR_RANGE1
COLOR_RANGE3 = COLOR_RANGE1
COLOR_RANGE4 = COLOR_RANGE1

COLOR_FONT = (255, 0, 0)
COLOR_BORDER = (255, 255, 255)
COLOR_FILL = (255, 0, 0, 50)

FILL_NONE = 1
FILL_CIRCLE = 2
FILL_BOXES = 3

TS_FOR_BEZIER_CURVE = [t / 100.0 for t in range(101)]
LIMIT_POINT_CURVE_BR = 1
LIMIT_POINT_CURVE_UR = 2
LIMIT_POINT_CURVE_UL = 3
LIMIT_POINT_CURVE_BL = 4

SIDE_RIGHT = 1
SIDE_TOP = 2
SIDE_LEFT = 3
SIDE_BOTTOM = 4

LINE_WIDTH = 3

HEXAGON_POINT_CORNER_UP = 1
HEXAGON_POINT_CORNER_UP_LEFT = 2
HEXAGON_POINT_CORNER_DOWN_LEFT = 3
HEXAGON_POINT_CORNER_DOWN = 4
HEXAGON_POINT_CORNER_DOWN_RIGHT = 5
HEXAGON_POINT_CORNER_UP_RIGHT = 6


def get_color_antenna(range_antenna):
    if range_antenna == 0:
        return COLOR_RANGE0
    elif range_antenna == 1:
        return COLOR_RANGE1
    elif range_antenna == 2:
        return COLOR_RANGE2
    elif range_antenna == 3:
        return COLOR_RANGE3
    return -1


def make_bezier(xys):
    # xys should be a sequence of 2-tuples (Bezier control points)
    n = len(xys)
    combinations = pascal_row(n - 1)

    def bezier(ts):
        # This uses the generalized formula for bezier curves
        # http://en.wikipedia.org/wiki/B%C3%A9zier_curve#Generalization
        result = []
        for t in ts:
            tpowers = (t ** i for i in range(n))
            upowers = reversed([(1 - t) ** i for i in range(n)])
            coefs = [c * a * b for c, a, b in zip(combinations, tpowers, upowers)]
            result.append(
                tuple(sum([coef * p for coef, p in zip(coefs, ps)]) for ps in zip(*xys)))
        return result

    return bezier


def pascal_row(n, memo={}):
    # This returns the nth row of Pascal's Triangle
    if n in memo:
        return memo[n]
    result = [1]
    x, numerator = 1, n
    for denominator in range(1, n // 2 + 1):
        # print(numerator,denominator,x)
        x *= numerator
        x /= denominator
        result.append(x)
        numerator -= 1
    if n & 1 == 0:
        # n is even
        result.extend(reversed(result[:-1]))
    else:
        result.extend(reversed(result))
    memo[n] = result
    return result


def draw_curved_line_in_single_box(draw, num_line, num_col, range_antenna, nb_pixels_per_unit, limit_point_curve, right_continuous, left_continuous):
    if limit_point_curve == LIMIT_POINT_CURVE_BR:
        point1 = ((num_line + 1) * nb_pixels_per_unit, num_col * nb_pixels_per_unit)
        if right_continuous:
            point2 = ((num_line + 0.8) * nb_pixels_per_unit, (num_col + 0.2) * nb_pixels_per_unit)
        else:
            point2 = ((num_line + 0.8) * nb_pixels_per_unit, num_col * nb_pixels_per_unit)
        point3 = ((num_line + 1.3) * nb_pixels_per_unit, (num_col + 1.3) * nb_pixels_per_unit)
        if left_continuous:
            point4 = ((num_line + 0.2) * nb_pixels_per_unit, (num_col + 0.8) * nb_pixels_per_unit)
        else:
            point4 = (num_line * nb_pixels_per_unit, (num_col + 0.8) * nb_pixels_per_unit)
        point5 = (num_line * nb_pixels_per_unit, (num_col + 1) * nb_pixels_per_unit)
    elif limit_point_curve == LIMIT_POINT_CURVE_UL:
        point1 = ((num_line + 1) * nb_pixels_per_unit, num_col * nb_pixels_per_unit)
        if right_continuous:
            point2 = ((num_line + 0.8) * nb_pixels_per_unit, (num_col + 0.2) * nb_pixels_per_unit)
        else:
            point2 = ((num_line + 1) * nb_pixels_per_unit, (num_col + 0.2) * nb_pixels_per_unit)
        point3 = ((num_line - 0.3) * nb_pixels_per_unit, (num_col - 0.3) * nb_pixels_per_unit)
        if left_continuous:
            point4 = ((num_line + 0.2) * nb_pixels_per_unit, (num_col + 0.8) * nb_pixels_per_unit)
        else:
            point4 = ((num_line + 0.2) * nb_pixels_per_unit, (num_col + 1) * nb_pixels_per_unit)
        point5 = (num_line * nb_pixels_per_unit, (num_col + 1) * nb_pixels_per_unit)
    elif limit_point_curve == LIMIT_POINT_CURVE_BL:
        point1 = (num_line * nb_pixels_per_unit, num_col * nb_pixels_per_unit)
        if right_continuous:
            point2 = ((num_line + 0.2) * nb_pixels_per_unit, (num_col + 0.2) * nb_pixels_per_unit)
        else:
            point2 = ((num_line + 0.2) * nb_pixels_per_unit, num_col * nb_pixels_per_unit)
        point3 = ((num_line - 0.3) * nb_pixels_per_unit, (num_col + 1.3) * nb_pixels_per_unit)
        if left_continuous:
            point4 = ((num_line + 0.8) * nb_pixels_per_unit, (num_col + 0.8) * nb_pixels_per_unit)
        else:
            point4 = ((num_line + 1) * nb_pixels_per_unit, (num_col + 0.8) * nb_pixels_per_unit)
        point5 = ((num_line + 1) * nb_pixels_per_unit, (num_col + 1) * nb_pixels_per_unit)
    else:
        assert limit_point_curve == LIMIT_POINT_CURVE_UR, "ERROR"
        point1 = (num_line * nb_pixels_per_unit, num_col * nb_pixels_per_unit)
        if right_continuous:
            point2 = ((num_line + 0.2) * nb_pixels_per_unit, (num_col + 0.2) * nb_pixels_per_unit)
        else:
            point2 = (num_line * nb_pixels_per_unit, (num_col + 0.2) * nb_pixels_per_unit)
        point3 = ((num_line + 1.3) * nb_pixels_per_unit, (num_col - 0.3) * nb_pixels_per_unit)
        if left_continuous:
            point4 = ((num_line + 0.8) * nb_pixels_per_unit, (num_col + 0.8) * nb_pixels_per_unit)
        else:
            point4 = ((num_line + 0.8) * nb_pixels_per_unit, (num_col + 1) * nb_pixels_per_unit)
        point5 = ((num_line + 1) * nb_pixels_per_unit, (num_col + 1) * nb_pixels_per_unit)

    xys = [point1, point2, point3, point4, point5]
    bezier = make_bezier(xys)
    points = bezier(TS_FOR_BEZIER_CURVE)
    draw.line(points, width=LINE_WIDTH, fill=get_color_antenna(range_antenna))


def draw_line_edge(draw, num_line, num_col, range_antenna, nb_pixels_per_unit, side):
    if side == SIDE_RIGHT:
        draw.line([(num_line + 1) * nb_pixels_per_unit, num_col * nb_pixels_per_unit, (num_line + 1) * nb_pixels_per_unit, (num_col + 1) * nb_pixels_per_unit], width=LINE_WIDTH, fill=get_color_antenna(range_antenna))
    elif side == SIDE_LEFT:
        draw.line([num_line * nb_pixels_per_unit, num_col * nb_pixels_per_unit, num_line * nb_pixels_per_unit, (num_col + 1) * nb_pixels_per_unit], width=LINE_WIDTH, fill=get_color_antenna(range_antenna))
    elif side == SIDE_TOP:
        draw.line([num_line * nb_pixels_per_unit, num_col * nb_pixels_per_unit, (num_line + 1) * nb_pixels_per_unit, num_col * nb_pixels_per_unit], width=LINE_WIDTH, fill=get_color_antenna(range_antenna))
    else:
        assert side == SIDE_BOTTOM, "ERROR"
        draw.line([num_line * nb_pixels_per_unit, (num_col + 1) * nb_pixels_per_unit, (num_line + 1) * nb_pixels_per_unit, (num_col + 1) * nb_pixels_per_unit], width=LINE_WIDTH, fill=get_color_antenna(range_antenna))


def draw_curved_line_edge(draw, num_line, num_col, range_antenna, nb_pixels_per_unit, side):
    if side == SIDE_RIGHT:
        point1 = ((num_line + 1) * nb_pixels_per_unit, num_col * nb_pixels_per_unit)
        point2 = ((num_line + 1.2) * nb_pixels_per_unit, (num_col + 0.5) * nb_pixels_per_unit)
        point3 = ((num_line + 1) * nb_pixels_per_unit, (num_col + 1) * nb_pixels_per_unit)
    elif side == SIDE_LEFT:
        point1 = (num_line * nb_pixels_per_unit, num_col * nb_pixels_per_unit)
        point2 = ((num_line - 0.2) * nb_pixels_per_unit, (num_col + 0.5) * nb_pixels_per_unit)
        point3 = (num_line * nb_pixels_per_unit, (num_col + 1) * nb_pixels_per_unit)
    elif side == SIDE_TOP:
        point1 = (num_line * nb_pixels_per_unit, num_col * nb_pixels_per_unit)
        point2 = ((num_line + 0.5) * nb_pixels_per_unit, (num_col - 0.2) * nb_pixels_per_unit)
        point3 = ((num_line + 1) * nb_pixels_per_unit, num_col * nb_pixels_per_unit)
    else:
        assert side == SIDE_BOTTOM, "ERROR"
        point1 = (num_line * nb_pixels_per_unit, (num_col + 1) * nb_pixels_per_unit)
        point2 = ((num_line + 0.5) * nb_pixels_per_unit, (num_col + 1.2) * nb_pixels_per_unit)
        point3 = ((num_line + 1) * nb_pixels_per_unit, (num_col + 1) * nb_pixels_per_unit)

    xys = [point1, point2, point3]
    bezier = make_bezier(xys)
    points = bezier(TS_FOR_BEZIER_CURVE)
    draw.line(points, width=LINE_WIDTH, fill=get_color_antenna(range_antenna))


def draw_nice_shape(draw, num_line, num_col, range_antenna, nb_pixels_per_unit):
    draw_curved_line_edge(draw, num_col + range_antenna, num_line, range_antenna, nb_pixels_per_unit, side=SIDE_RIGHT)
    for x in range(range_antenna):
        if range_antenna == 1:
            draw_curved_line_in_single_box(draw, num_col + 1, num_line + 1, range_antenna, nb_pixels_per_unit, limit_point_curve=LIMIT_POINT_CURVE_UL, right_continuous=False, left_continuous=False)
        elif x == 0:
            draw_curved_line_in_single_box(draw, num_col + range_antenna, num_line + 1, range_antenna, nb_pixels_per_unit,
                                           limit_point_curve=LIMIT_POINT_CURVE_UL, right_continuous=False,
                                           left_continuous=True)
        elif x == range_antenna - 1:
            draw_curved_line_in_single_box(draw, num_col + range_antenna - x, num_line + 1 + x, range_antenna, nb_pixels_per_unit,
                                           limit_point_curve=LIMIT_POINT_CURVE_UL, right_continuous=True,
                                           left_continuous=False)
        else:
            draw_curved_line_in_single_box(draw, num_col + range_antenna - x, num_line + 1 + x, range_antenna, nb_pixels_per_unit,
                                           limit_point_curve=LIMIT_POINT_CURVE_UL, right_continuous=False,
                                           left_continuous=False)
    draw_curved_line_edge(draw, num_col, num_line + range_antenna, range_antenna, nb_pixels_per_unit, side=SIDE_BOTTOM)
    for x in range(range_antenna):
        if range_antenna == 1:
            draw_curved_line_in_single_box(draw, num_col - 1, num_line + 1, range_antenna, nb_pixels_per_unit,
                                           limit_point_curve=LIMIT_POINT_CURVE_UR, right_continuous=False,
                                           left_continuous=False)
        elif x == 0:
            draw_curved_line_in_single_box(draw, num_col - 1, num_line + range_antenna, range_antenna, nb_pixels_per_unit,
                                           limit_point_curve=LIMIT_POINT_CURVE_UR, right_continuous=True,
                                           left_continuous=False)
        elif x == range_antenna - 1:
            draw_curved_line_in_single_box(draw, num_col - 1 - x, num_line + range_antenna - x, range_antenna, nb_pixels_per_unit,
                                           limit_point_curve=LIMIT_POINT_CURVE_UR, right_continuous=False,
                                           left_continuous=True)
        else:
            draw_curved_line_in_single_box(draw, num_col - 1 - x, num_line + range_antenna - x, range_antenna, nb_pixels_per_unit,
                                           limit_point_curve=LIMIT_POINT_CURVE_UR, right_continuous=False,
                                           left_continuous=False)
    draw_curved_line_edge(draw, num_col - range_antenna, num_line, range_antenna, nb_pixels_per_unit, side=SIDE_LEFT)
    for x in range(range_antenna):
        if range_antenna == 1:
            draw_curved_line_in_single_box(draw, num_col - 1, num_line - 1, range_antenna, nb_pixels_per_unit,
                                           limit_point_curve=LIMIT_POINT_CURVE_BR, right_continuous=False,
                                           left_continuous=False)
        elif x == 0:
            draw_curved_line_in_single_box(draw, num_col - range_antenna, num_line - 1, range_antenna, nb_pixels_per_unit,
                                           limit_point_curve=LIMIT_POINT_CURVE_BR, right_continuous=True,
                                           left_continuous=False)
        elif x == range_antenna - 1:
            draw_curved_line_in_single_box(draw, num_col - range_antenna + x, num_line - 1 - x, range_antenna, nb_pixels_per_unit,
                                           limit_point_curve=LIMIT_POINT_CURVE_BR, right_continuous=False,
                                           left_continuous=True)
        else:
            draw_curved_line_in_single_box(draw, num_col - range_antenna + x, num_line - 1 - x, range_antenna, nb_pixels_per_unit,
                                           limit_point_curve=LIMIT_POINT_CURVE_BR, right_continuous=False,
                                           left_continuous=False)
    draw_curved_line_edge(draw, num_col, num_line - range_antenna, range_antenna, nb_pixels_per_unit, side=SIDE_TOP)
    for x in range(range_antenna):
        if range_antenna == 1:
            draw_curved_line_in_single_box(draw, num_col + 1, num_line - 1, range_antenna, nb_pixels_per_unit,
                                           limit_point_curve=LIMIT_POINT_CURVE_BL, right_continuous=False,
                                           left_continuous=False)
        elif x == 0:
            draw_curved_line_in_single_box(draw, num_col + 1, num_line - range_antenna, range_antenna, nb_pixels_per_unit,
                                           limit_point_curve=LIMIT_POINT_CURVE_BL, right_continuous=True,
                                           left_continuous=False)
        elif x == range_antenna - 1:
            draw_curved_line_in_single_box(draw, num_col + 1 + x, num_line - range_antenna + x, range_antenna, nb_pixels_per_unit,
                                           limit_point_curve=LIMIT_POINT_CURVE_BL, right_continuous=False,
                                           left_continuous=True)
        else:
            draw_curved_line_in_single_box(draw, num_col + 1 + x, num_line - range_antenna + x, range_antenna, nb_pixels_per_unit,
                                           limit_point_curve=LIMIT_POINT_CURVE_BL, right_continuous=False,
                                           left_continuous=False)


def draw_nice_but_simple_shape(draw, num_line, num_col, range_antenna, nb_pixels_per_unit):
    draw_curved_line_edge(draw, num_col + range_antenna, num_line, range_antenna, nb_pixels_per_unit, side=SIDE_RIGHT)
    point1 = ((num_col + 1 + range_antenna) * nb_pixels_per_unit, num_line * nb_pixels_per_unit)
    point2 = ((num_col + 1 + (1.2 * range_antenna / 2)) * nb_pixels_per_unit, (num_line - (1.2 * range_antenna / 2)) * nb_pixels_per_unit)
    point3 = ((num_col + 1) * nb_pixels_per_unit, (num_line - range_antenna) * nb_pixels_per_unit)
    xys = [point1, point2, point3]
    bezier = make_bezier(xys)
    points = bezier(TS_FOR_BEZIER_CURVE)
    draw.line(points, width=LINE_WIDTH, fill=get_color_antenna(range_antenna))

    draw_curved_line_edge(draw, num_col, num_line + range_antenna, range_antenna, nb_pixels_per_unit, side=SIDE_BOTTOM)
    for x in range(range_antenna):
        if range_antenna == 1:
            draw_curved_line_in_single_box(draw, num_col - 1, num_line + 1, range_antenna, nb_pixels_per_unit,
                                           limit_point_curve=LIMIT_POINT_CURVE_UR, right_continuous=False,
                                           left_continuous=False)
        elif x == 0:
            draw_curved_line_in_single_box(draw, num_col - 1, num_line + range_antenna, range_antenna, nb_pixels_per_unit,
                                           limit_point_curve=LIMIT_POINT_CURVE_UR, right_continuous=True,
                                           left_continuous=False)
        elif x == range_antenna - 1:
            draw_curved_line_in_single_box(draw, num_col - 1 - x, num_line + range_antenna - x, range_antenna, nb_pixels_per_unit,
                                           limit_point_curve=LIMIT_POINT_CURVE_UR, right_continuous=False,
                                           left_continuous=True)
        else:
            draw_curved_line_in_single_box(draw, num_col - 1 - x, num_line + range_antenna - x, range_antenna, nb_pixels_per_unit,
                                           limit_point_curve=LIMIT_POINT_CURVE_UR, right_continuous=False,
                                           left_continuous=False)
    draw_curved_line_edge(draw, num_col - range_antenna, num_line, range_antenna, nb_pixels_per_unit, side=SIDE_LEFT)
    for x in range(range_antenna):
        if range_antenna == 1:
            draw_curved_line_in_single_box(draw, num_col - 1, num_line - 1, range_antenna, nb_pixels_per_unit,
                                           limit_point_curve=LIMIT_POINT_CURVE_BR, right_continuous=False,
                                           left_continuous=False)
        elif x == 0:
            draw_curved_line_in_single_box(draw, num_col - range_antenna, num_line - 1, range_antenna, nb_pixels_per_unit,
                                           limit_point_curve=LIMIT_POINT_CURVE_BR, right_continuous=True,
                                           left_continuous=False)
        elif x == range_antenna - 1:
            draw_curved_line_in_single_box(draw, num_col - range_antenna + x, num_line - 1 - x, range_antenna, nb_pixels_per_unit,
                                           limit_point_curve=LIMIT_POINT_CURVE_BR, right_continuous=False,
                                           left_continuous=True)
        else:
            draw_curved_line_in_single_box(draw, num_col - range_antenna + x, num_line - 1 - x, range_antenna, nb_pixels_per_unit,
                                           limit_point_curve=LIMIT_POINT_CURVE_BR, right_continuous=False,
                                           left_continuous=False)
    draw_curved_line_edge(draw, num_col, num_line - range_antenna, range_antenna, nb_pixels_per_unit, side=SIDE_TOP)
    for x in range(range_antenna):
        if range_antenna == 1:
            draw_curved_line_in_single_box(draw, num_col + 1, num_line - 1, range_antenna, nb_pixels_per_unit,
                                           limit_point_curve=LIMIT_POINT_CURVE_BL, right_continuous=False,
                                           left_continuous=False)
        elif x == 0:
            draw_curved_line_in_single_box(draw, num_col + 1, num_line - range_antenna, range_antenna, nb_pixels_per_unit,
                                           limit_point_curve=LIMIT_POINT_CURVE_BL, right_continuous=True,
                                           left_continuous=False)
        elif x == range_antenna - 1:
            draw_curved_line_in_single_box(draw, num_col + 1 + x, num_line - range_antenna + x, range_antenna, nb_pixels_per_unit,
                                           limit_point_curve=LIMIT_POINT_CURVE_BL, right_continuous=False,
                                           left_continuous=True)
        else:
            draw_curved_line_in_single_box(draw, num_col + 1 + x, num_line - range_antenna + x, range_antenna, nb_pixels_per_unit,
                                           limit_point_curve=LIMIT_POINT_CURVE_BL, right_continuous=False,
                                           left_continuous=False)

def offset(size_init_map):
    #valid values for size_init_map are supposed to be 4, 8, 16, 32, 64, 128, 256
    return (int(-760 // size_init_map), int(-1530 // size_init_map))


def draw_text(draw, point, cost, range_antenna, size_init_map, width, height, font):
    center_point = get_hexagon_center_point(point, width, height)
    draw.text((center_point[0] + offset(size_init_map)[0], center_point[1] + offset(size_init_map)[1]), str(cost),
              fill=get_color_antenna(range_antenna), font=font)


def draw_ellipse(draw, point, range_antenna, width, height, fill=False):
    ray = height // 2
    center_point = get_hexagon_center_point(point, width, height)
    multiplicator = -1
    if range_antenna == 0:
        multiplicator = 1
    elif range_antenna == 1:
        multiplicator = 2.65
    elif range_antenna == 2:
        multiplicator = 4.35
    elif range_antenna == 3:
        multiplicator = 6.1
    elif range_antenna == 4:
        multiplicator = 7.8
    multiplied_ray = ray * multiplicator
    if fill:
        draw.ellipse([center_point[0] - multiplied_ray, center_point[1] - multiplied_ray,
                     center_point[0] + multiplied_ray, center_point[1] + multiplied_ray], fill=COLOR_FILL,
                     outline=get_color_antenna(range_antenna), width=LINE_WIDTH)
    else:
        draw.ellipse([center_point[0] - multiplied_ray, center_point[1] - multiplied_ray,
                     center_point[0] + multiplied_ray, center_point[1] + multiplied_ray],
                     outline=get_color_antenna(range_antenna), width=LINE_WIDTH)


def fill_box(draw, num_line, num_col, nb_pixels_per_unit):
    draw.rectangle([num_col * nb_pixels_per_unit, num_line * nb_pixels_per_unit, (num_col + 1) * nb_pixels_per_unit - 1,
                    (num_line + 1) * nb_pixels_per_unit - 1], fill=COLOR_FILL)


def fill_boxes(draw, num_line, num_col, range_antenna, nb_pixels_per_unit):
    for x in range(num_line - range_antenna, num_line + 1 + range_antenna):
        for y in range(num_col - range_antenna, num_col + 1 + range_antenna):
            if abs(x - num_line) + abs(y - num_col) <= range_antenna:
                fill_box(draw, x, y, nb_pixels_per_unit)


def put_antenna(draw, point, cost, range_antenna, size_init_map, width, height, font, fill_type=FILL_CIRCLE):
    draw_text(draw, point, cost, range_antenna, size_init_map, width, height, font)
    draw_ellipse(draw, point, range_antenna, width, height, fill=(fill_type == FILL_CIRCLE))
    #draw_nice_shape(draw, num_line, num_col, range_antenna, nb_pixels_per_unit)
    #draw_nice_but_simple_shape(draw, num_line, num_col, range_antenna, nb_pixels_per_unit)


"""
takes an instance name <instance_name>, and convert <instance_name>.ppm file to a png file
of a given resolution. Resolution should be an integer and is set by default to 1024
If solution=None then no solution is displayed, only the plain map is generated into <instance_name>.png
If solution=SOLUTION_FOR_TF then solution for TF is also displayed using the file <filename>-solution-TF.sol is used
etc., solution can also have the values SOLUTION_FOR_ROBUST_TF, SOLUTION_FOR_PARTIAL_ROBUST_TF, and SOLUTION_FOR_RECOVERABLE_TF
and should just contain one line listing the ids of all agents
"""


def generate_png_map(instance_name: str, solution_type=None, resolution=1024):
    f = open(instance_name + '.ppm', 'r')
    f.readline()
    size_init_map = int(f.readline().split()[0])
    nb_pixels_per_unit = resolution / size_init_map
    print(nb_pixels_per_unit)
    output_image = Image.new('RGB', (size_init_map, size_init_map))
    f.readline()
    data_image = []

    # from here, read all pixels from the ppm file and write it into data_image
    for x in range(size_init_map):
        for y in range(size_init_map):
            line = f.readline().split()
            data_image.append((int(line[0]), int(line[1]), int(line[2])))
    output_image.putdata(data_image)

    # resize the image at the given resolution (by deafult, 1024 * 1024)
    output_image = output_image.resize((resolution, resolution), resample=Image.BOX)

    solution_details = None
    print(solution_type)
    if solution_type:
        print('here')
        draw = ImageDraw.Draw(output_image, 'RGBA')
        # the font size should be revised according to different maps (i.e., according to resolution + size_init_map)
        font = ImageFont.truetype('/System/Library/Fonts/ArialHB.ttc', int(resolution / 10))
        # read the solution
        solution_details = common_tools.read_solution_file(instance_name, solution_type)
        print(solution_details)
        # solution_details[0] contains the list of agent ids from the solution
        # solution_details[1] contains the deployment cost of the solution
        # solution_details[2] contains additional paramters (k or <k, t>, etc.)
        agent_list_in_solution = common_tools.read_agents_from_info_file(instance_name, solution_details[0])
        print(agent_list_in_solution)
        # put all antennas from the solution
        for agent in agent_list_in_solution:
            print(f'put {agent}')
            # put_antenna(draw, agent[4], agent[5], agent[1], agent[3], nb_pixels_per_unit, font)
            put_antenna(draw, agent[4], agent[5], agent[1], agent[3], nb_pixels_per_unit, font, fill_type=FILL_NONE)

        # fill_boxes(draw, 3, 5, 1, nb_pixels_per_unit)
        # fill_box(draw, 3, 5, nb_pixels_per_unit)
        #draw_nice_shape(draw, 4, 5, 3, nb_pixels_per_unit)
        #put_antenna(draw, 4, 5, 4, 3, nb_pixels_per_unit, font, fill_type=FILL_NONE)




    if solution_type == common_tools.SOLUTION_FOR_TF:
        output_image.save(f'{instance_name}-solution-TF.png')
    elif solution_type == common_tools.SOLUTION_FOR_ROBUST_TF:
        assert solution_details, "ERROR"
        output_image.save(f'{instance_name}-solution-robust-TF.png')
    elif solution_type == common_tools.SOLUTION_FOR_PARTIAL_ROBUST_TF:
        assert solution_details, "ERROR"
        output_image.save(
            f'{instance_name}-solution-partial-robust-TF-k{solution_details[2][0]}-t{solution_details[2][1]}.png')
    elif solution_type == common_tools.SOLUTION_FOR_RECOVERABLE_TF:
        assert solution_details, "ERROR"
        output_image.save(f'{instance_name}-solution-recoverable-TF.png')
    else:
        output_image.save(f'{instance_name}.png')


def get_hexagon_center_point(point, width, height):
    hexagonal_point_x = (2 * point[1] + 1) * 0.5 * width
    if point[0] % 2 == 1:
        hexagonal_point_x += 0.5 * width
    hexagonal_point_y = (3 * point[0] + 2) * 0.25 * height

    return hexagonal_point_x, hexagonal_point_y


def get_hexagon_corner_point(point, width, height, which_corner):
    result = None
    hexagonal_point = get_hexagon_center_point(point, width, height)
    if which_corner == HEXAGON_POINT_CORNER_UP:
        result = (hexagonal_point[0], hexagonal_point[1] - 0.5 * height)
    elif which_corner == HEXAGON_POINT_CORNER_UP_LEFT:
        result = (hexagonal_point[0] - 0.5 * width, hexagonal_point[1] - 0.25 * height)
    elif which_corner == HEXAGON_POINT_CORNER_DOWN_LEFT:
        result = (hexagonal_point[0] - 0.5 * width, hexagonal_point[1] + 0.25 * height)
    elif which_corner == HEXAGON_POINT_CORNER_DOWN:
        result = (hexagonal_point[0], hexagonal_point[1] + 0.5 * height)
    elif which_corner == HEXAGON_POINT_CORNER_DOWN_RIGHT:
        result = (hexagonal_point[0] + 0.5 * width, hexagonal_point[1] + 0.25 * height)
    elif which_corner == HEXAGON_POINT_CORNER_UP_RIGHT:
        result = (hexagonal_point[0] + 0.5 * width, hexagonal_point[1] - 0.25 * height)
    return result


def draw_filled_hexagon(draw, point, color, width, height):
    hexagonal_point = get_hexagon_center_point(point, width, height)

    point1 = get_hexagon_corner_point(point, width, height, HEXAGON_POINT_CORNER_UP)
    point2 = get_hexagon_corner_point(point, width, height, HEXAGON_POINT_CORNER_UP_LEFT)
    point3 = get_hexagon_corner_point(point, width, height, HEXAGON_POINT_CORNER_DOWN_LEFT)
    point4 = get_hexagon_corner_point(point, width, height, HEXAGON_POINT_CORNER_DOWN)
    point5 = get_hexagon_corner_point(point, width, height, HEXAGON_POINT_CORNER_DOWN_RIGHT)
    point6 = get_hexagon_corner_point(point, width, height, HEXAGON_POINT_CORNER_UP_RIGHT)
    #print(f'draw polygon ({point1}, {point2}, {point3}, {point4}, {point5}, {point6}), color: {color}')
    draw.polygon([point1, point2, point3, point4, point5, point6], fill=color)
    font = ImageFont.truetype('/System/Library/Fonts/ArialHB.ttc', 20)
    x = int(hexagonal_point[0])
    y = int(hexagonal_point[1])
    #draw.text(hexagonal_point, str(point), fill=(255, 255, 255), font=font)


def draw_all_hexagons(draw, data_image, size_init_map, width, height):
    coord_x = 0
    coord_y = 0
    data_image_counter = 0
    for box in data_image:
        draw_filled_hexagon(draw, (coord_x, coord_y), data_image[data_image_counter], width, height)
        coord_y += 1
        if coord_y % size_init_map == 0:
            coord_y = 0
            coord_x += 1
        data_image_counter += 1


def get_solution_details_into_text(solution_details):
    shift = '    '
    if solution_details[8]:
        result = shift + 'Optimal solution found for '
    else:
        result = shift + 'Sub-optimal solution found for '
    if solution_details[0] == 'TF':
        result += 'TF\n'
    elif solution_details[0] == 'KTF':
        result += f'{solution_details[5][0]}-robust TF\n'
    elif solution_details[0] == 'PTF':
        result += f'({solution_details[5][0]}, {solution_details[5][1]})-partial robust TF\n'
    elif solution_details[0] == 'PTF_ANYTIME':
        result += f'({solution_details[5][0]}, {solution_details[5][1]})-partial robust TF (anytime)\n'
    elif solution_details[0] == 'RecTF':
        result += f'{solution_details[5][0]}-recoverable TF\n'
    result += shift + f'Deployment cost: {solution_details[2]}\n'
    #if solution_details[0] != 'TF':
    #    result += shift + f'Worst (lowest) percentage coverage after {solution_details[5][0]} agent loss: {solution_details[6]}\n'
    #result += shift + f'Repair cost in the worst case: '
    #if solution_details[3] >= 0:
    #    result += f'{solution_details[3]}\n'
    #else:
    #    result += 'not computed\n'
    result += shift + f'Computation time: {solution_details[4]:.2f} seconds'
    if solution_details[7] == 'NO_CUT':
        result += ' (without cut)'
    elif solution_details[7] == 'CUT':
        result += ' (with cut)'
    elif solution_details[7] == 'CUT+':
        result += ' (with modified cut)'
    return result


def generate_png_maps_hexagonal(directory_name:str, instance_name: str, res=2, solution_name=None, with_text=True):
    # res should range between 1 and 5
    # here size is the nb of pixels between the center of an hexagon and one of its corners
    # size=64 is good for initial resolution of 4, so size = (2 ** (10 - resolution))
    Image.MAX_IMAGE_PIXELS = None
    f = open(directory_name + '/' + instance_name + '.ppm', 'r')
    f.readline()
    size_init_map = int(f.readline().split()[0])
    size = (128 * (4 ** res)) / size_init_map
    width = math.sqrt(3) * size
    total_width = (size_init_map + 0.5) * width
    height = 2 * size
    #height_for_white_space_below = 3.5 * size
    height_for_white_space_below = 700
    if not with_text:
        height_for_white_space_below = 0
    #print(f'white space height: {height_for_white_space_below}')
    total_height = (size_init_map // 2) * 1.5 * height + 0.25 * height + height_for_white_space_below
    if size_init_map % 2 == 1:
        total_height += 0.75 * height

    total_width = int(total_width)
    total_height = int(total_height)

    #print(f'size_init_map = {size_init_map}, total_width = {total_width}, total_height = {total_height}')

    f.readline()
    data_image = []

    # from here, read all pixels from the ppm file and write it into data_image
    for x in range(size_init_map):
        for y in range(size_init_map):
            line = f.readline().split()
            data_image.append((int(line[0]), int(line[1]), int(line[2])))

    if not solution_name:
        # save the plain problem, i.e., the png picture without any solution
        output_image = Image.new('RGB', (int(total_width), int(total_height)), (255, 255, 255))
        draw = ImageDraw.Draw(output_image, 'RGBA')
        draw_all_hexagons(draw, data_image, size_init_map, width, height)
        output_image_only_map = output_image.crop((0, 0, total_width, total_height - height_for_white_space_below))
        output_image_only_map.save(f'{directory_name}/{instance_name}.png')
    else:
        # now, do for each solution file
        #all_solution_files = [solution_file for solution_file in os.listdir(directory_name) if
        #                      instance_name + '-' in solution_file and solution_file.endswith('.sol')]
        # the font size should be revised according to different maps (i.e., according to resolution + size_init_map)
        font = ImageFont.truetype('/System/Library/Fonts/ArialHB.ttc', int(1.5 * size))
        #for solution_file in all_solution_files:
        solution_details = None
        file_name = None
        output_image = Image.new('RGB', (int(total_width), int(total_height)), (255, 255, 255))
        draw = ImageDraw.Draw(output_image, 'RGBA')
        draw_all_hexagons(draw, data_image, size_init_map, width, height)

        # read the solution
        solution_details = common_tools.read_solution_file(directory_name + '/' + solution_name)
        #print(solution_details)
        # solution_details[0] contains the type of problem (TF / KTF / PTF / RecTF)
        # solution_details[1] contains the list of agent ids from the solution
        # solution_details[2] contains the deployment cost of the solution
        # solution_details[3] contains the repair cost (if computed / found)
        # solution_details[4] contains the time to compute the solution
        # solution_details[5] contains additional parameters (k or <k, t>, etc.)
        # solution_details[6] contains the percentage covered in the worst case
        if solution_details:
            agent_list_in_solution = common_tools.read_agents_from_info_file(directory_name + '/' + instance_name, solution_details[1])
            #print(agent_list_in_solution)
            # put all antennas from the solution
            for agent in agent_list_in_solution:
                #print(f'put {agent}')
                # put_antenna(draw, agent[4], agent[5], agent[1], agent[3], nb_pixels_per_unit, font)
                put_antenna(draw, (agent[4], agent[5]), agent[1], agent[3], size_init_map, width, height, font, fill_type=FILL_CIRCLE)
            # printing on the image the solution details
            text_solution_details = get_solution_details_into_text(solution_details)
            font_text_solution_details = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', int(size * size_init_map // 24))
            draw.text((0, total_height - 0.5 * height_for_white_space_below), str(text_solution_details), fill=(0, 0, 0), font=font_text_solution_details)
            # saving the png file
            output_image.save(f'{directory_name}/{solution_name[:-4]}.png')
