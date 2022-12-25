import os
import cv2
import pytesseract
from pytesseract import Output
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import re
import preprocess
# from pdf2image import convert_from_path
import json

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

patt = '[^a-zA-Z0-9]+'

# pdf = r"Sanskrit_Text.pdf"
# pages = convert_from_path(pdf, 300)

# pg_num = 1
# for page in pages:
#     img_name = "Page_" + str(pg_num) + ".jpg"
#     page.save(img_name, "JPEG")
#     pg_num += 1


def lineup(boxes):
    linebox = None
    for _, box in boxes.iterrows():
        if linebox is None: linebox = box           # first line begins
        elif box.top <= linebox.top+linebox.height: # box in same line
            linebox.top = min(linebox.top, box.top)
            linebox.width = box.left+box.width-linebox.left
            linebox.heigth = max(linebox.top+linebox.height, box.top+box.height)-linebox.top
            linebox.text += ' '+box.text
        else:                                       # box in new line
            yield linebox
            linebox = box                           # new line begins
    yield linebox                                   # return last line
    
def plot_boxes(boxes, j):
    boxes_dict = {}
    i = 0
    for index, b in boxes.iterrows():
        if re.match(patt, b.text):
            i += 1
            (x,y,w,h) = b['left'],b['top'],b['width'],b['height']
            boxes_dict[f"box{i}"] = {"top-left": [x,y],
                                     "top-right": [x+w,y],
                                     "bottom-left": [x,y+h],
                                     "bottom-right": [x+w,y+h],}
            print((x,y,w,h), b['text'])
            result = cv2.rectangle(img, (x,y), (w+x,h+y), (0, 255, 0), 1)
    cv2.imwrite(f'p{j}.jpg', result)
    # cv2.imshow('result', result)
    # cv2.waitKey(0)
    return boxes_dict

for j in range(1,6):
    img = cv2.imread(f'Images\Page_{j}.png')

    img = preprocess.get_grayscale(img)
    # alpha = 0.5 # Contrast control (1.0-3.0)
    # beta = 0 # Brightness control (0-100)
    # img = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)


    boxes = pytesseract.image_to_data(img, lang="san", output_type=Output.DICT)
    boxes = pd.DataFrame(boxes)
    boxes['text'].replace('', np.nan, inplace=True)
    boxes = boxes.dropna(subset=['text'])

    # string = pytesseract.image_to_string(img, lang="eng+san")
    # print(string)

    lineboxes = pd.DataFrame.from_records(lineup(boxes))
    res_dict = plot_boxes(lineboxes, j)
    with open(f'result{j}.json', 'w') as fp:
        json.dump(res_dict, fp)
# plot_boxes(boxes)