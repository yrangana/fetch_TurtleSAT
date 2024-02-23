import glob
import keras_ocr
import cv2
import math
import numpy as np
import os
import tqdm


def midpoint(x1, y1, x2, y2):
    x_mid = int((x1 + x2) / 2)
    y_mid = int((y1 + y2) / 2)
    return (x_mid, y_mid)


def inpaint_text(img_path, pipeline, radius=7, method=cv2.INPAINT_TELEA):
    # read image
    img = keras_ocr.tools.read(img_path)
    image = cv2.imread(img_path)
    # generate (word, box) tuples
    prediction_groups = pipeline.recognize([img])
    mask = np.zeros(img.shape[:2], dtype="uint8")
    for box in prediction_groups[0]:
        x0, y0 = box[1][0]
        x1, y1 = box[1][1]
        x2, y2 = box[1][2]
        x3, y3 = box[1][3]

        x_mid0, y_mid0 = midpoint(x1, y1, x2, y2)
        x_mid1, y_mi1 = midpoint(x0, y0, x3, y3)

        thickness = int(math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2))

        cv2.line(mask, (x_mid0, y_mid0), (x_mid1, y_mi1), 255, thickness)
        # img = cv2.inpaint(img, mask, 7, cv2.INPAINT_NS)
        img = cv2.inpaint(image, mask, radius, method)

    return img


def removeWatermark(img_path, pipeline, radius, method):
    return inpaint_text(img_path, pipeline, radius, method)


if __name__ == "__main__":

    folder_dir = "images"

    pipeline = keras_ocr.pipeline.Pipeline()

    radius = 5

    method = cv2.INPAINT_TELEA  # cv2.INPAINT_NS

    os.makedirs("./watermarkRemovedImages", exist_ok=True)
    
    # count the number of images in the folder and subfolders
    
    total = 0
    for images in glob.iglob(f"{folder_dir}/*/*", recursive=True):
        if images.endswith(".png"):
            total += 1

    for images in tqdm.tqdm(list(glob.iglob(f"{folder_dir}/*/*", recursive=True)),total=total, desc="Removing Watermark"):
        if images.endswith(".png"):

            parent_folder = os.path.basename(os.path.dirname(images))
            file = os.path.basename(images)

            filename = f"watermarkRemovedImages/{parent_folder}/{file}"
            
            os.makedirs(f"./watermarkRemovedImages/{parent_folder}", exist_ok=True)

            img = removeWatermark(images, pipeline, radius, method)

            if(not cv2.imwrite(filename, img)):
                print(f"Error writing file: {filename}")
                break
                
                
