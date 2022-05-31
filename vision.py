import cv2 as cv
import numpy as np


class Vision:
    # Given a list of [x, y, w, h] rectangles returned by find(), convert those into a list of
    # [x, y] positions in the center of those rectangles where we can click on those found items
    def get_click_points(self, rectangles):
        points = []

        # Loop over all the rectangles
        for (x, y, w, h) in rectangles:
            # Determine the center position
            center_x = x + int(w / 2)
            center_y = y + int(h / 2)
            # Save the points
            points.append((center_x, center_y))

        return points

    # Given a list of [x, y, w, h] rectangles and a canvas image to draw on, return an image with
    # all of those rectangles drawn.
    def draw_rectangles(self, img, rectangles, color = None):
        # These colors are actually BGR.
        line_color = color if color else (0, 255, 0)
        line_type = cv.LINE_4

        for (x, y, w, h) in rectangles:
            # Determines the box positions.
            top_left = (x, y)
            bottom_right = (x + w, y + h)
            # Draws the box.
            cv.rectangle(img, top_left, bottom_right, line_color, lineType=line_type)

        return img

    # given a list of [x, y] positions and a canvas image to draw on, return an image with all
    # of those click points drawn on as a crosshair.
    def draw_crosshairs(self, img, points):
        # these colors are actually BGR
        marker_color = (255, 0, 255)
        marker_type = cv.MARKER_CROSS

        for (center_x, center_y) in points:
            # draw the center point
            cv.drawMarker(img, (center_x, center_y), marker_color, marker_type)

        return img

    def centeroid(self, point_list):
        point_list = np.asarray(point_list, dtype=np.int32)
        length = point_list.shape[0]
        sum_x = np.sum(point_list[:, 0])
        sum_y = np.sum(point_list[:, 1])
        return [np.floor_divide(sum_x, length), np.floor_divide(sum_y, length)]
