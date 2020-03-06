#!/usr/bin/python3

import numpy as np
import cv2
import math


def elaborate_image(image_name, blackThreshold, whiteThreshold, canny_min, canny_max, black_steps=2, gray_steps=6):
    white = [255,255,255]
    black = [0,0,0]
    gray = [81,81,81]


    image = cv2.imread(image_name)
    gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray_img = cv2.medianBlur(image, 3)
    edged = cv2.Canny(gray_img, canny_min, canny_max)


    ret, labels = cv2.connectedComponents(edged)
    contours, hierarchy = cv2.findContours(edged, cv2.RETR_EXTERNAL , cv2.CHAIN_APPROX_TC89_L1)

    imageWidth = image.shape[1]
    imageHeight = image.shape[0]

    xPos, yPos = 0, 0

    output = np.full((imageHeight, imageWidth, 3), 255, dtype=np.uint8)

    for xPos in range(imageWidth):
        for yPos in range(imageHeight):
            R,G,B = image[yPos, xPos]
            brightness = sum([R,G,B])/3

            if labels[yPos, xPos] != 0:
                for x in range(-1, 1):
                    for y in range(-1, 1):
                        if xPos + x in range(0, imageWidth) and yPos + y in range(0, imageHeight):
                            output[yPos + y, xPos + x] = black

            if brightness < blackThreshold:
                image[yPos, xPos] = black
            elif brightness < whiteThreshold:
                image[yPos, xPos] = gray
            else:
                image[yPos, xPos] = white


    def penDown():
        return 'M03\n'

    def penUp():
        return 'M05\n'

    def move(x, y, fast=False):
        x_max = 150
        y_max = imageHeight / imageWidth * x_max

        ratio_x = x_max / imageWidth
        ratio_y = y_max / imageHeight

        x = x * ratio_x
        y = y * ratio_y

        #to avoid mirroring
        y = y * -1 + y_max

        cmd = 'G1'
        if fast:
            cmd = 'G0'

        return '{} X{} Y{}\n'.format(cmd, x, y)

    def hatch(image, output, target_color, step):
        gcode = ''

        xArray = [(xPos, 0) for xPos in range(0, imageWidth, step)]
        yArray = [(0, yPos) for yPos in range(0, imageHeight, step)]

        for xPos, yPos in xArray + yArray:
            begin = False
            while xPos < imageWidth and yPos < imageHeight:
                r1,g1,b1 = image[yPos, xPos]
                r2,b2,g2 = target_color
                if r1 == r2 and b1 == b2 and g1 == g2:
                    if not begin:
                        gcode += move(xPos, yPos, True)
                        gcode += penDown()
                    elif yPos == imageHeight + 1:
                        gcode += move(xPos, yPos)
                        gcode += penUp()

                    begin = True
                    output[yPos, xPos] = [0,0,0]
                elif begin:
                    gcode += move(xPos, yPos)
                    gcode += penUp()
                    begin = False

                xPos = min(xPos + 1, imageWidth)
                yPos = min(yPos + 1, imageHeight)

        return gcode

    gcode = ''

    contours_start = sorted(contours, key=lambda x: (x[0][0][0], x[0][0][1]))

    contours_new = []

    contours_new.append(contours_start[0])
    del contours_start[0]
    while len(contours_start) > 0:
        cont = contours_new[-1]

        min_elem = min(contours_start,
            key=lambda x: math.sqrt((cont[-1][0][0] - x[0][0][0])**2 + (cont[-1][0][1] - x[0][0][1])**2))

        cont_idx = [np.array_equal(min_elem, x) for x in contours_start].index(True)

        contours_new.append(min_elem)
        del contours_start[cont_idx]

    for c in contours_new:
        x, y = c[0][0]
        gcode += move(x, y, True)
        gcode += penDown()

        for i in range(1, len(c)):
            x, y = c[i][0]
            gcode += move(x, y)

        gcode += penUp()


    gcode += hatch(image, output, black, black_steps)
    gcode += hatch(image, output, gray, gray_steps)


    return output, gcode
