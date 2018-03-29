# -*- encoding:utf-8 -*-

import os
import cv2
import sys
import logging
import numpy as np
from PIL import Image, ImageEnhance
from noisy import noisy
from copy import deepcopy

# log
## log instance
logger = logging.getLogger("AddSamples")
formatter = logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s')

## file_log
file_handler = logging.FileHandler("addsamples.log")
file_handler.setFormatter(formatter)

## console_log
console_hander = logging.StreamHandler(sys.stdout)
console_hander.formatter = formatter

logger.addHandler(file_handler)
logger.addHandler(console_hander)

## set log level default WARN
logger.setLevel(logging.DEBUG)

## remove file_log
logger.removeHandler(file_handler)


def cropit(img_src_path, img_dst_path):
    """
    Crop image from src_img_path, and save it to dst_img_path.
    :param img_src_path: the path of input image
    :param img_dst_path: the path of output image
    :return: None
    """
    pil_image = Image.open(img_src_path).convert('RGB')
    src = np.array(pil_image)
    src = src[:, :, ::-1].copy()
    # src = cv2.imread(img_src_path)
    img_info = np.shape(src)
    gray = deepcopy(src)
    if len(img_info) == 3:
        cv2.cvtColor(src, cv2.COLOR_BGR2GRAY, gray)
    gray = cv2.GaussianBlur(gray, (3,3), 0)
    edges = cv2.Canny(gray, 30, 90, None, 3, False)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    mask = cv2.dilate(edges, kernel)
    contours, hierarchy = cv2.findContours(mask, 0, 2)

    max_cnt = contours[0]
    max_area = 0
    for cnt in contours:
        tmp_area = cv2.contourArea(cnt)
        if tmp_area >= max_area:
            max_area = tmp_area
            max_cnt = cnt
    if len(max_cnt):
        x,y,w,h = cv2.boundingRect(max_cnt)
        dst = src[y:y+h, x:x+w]
        cv2.imwrite(img_dst_path, dst)
    else:
        cv2.imwrite(img_dst_path, src)


def add_noise(noise_type, img_dst_dir, img_prefix, image):
    """
    Add noise of noise_type to image.
    :param noise_type: the type of noise
    :param img_dst_dir: the prefix of save path
    :param img_prefix: the prefix of image name
    :param image: the cv type of image
    :return:
    """
    noise_img = noisy(noise_type, image)
    save_path = os.path.join(img_dst_dir, img_prefix + "_noise_" + noise_type + ".jpg")
    cv2.imwrite(save_path, noise_img)


def adjust_brightness(img_src_path, img_dst_dir, img_prefix):
    """
    Adjust brightness of input image.
    :param img_src_path: the path of input image
    :param img_dst_dir: the root path of output image directory
    :param img_prefix: the prefix name of input image
    :return:
    """
    im = Image.open(img_src_path)
    enhancer = ImageEnhance.Brightness(im)
    for i in range(2, 8, 2):
        factor = i / 4.0
        dst = enhancer.enhance(factor)
        if factor != 1.0:
            save_path = os.path.join(img_dst_dir, img_prefix + "_brightenss_" + str(factor) + ".jpg")
        dst.save(save_path)


def preprocess_img(img_src_path, img_dst_dir, img_prefix):
    """
    Preprocess the input image file.
    :param img_src_path: the path of input image
    :param img_dst_dir: the root path of output image directory
    :param img_prefix: the prefix name of input image
    :return:
    """
    if not os.path.isfile(img_src_path):
        logger.error("The input path for image file is invalid.")
        return

    img_dst_path = os.path.join(img_dst_dir, img_prefix + ".jpg")    
    # 0-Crop if need
    # cropit(img_src_path, img_dst_path)

    pil_image = Image.open(img_src_path).convert('RGB')
    src = np.array(pil_image)
    src = src[:, :, ::-1].copy()
    src_rows, src_cols = np.shape(src)[:2]
    if src_rows > src_cols:
        src = cv2.transpose(src)
        src = cv2.flip(src, 1)
        cv2.imwrite(img_src_path, src)

    # Adjust_brightness
    adjust_brightness(img_src_path, img_dst_dir, img_prefix)

    # 1-Rotate
    im = Image.open(img_src_path)
    rotates = range(0, 271, 180) # 90
    for idx, v in enumerate(rotates):
        dst_im = im.rotate(v, 0, 1)
        img_pfix = img_prefix + "_rotate_" + str(v)
        dst_file_path = os.path.join(img_dst_dir, img_pfix + ".jpg")
        dst_im.save(dst_file_path)
        # 2-Add Noise
        cvimg = cv2.imread(dst_file_path)
        add_noise("gauss", img_dst_dir, img_pfix, cvimg)
        add_noise("s&p", img_dst_dir, img_pfix, cvimg)


def main(src_path, dst_path):
    """
    main entry
    :param src_path: the root folder of images from src_path
    :param dst_path: the dst folder of images to dst_path
    :return: None
    """

    if not os.path.isdir(src_path):
        logger.error("The input path is invalid.")
        return
    if not os.path.isdir(dst_path):
        logger.error("The output path is invalid.")
        return

    src_subfolders = []
    dst_subfolders = []
    for sub in os.listdir(src_path):
        src_sub = os.path.join(src_path, sub)
        dst_sub = os.path.join(dst_path, sub)
        if os.path.exists(src_sub) and os.path.isdir(src_sub):
            src_subfolders.append(src_sub)
        if os.path.exists(dst_sub) and os.path.isdir(dst_sub):
            dst_subfolders.append(dst_sub)
        else:
            if ".DS_Store" in dst_sub:
                continue
            os.mkdir(dst_sub)
            dst_subfolders.append(dst_sub)

    logger.debug(src_subfolders)
    logger.debug(dst_subfolders)

    src_len = len(src_subfolders)
    dst_len = len(dst_subfolders)
    img_postfix = ['jpg', 'png', 'jpeg']
    if (src_len != 0) and (src_len == dst_len):
        for idn in range(src_len):
            src_sub = src_subfolders[idn]
            dst_sub = dst_subfolders[idn]
            for img in os.listdir(src_sub):
                if img[-3:] in img_postfix:
                    img_prefix = img[:-4]
                    img_src_path = os.path.join(src_sub, img)
                    preprocess_img(img_src_path, dst_sub, img_prefix)
            logger.debug('-' * 80)
            logger.debug(src_sub.split("\\")[-1] + "\tDone!")
            # break


if __name__ == '__main__':
    src_data_path = os.path.join(os.getcwd(), "images")
    dst_data_path = os.path.join(os.getcwd(), "data")
    main(src_data_path, dst_data_path)
