import numpy as np
import cv2 as cv

def calc_bounding_rect(image, landmarks):
    image_width, image_height = image.shape[1], image.shape[0]
    landmark_array = np.array([[min(int(p.x * image_width), image_width - 1),
                                min(int(p.y * image_height), image_height - 1)]
                               for p in landmarks.landmark], dtype=int)
    x, y, w, h = cv.boundingRect(landmark_array)
    return [x, y, x + w, y + h]

def calc_landmark_list(image, landmarks):
    image_width, image_height = image.shape[1], image.shape[0]
    return [[min(int(p.x * image_width), image_width - 1),
             min(int(p.y * image_height), image_height - 1)]
            for p in landmarks.landmark]