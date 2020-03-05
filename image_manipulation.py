#!/usr/bin/python3

import numpy as np
import cv2


def elaborate_image(image_name, blackThreshold, whiteThreshold, canny_min, canny_max):
    image = cv2.imread(image_name)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(image, 3)
    edged = cv2.Canny(gray, canny_min, canny_max)


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
                            output[yPos + y, xPos + x] = [0,0,0] #black

            if brightness < blackThreshold:
                image[yPos, xPos] = [0,0,0] #black
            elif brightness < whiteThreshold:
                image[yPos, xPos] = [81,81,81] #gray
            else:
                image[yPos, xPos] = [255,255,255] #white


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

        for xPos in range(0, imageWidth, step):
            begin = False
            for yPos in range(imageHeight):
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

        for yPos in range(0, imageHeight, step):
            begin = False
            for xPos in range(imageWidth):
                r1,g1,b1 = image[yPos, xPos]
                r2,b2,g2 = target_color
                if r1 == r2 and b1 == b2 and g1 == g2:
                    if not begin:
                        gcode += move(xPos, yPos, True)
                        gcode += penDown()
                    elif xPos == imageWidth + 1:
                        gcode += move(xPos, yPos)
                        gcode += penUp()

                    begin = True
                    output[yPos, xPos] = [0,0,0]
                elif begin:
                    gcode += move(xPos, yPos)
                    gcode += penUp()
                    begin = False

        return gcode

    gcode = ''

    for c in contours:
        x, y = c[0][0]
        gcode += move(x, y, True)
        gcode += penDown()

        for i in range(1, len(c)):
            x, y = c[i][0]
            gcode += move(x, y)

        gcode += penUp()


    gcode += hatch(image, output, [0,0,0], 2)
    gcode += hatch(image, output, [81,81,81], 6)


    return output, gcode
