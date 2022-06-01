from math import sqrt

from PIL import Image

RED = 0
GREEN = 1
BLUE = 2
COLORS = [RED, GREEN, BLUE]
RED_HEALTH = (167, 42, 37)
BLUE_HEALTH = (24, 65, 115)
HEALTH_BORDER = (0, 0, 0)
image = Image.open("images/character_info.jpg")


def close_enough_to(src, target, delta):
    diff = 0
    for color in COLORS:
        diff += (src[color] - target[color]) ** 2
    diff = sqrt(diff)
    return diff <= delta


class HealthBar:
    def __init__(self, team, health_percentage, length, pos):
        self.team = team
        self.health_percentage = health_percentage
        self.length = length
        self.pos = pos

    def __str__(self):
        return "team {}, percentage {}, length {}, pos {}".format(self.team,
                                                                  self.health_percentage,
                                                                  self.length,
                                                                  self.pos
                                                                  )

    def __repr__(self):
        return str(self)


def flood_fill_health_bar(image, pos, color, traversed):
    (x, y) = pos
    health_pixels = 0
    while close_enough_to(image.getpixel((x, y)), color) \
            and (x, y) not in traversed:
        health_pixels += 1
        traversed.add((x, y))
        x += 1
    black_pixels = 0
    while close_enough_to(image.getpixel((x, y)), HEALTH_BORDER, 50) \
            and (x, y) not in traversed:
        black_pixels += 1
        traversed.add((x, y))
        x += 1
    if black_pixels > 0:
        if color is RED_HEALTH:
            team = "red"
        else:
            team = "blue"
        percent_health = health_pixels / (health_pixels + black_pixels)
        return HealthBar(team, percent_health, health_pixels + black_pixels, pos)


def in_bounds(image, pos):
    return pos[0] >= 0 and pos[1] >= 0 \
           and pos[0] < image.width and pos[1] < image.height


def flood_fill_image(image, start, delta):
    flood_fill_queue = [start]
    traversed = []
    color = image.getpixel(start)
    pos = start
    pix = image.load()
    while len(flood_fill_queue):
        (x, y) = flood_fill_queue.pop()
        positions = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
        for position in positions:
            if in_bounds(image, position) \
                    and close_enough_to(image.getpixel(position), color, delta):
                if position not in traversed:
                    flood_fill_queue.append(position)
                    traversed.append(position)
                    (x, y) = position
                    pix[x, y] = (0, 0, 255)
    return traversed


def get_width(positions):
    return get_max_x(positions) - get_min_x(positions)


def get_height(positions):
    return get_max_y(positions) - get_min_y(positions)


def get_max_x(positions):
    return sorted(list(positions), key=lambda x: x[0])[-1][0]


def get_max_y(positions):
    return sorted(list(positions), key=lambda x: x[1])[-1][1]


def get_min_x(positions):
    return sorted(list(positions), key=lambda x: x[0])[0][0]


def get_min_y(positions):
    return sorted(list(positions), key=lambda x: x[1])[0][1]


def find_health_bars(image):
    traversed = set()
    health_bars = []
    pix = image.load()
    (width, height) = image.size
    for col in range(0, width):
        for row in range(0, height):
            #  pix = image.getpixel((col, row))
            if (col, row) in traversed:
                continue
            for health_color in [RED_HEALTH, BLUE_HEALTH]:
                border_pixels = []
                if close_enough_to(image.getpixel((col, row)), health_color, 10):
                    health_pixels = flood_fill_image(image, (col, row), 100)
                    for pos in health_pixels:
                        (x, y) = pos
                        traversed.add(pos)
                        pix[x, y] = (255, 255, 0)
                    border_pixels = flood_fill_image(image, (col - 1, row - 1), 30)
                    if len(border_pixels) == 0:
                        continue
                    health_bar_width = get_width(border_pixels)
                    health_bar_height = get_height(border_pixels)
                    health_width = get_width(health_pixels)
                    if abs(health_bar_width / health_bar_height) - 10 <= 0.5:
                        team = "blue" if health_color == BLUE_HEALTH else "red"
                        percent_health = health_width / health_bar_width
                        health_bar = HealthBar(team, percent_health, health_bar_width, (col, row))
                        health_bars.append(health_bar)

                for pos in border_pixels:
                    (x, y) = pos
                    traversed.add(pos)
                    pix[x, y] = (0, 255, 255)
    health_bars = [health_bar for health_bar in health_bars if health_bar is not None]
    health_bars.sort(key=lambda x: x.length)
    return health_bars

