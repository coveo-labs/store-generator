import cv2
import imutils
import os
import traceback
import json
import re
import sys
from os import walk

import numpy as np
import logging
import base64
import operator
from webcolors import (
    CSS3_NAMES_TO_HEX,
    hex_to_rgb,
)
from scipy.spatial import KDTree
from collections import Counter
import math
import glob

def checkIfBW(img):
    
  ### splitting b,g,r channels
  b,g,r=cv2.split(img)

  ### getting differences between (b,g), (r,g), (b,r) channel pixels
  r_g=np.count_nonzero(abs(r-g))
  r_b=np.count_nonzero(abs(r-b))
  g_b=np.count_nonzero(abs(g-b))

  ### sum of differences
  diff_sum=float(r_g+r_b+g_b)

  ### finding ratio of diff_sum with respect to size of image
  ratio=diff_sum/img.size
  print (ratio)
  if ratio>0.5:
      return False
      #image is color
  else:
      return True
      #image is bw

def createCopiesImages(photo, nr):
  #create Output folder
  path = '\\'.join(photo.split('\\')[0:-1])
  outputpath = path+'\\Output'
  original_file = outputpath+'\\image'+str(nr)
  #check if output folder exists
  if (not os.path.exists(outputpath)):
    os.makedirs(outputpath)
  #Make a copy of the photo
  theimage = cv2.imread(photo)
  theimage = imutils.resize(theimage, width=600)

  #imageIsBW = checkIfBW(theimage)

  rename = original_file+'.jpg'
  cv2.imwrite(rename, theimage)

  #Now create different copies
  #B/W
  # rename = original_file+'_bw.jpg'
  # if (not imageIsBW):
  #   bw = theimage.copy()
  #   bw = cv2.cvtColor(bw, cv2.COLOR_BGR2GRAY)
  #   cv2.imwrite(rename, bw)
  # else:
  #   #remove bw
  #   pass

  #Flipped Original
  rename = original_file+'_rot.jpg'
  rot = theimage.copy()
  rot = cv2.flip(rot,1)
  cv2.imwrite(rename, rot)
  #B/W Flipped
  # rename = original_file+'_bwrot.jpg'
  # if (not imageIsBW):
  #   bw = theimage.copy()
  #   bw = cv2.cvtColor(bw, cv2.COLOR_BGR2GRAY)
  #   bw = cv2.flip(bw,1)
  #   cv2.imwrite(rename, bw)
  # else:
  #   #remove bw
  #   pass
  #Zoomed 20%
  rename = original_file+'_zoom.jpg'
  zoom = theimage.copy()
  h,w,_ = zoom.shape
  y=int(h/8)
  x=int(w/8)
  h = int(h)#-x)
  w = int(w)#-y)
  zoom = zoom[y:h, x:w]
  cv2.imwrite(rename, zoom)
  #Zoomed flipped
  rename = original_file+'_zoomrot.jpg'
  zoom = cv2.flip(zoom,1)
  cv2.imwrite(rename, zoom)

  #Zoomed 40%
  rename = original_file+'_zoom6.jpg'
  zoom = theimage.copy()
  h,w,_ = zoom.shape
  y=int((h/6)*1.5)
  x=int(w/6)
  h = int(h)#-x)
  w = int(w)#-y)
  zoom = zoom[y:h, x:w]
  cv2.imwrite(rename, zoom)
  #Zoomed flipped
  rename = original_file+'_zoomrot6.jpg'
  zoom = cv2.flip(zoom,1)
  cv2.imwrite(rename, zoom)



def change_brightness(img, value=30):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    v = cv2.add(v,value)
    v[v > 255] = 255
    v[v < 0] = 0
    final_hsv = cv2.merge((h, s, v))
    img = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
    return img

def process():
  #Get All files
  total=0
  #images = glob.glob('images\\*.jpg',recursive=True)
  path = 'images'
  my_files = []
  for (dirpath, dirnames, filenames) in walk(path):
    for file in filenames:
      my_files.append(os.path.join(dirpath, file))
  print ("Processing "+str(len(my_files)))
  #first remove all old images from output folders
  for image in my_files:
    if ('\\Output' in image):
      print(" Deleting Output folder images ")
      os.remove(image)
  for image in my_files:
    total = total+1
    #skip images in \output\ folder
    if ('\\Output' in image):
      print(" Skipping Output folder image ")
    else:
      print ("Processing image: "+image)
      createCopiesImages(image,total)
    

  print("We are done!\n")
  print("Processed: "+str(total)+" results\n")


try:
  process()
except Exception as e: 
  print(e)
  traceback.print_exception(*sys.exc_info())
  print ("Specify configuration json (like config.json) on startup")
