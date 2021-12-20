import cv2
import os
import numpy as np
import imutils

def read_file(filename):
  img = cv2.imread(filename)
  return img


def processFile3(filen, rename, rename_res):
  img = read_file(filen)
  if img is not None:
   if (img.shape[0]>200):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (3,3), 1)

    edge = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 43, 16)
    cartoon = cv2.bitwise_and(img, img, mask=edge) 


    res = imutils.resize(cartoon, width=400)
    cv2.imwrite(rename, cartoon)
    cv2.imwrite(rename_res, res)


for url in os.listdir('c:/fashion'):
#url='cn7629899.jpg'
  print (url)
  if (url!='out' and '.zip' not in url):
    processFile3('c:/fashion/'+url,'c:/fashion/out/'+url,'c:/fashion/out_res/'+url)
  #break
