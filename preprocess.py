import cv2
import numpy as np

def reorder_points(pts):
    pts = pts.reshape((4, 2))
    new_pts = np.zeros((4, 1, 2), dtype=np.int32)

    add = pts.sum(1)
    new_pts[0] = pts[np.argmin(add)]
    new_pts[3] = pts[np.argmax(add)]

    diff = np.diff(pts, axis=1)
    new_pts[1] = pts[np.argmin(diff)]
    new_pts[2] = pts[np.argmax(diff)]

    return new_pts


def get_warp(image, pts, w=700, h=1000):
    pts = reorder_points(pts)

    pts1 = np.float32(pts)
    pts2 = np.float32([[0,0],[w,0],[0,h],[w,h]])

    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    return cv2.warpPerspective(image, matrix, (w,h))


def preprocess(image_path):
    image = cv2.imread(image_path)

    if image is None:
        raise Exception("Image not found")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    gray = clahe.apply(gray)

    blur = cv2.GaussianBlur(gray, (5,5), 0)

    thresh = cv2.adaptiveThreshold(
        blur,
        255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY_INV,
        31,
        7
    )

    return gray, thresh