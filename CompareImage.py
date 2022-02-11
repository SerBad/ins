# -*- coding: utf-8 -*-
from PIL import Image
from PIL import ImageChops
import time
import os
import argparse


def compare_images(path_one, path_two):
    """
    比较图片
    :param path_one: 第一张图片的路径
    :param path_two: 第二张图片的路径
    :return: 相同返回 success
    """
    if not os.path.exists(path_one) or not os.path.exists(path_two):
        return False

    image_one = Image.open(path_one)
    image_two = Image.open(path_two)
    try:
        diff = ImageChops.difference(image_one, image_two)

        if diff.getbbox() is None:
            # 图片间没有任何不同则直接退出
            return True
        else:
            # return "ERROR: 匹配失败！"
            return False

    except ValueError as e:
        # return "{0}\n{1}".format(e, "图片大小和box对应的宽度不一致!")
        return False


class CompareImageOptions:
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


# python3 CompareImage.py --path=./images
if __name__ == '__main__':
    opt = CompareImageOptions().parse()
    print('start compare image', opt)
    path = opt.path
    flist = os.listdir(path)

    for index1 in range(0, len(flist)):
        image1 = path + os.sep + flist[index1]
        for index2 in range(index1 + 1, len(flist)):
            image2 = path + os.sep + flist[index2]
            result = compare_images(image1, image2)
            if result:
                print("删除的文件", image2)
                os.remove(image2)