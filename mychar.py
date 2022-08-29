from threading import Lock, Thread

import cv2 as cv
import numpy as np

from hsvfilter import HsvFilter

character_info_bar_hsv = HsvFilter(0, 0, 111, 0, 255, 255, 0, 0, 34, 0)


def locations_to_rectangles(locations, size):
    locations = list(zip(*locations[::-1]))

    if not locations:
        print('No location found for the character info bar.')
        return np.array([], dtype=np.int32).reshape(0, 4)

    rectangles = []
    for loc in locations:
        rect = [int(loc[0]), int(loc[1]), size[1], size[0]]
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


class MyChar:
    character_info = None
    character_info_size = (0, 0)  # (height, width)
    character_hp_mp_bar = (0, 0, 0, 0)
    character_hp_mp_bar_set = False

    hp_item = None
    hp_item_size = (0, 0)  # (height, width)
    hp_item_location = (0, 0, 0, 0)
    hp_item_location_set = False

    mp_item = None
    mp_item_size = (0, 0)  # (height, width)
    mp_item_location = (0, 0, 0, 0)
    mp_item_location_set = False

    image_flag_method = cv.IMREAD_UNCHANGED
    match_template_method = cv.TM_CCOEFF_NORMED

    stopped = True
    lock = None
    screenshot = None

    def __init__(self, window_offset, window_size):
        self.character_info = cv.imread('images/character_info.jpg', self.image_flag_method)
        self.character_info_size = self.character_info.shape

        self.hp_item = cv.imread('images/pots/hp.jpg', self.image_flag_method)
        self.hp_item_size = self.hp_item.shape

        self.mp_item = cv.imread('images/pots/mp.jpg', self.image_flag_method)
        self.mp_item_size = self.mp_item.shape

        # create a thread lock object
        self.lock = Lock()

        # for translating window positions into screen positions, it's easier to just
        # get the offsets and window size from WindowCapture rather than passing in
        # the whole object
        self.window_offset = window_offset
        self.window_w = window_size[0]
        self.window_h = window_size[1]

    def update_screenshot(self, screenshot):
        self.lock.acquire()
        self.screenshot = screenshot
        self.lock.release()

    def start(self):
        self.stopped = False
        t = Thread(target=self.current_hp_mp)
        t.start()

    def stop(self):
        self.stopped = True

    def set_character_hp_mp_bar(self, location):
        self.character_hp_mp_bar = location
        self.character_hp_mp_bar_set = True

    def find_character_info(self, screenshot):
        result = cv.matchTemplate(screenshot, self.character_info, self.match_template_method)

        locations = np.where(result == np.max(result))

        return locations_to_rectangles(locations, self.character_info_size)

    def current_hp_mp(self):
        if self.character_hp_mp_bar_set:
            rectangles = self.character_hp_mp_bar
        else:
            rectangles = self.find_character_info(self.screenshot)
            self.set_character_hp_mp_bar(rectangles)

        gray = cv.imread("test.webp", 0)
        bar = gray[33, 92:337]
        # cv.imshow('q', gray)

        xPos, yPos, wPos, hPos = rectangles[0]
        xPos = xPos + 10
        wPos = wPos - 35
        yPos = yPos + 5
        hPos = hPos - 46
        # test = self.screenshot[yPos:yPos + hPos, xPos:xPos + wPos]
        test = cv.cvtColor(self.screenshot, cv.COLOR_BGR2GRAY)
        test = test[33, 92:337]
        test = cv.resize(test, (0, 0), fx=2.5, fy=2.5)
        cv.imshow('test', test)
        print(test)
        for i, x in enumerate(test):
            if x < 80:
                print(f"{(i / len(test))*100:.1f}%")
                break




        # x, y, w, h = rectangles[0]
        # w = w - 160
        # h = h - 10
        # y = y + 6
        # x = x + 80
        # cv.imshow('screensot', screenshot)
        # screenshot = screenshot[y:y + h, x:x + w]
        # screenshot = cv.resize(screenshot, (0, 0), fx=2.5, fy=2.5)
        # output = vision_object.apply_hsv_filter(screenshot, character_info_bar_hsv)
        # cv.imshow('test', output)

        # config = r'--psm 11 --oem 3 -c tessedit_char_whitelist=0123456789/'
        # detected_values = pytesseract.image_to_string(output, config=config) \
        #     .split('\n')
        # detected_values_result = []
        #
        # for value in detected_values:
        #     if value and value.replace('/', '').isdigit():
        #         detected_values_result.append(value.strip().replace(' ', ''))
        #
        # values = []
        #
        # for value in detected_values_result:
        #     value = value.split('/')
        #
        #     if len(value) == 2:
        #         values.append(value[0])
        #         values.append(value[1])

        # print(values)




# xPos = xPos + 18
#         wPos = wPos - 22
#         yPos = yPos + 24
#         hPos = hPos - 48