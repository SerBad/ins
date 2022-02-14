# -*- coding: utf-8 -*-
import face_recognition
from PIL import Image
from PIL import ImageChops
import time
import os
import shutil
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed, ProcessPoolExecutor
import numpy as np
import pandas


def face(imagePath: str, faceRoot: str, bodyRoot: str):
    image = face_recognition.load_image_file(imagePath)
    face_locations = face_recognition.face_locations(image)
    base_name = os.path.basename(imagePath)
    if len(face_locations) == 0:
        print(imagePath, "没有脸")
        shutil.copyfile(imagePath, os.path.join(bodyRoot, base_name))
        return 1, [base_name, []]
    else:
        for face_location in face_locations:
            # Print the location of each face in this image
            top, right, bottom, left = face_location
            print(imagePath, bottom - top, right - left, "height:", image.shape[0], "width:", image.shape[1])

            if (bottom - top * 1.0) / image.shape[0] >= 0.4 and (right - left * 1.0) / image.shape[1] >= 0.4:
                shutil.copyfile(imagePath, os.path.join(faceRoot, base_name))
                return 2, [base_name, [top, right, bottom, left]]
            else:
                shutil.copyfile(imagePath, os.path.join(bodyRoot, base_name))
                return 1, [base_name, [top, right, bottom, left]]


class ImageOptions:
    def __init__(self):
        self.parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        self.initialized = False

    def initialize(self):
        self.parser.add_argument('--path', type=str, required=True, default='results', help='image file path')
        self.initialized = True

    def parse(self):
        if not self.initialized:
            self.initialize()
        self.opt = self.parser.parse_args()

        return self.opt


if __name__ == '__main__':
    opt = ImageOptions().parse()
    print('start classification image', opt)
    tt = time.time()
    path = opt.path
    flist = os.listdir(path)
    faceRoot = path + "Face"
    bodyRoot = path + "Body"
    if not os.path.exists(faceRoot):
        os.makedirs(faceRoot)

    if not os.path.exists(bodyRoot):
        os.makedirs(bodyRoot)

    executor = ProcessPoolExecutor(max_workers=8)
    columns1 = ["image", "face"]
    resultFaceData = []
    resultBodyData = []
    futures = []

    for index1 in range(0, len(flist)):
        image = path + os.sep + flist[index1]
        # face(image, faceRoot, bodyRoot)

        task = executor.submit(face, image, faceRoot, bodyRoot)
        futures.append(task)

    for future in as_completed(futures):
        is_face, face = future.result()
        if is_face == 1:
            resultBodyData.append(face)
        elif is_face == 2:
            resultFaceData.append(face)
        futures.remove(future)

        if len(futures) == 0:
            resultFace = pandas.ExcelWriter(faceRoot + os.sep + "tags.xlsx")
            resultBody = pandas.ExcelWriter(bodyRoot + os.sep + "tags.xlsx")
            pandas.DataFrame(resultFaceData, columns=columns1).to_excel(resultFace, index=False)
            resultFace.save()
            pandas.DataFrame(resultBodyData, columns=columns1).to_excel(resultBody, index=False)
            resultBody.save()

    print('time2 end:', time.time() - tt)
