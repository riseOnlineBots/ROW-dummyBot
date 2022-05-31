import cv2 as cv
import numpy as np


class ObjectDetection:
    character_info = None
    character_info_w = 0
    character_info_h = 0
    character_hp_mp_bar = (0, 0, 0, 0)
    character_hp_mp_bar_set = False

    image_flag_method = cv.IMREAD_UNCHANGED
    match_template_method = cv.TM_CCOEFF_NORMED

    def __init__(self):
        self.character_info = cv.imread('images/character_info.jpg', self.image_flag_method)
        self.character_info_w = self.character_info.shape[1]
        self.character_info_h = self.character_info.shape[0]

    def set_character_hp_mp_bar(self, location):
        self.character_hp_mp_bar = location
        self.character_hp_mp_bar_set = True


    def find_character_info(self, screenshot):
        result = cv.matchTemplate(screenshot, self.character_info, self.match_template_method)

        locations = np.where(result == np.max(result))

        return self.locations_to_rectangles(locations)

    def locations_to_rectangles(self, locations):
        locations = list(zip(*locations[::-1]))

        if not locations:
            print('No location found for the character info bar.')
            return np.array([], dtype=np.int32).reshape(0, 4)

        rectangles = []
        for loc in locations:
            rect = [int(loc[0]), int(loc[1]), self.character_info_w, self.character_info_h]
            # Add every box to the list twice in order to retain single (non-overlapping) boxes
            rectangles.append(rect)
            rectangles.append(rect)
        # Apply group rectangles.
        # The groupThreshold parameter should usually be 1. If you put it at 0 then no grouping is
        # done. If you put it at 2 then an object needs at least 3 overlapping rectangles to appear
        # in the result. I've set eps to 0.5, which is:
        # "Relative difference between sides of the rectangles to merge them into a group."
        rectangles, weights = cv.groupRectangles(rectangles, groupThreshold=1, eps=0.5)

        return rectangles
