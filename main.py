# -*- encoding:utf-8 -*-

import os
from PIL import Image


def preprocess_img(img_path, dst_sub_path, pfix):
    if not os.path.isfile(img_path):
        print("The input path for image file is invalid.")
        return
    if not os.path.isdir(dst_sub_path):
        print("The output path is invalid")
        return
    im = Image.open(img_path)
    rotates = range(0, 361, 15)
    for idx, v in enumerate(rotates):
        dst_im = im.rotate(v, 0, 1)
        dst_file_path = os.path.join(dst_sub_path, str(pfix + idx) + ".jpg")
        dst_im.save(dst_file_path)
    return pfix + len(rotates)


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
    print src_subfolders
    print dst_subfolders
    print '-' * 80
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
            print('-' * 80)
            print(src_sub.split("\\")[-1] + "Done!")


if __name__ == '__main__':
    src_data_path = os.path.join(os.getcwd(), "images")
    dst_data_path = os.path.join(os.getcwd(), "samples")
    main(src_data_path, dst_data_path)