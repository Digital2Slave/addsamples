# -*- encoding:utf-8 -*-

import os
import cv2
import sys
import logging
from PIL import Image
from noisy import noisy

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
logger.setLevel(logging.INFO)

## remove file_log
logger.removeHandler(file_handler)



def add_noise(noise_type, save_prefix, img_prefix, image):
    """
    Add noise of noise_type to image.
    :param noise_type: the type of noise
    :param save_prefix: the prefix of save path
    :param img_prefix: the prefix of image name
    :param image: the cv type of image
    :return:
    """
    noise_img = noisy(noise_type, image)
    save_path = os.path.join(save_prefix, img_prefix + noise_type + ".jpg")
    cv2.imwrite(save_path, noise_img)


def preprocess_img(img_path, dst_sub_path, pfix):
    if not os.path.isfile(img_path):
        print("The input path for image file is invalid.")
        return
    if not os.path.isdir(dst_sub_path):
        print("The output path is invalid")
        return

    # Rotate
    im = Image.open(img_path)
    rotates = range(0, 271, 90)
    for idx, v in enumerate(rotates):
        img_prefix = str(pfix + idx)
        dst_im = im.rotate(v, 0, 1)
        dst_file_path = os.path.join(dst_sub_path, img_prefix + "rotate.jpg")
        dst_im.save(dst_file_path)
        # Add noise
        cvimg = cv2.imread(dst_file_path)
        add_noise("gauss", dst_sub_path, img_prefix, cvimg)
        add_noise("poisson", dst_sub_path, img_prefix, cvimg)
        # add_noise("s&p", dst_sub_path, img_prefix, cvimg)
        # add_noise("speckle", dst_sub_path, img_prefix, cvimg)
    return pfix + len(rotates) + 4


def main(src_path, dst_path):
    """
    main entry
    """
    if not os.path.isdir(src_path):
        print("The input path is invalid.")
        return
    if not os.path.isdir(dst_path):
        print("The output path is invalid.")
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

    logger.info(src_subfolders)
    logger.info(dst_subfolders)

    src_len = len(src_subfolders)
    dst_len = len(dst_subfolders)
    img_postfix = ['jpg', 'png', 'jpeg']
    if (src_len != 0) and (src_len == dst_len):
        for idn in range(src_len):
            src_sub = src_subfolders[idn]
            dst_sub = dst_subfolders[idn]
            pfix = 0
            for img in os.listdir(src_sub):
                if img[-3:] in img_postfix:
                    img_abs_path = os.path.join(src_sub, img)
                    pfix = preprocess_img(img_abs_path, dst_sub, pfix)
            logger.info('-' * 80)
            logger.info(src_sub.split("\\")[-1] + "\tDone!")
            # break


if __name__ == '__main__':
    src_data_path = os.path.join(os.getcwd(), "images")
    dst_data_path = os.path.join(os.getcwd(), "samples")
    main(src_data_path, dst_data_path)
