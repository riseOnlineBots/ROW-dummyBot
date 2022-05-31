# import os
import os
from time import time

import cv2
import pytesseract

from bot import RiseOnlineBot, BotState
from detection import Detection
from objectDetection import ObjectDetection
from vision import Vision
from windowcapture import WindowCapture

DEBUG = True

# Initializes the path for the tesseract cmd.
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Changes the directory portion.
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Initializes WindowCapture object.
window_capture = WindowCapture(None)

# Loads the detector.
detector = Detection('cascade/cascade.xml')

# Loads an empty vision class.
vision_object = Vision()

# Initializes the object detection
object_detection = ObjectDetection()

# Initializes the bot object.
bot = RiseOnlineBot((window_capture.offset_x, window_capture.offset_y), (window_capture.w, window_capture.h))

window_capture.start()
# detector.start()
# bot.start()

loop_time = time()

while True:
    # Check if there is a screenshot. If not, it won't run the code.
    if window_capture.screenshot is None:
        continue

    # screenshot = np.array(ImageGrab.grab(bbox=(0, 40, 1366, 768)))
    # screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)

    # # Gives the detector the current screenshot to search for objects in.
    detector.update(window_capture.screenshot)

    # Update the bot with the data it needs right now.
    if bot.state == BotState.INITIALIZING:
        # While bot is waiting to start, go ahead and start giving it some targets to work
        # on right away when it does start
        targets = vision_object.get_click_points(detector.rectangles)
        bot.update_targets(targets)
    elif bot.state == BotState.SEARCHING:
        # When searching for something to click on next, the bot needs to know what the click
        # points are for the current detection results. It also needs an updated screenshot
        # to verify the hover tooltip once it has moved the mouse to that position.
        targets = vision_object.get_click_points(detector.rectangles)
        bot.update_targets(targets)
        bot.update_screenshot(window_capture.screenshot)
    elif bot.state == BotState.MOVING:
        # When moving, we need fresh screenshots to determine when we've stopped moving.
        bot.update_screenshot(window_capture.screenshot)
    elif bot.state == BotState.MINING:
        # Nothing is needed while we wait for the mining to finish.
        pass

    if DEBUG:
        # Draws the detection results onto the original image.
        # detection_image = vision_object.draw_rectangles(window_capture.screenshot, detector.rectangles)
        rectangles = (0, 0, 0, 0)
        if object_detection.character_hp_mp_bar_set:
            rectangles = object_detection.character_hp_mp_bar
        else:
            rectangles = object_detection.find_character_info(window_capture.screenshot)
            object_detection.set_character_hp_mp_bar(rectangles)

        positions = vision_object.get_click_points(rectangles)
        x, y, w, h = rectangles[0]
        x = x + 30
        w = w - 130
        h = h - 1
        info = window_capture.screenshot[y:y + h, x:x + w]
        info = cv2.cvtColor(info, cv2.COLOR_BGR2GRAY)

        scale_percent = 250
        width = int(w * scale_percent / 100)
        height = int(h * scale_percent / 100)
        dim = (width, height)
        info = cv2.resize(info, dim, interpolation=cv2.INTER_AREA)

        cv2.imshow('bar', info)
        config = r'--oem 3 --psm 4 -c tessedit_char_whitelist=0123456789/'
        text = pytesseract.image_to_string(info, config=config) \
            .replace('\n', ',')

        print(text)
        print('------')

        # detection_image = vision_object.draw_rectangles(window_capture.screenshot, rectangles, (155, 155, 155))

        # Displays the image.
        # cv2.imshow('Matches', window_capture.screenshot)

    loop_time = time()
    key = cv2.waitKey(1) & 0xFF  # Waits 1ms every loop to process key presses.

    if key == ord('z'):
        window_capture.stop()
        detector.stop()
        bot.stop()
        cv2.destroyAllWindows()
        break
    elif key == ord('f'):
        cv2.imwrite('copperMines/positive/{}.jpg'.format(loop_time), window_capture.screenshot)
        print('Screenshot taken.')
    elif key == ord('d'):
        cv2.imwrite('copperMines/negative/{}.jpg'.format(loop_time), window_capture.screenshot)
        print('Screenshot taken.')

print('Peacefully closing the app.')
