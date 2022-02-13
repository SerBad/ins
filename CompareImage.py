# -*- coding: utf-8 -*-
from PIL import Image
from PIL import ImageChops
import time
import os
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed, ProcessPoolExecutor

Image.LOAD_TRUNCATED_IMAGES = True


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
    except Exception as e:
        print(path_one, path_two, e)
        return False
    except:
        return False

    return False


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


# python3 CompareImage.py --path=./images
if __name__ == '__main__':
    opt = ImageOptions().parse()
    print('开始比较图片', opt)
    tt = time.time()
    path = opt.path
    flist = os.listdir(path)
    executor = ProcessPoolExecutor(max_workers=8)
    for index1 in range(0, len(flist)):
        image1 = path + os.sep + flist[index1]
        for index2 in range(index1 + 1, len(flist)):
            image2 = path + os.sep + flist[index2]
            futures = []
            task = executor.submit(compare_images, image1, image2)
            futures.append(task)

            for future in as_completed(futures):
                if future.result():
                    print("删除的文件", image2)
                    os.remove(image2)

    print('比较结束:', time.time() - tt)
