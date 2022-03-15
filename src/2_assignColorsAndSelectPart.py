import cv2
import imutils
import os
import traceback
import json
import re
import sys

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

currentFile=''
asIs = False
image_hsv = None   # global
image_normal = None   # global
image_option1 = None   # global
image_option2 = None   # global
image_option3 = None   # global
pixel = (20,60,80) # some stupid default
offset = 10
offsetZoom = 200
offsetHSV = 20
currentJson = {}

def loadConfiguration(filename):
  settings={}
  config={}
  try:
      with open(filename, "r",encoding='utf-8') as fh:
        text = fh.read()
        config = json.loads(text)
      with open("settings.json", "r",encoding='utf-8') as fh:
        text = fh.read()
        settings = json.loads(text)
  except:
    print ("Failure, could not load settings.json or config.json")
  return settings, config

def BGR2HEX(color):
    return "{:02x}{:02x}{:02x}".format(int(color[2]), int(color[1]), int(color[0]))


def removeNumbers(input):
  return input
  #r=re.compile(r'\d')
  #output = r.sub('', input)
  #return output


def getAllColors():
    css3_db = CSS3_NAMES_TO_HEX
    names = []
    rgb_values = []
    for color_name, color_hex in css3_db.items():
        names.append(color_name)
    return names

def rgbToColor(rgb_tuple):
    
    # a dictionary of all the hex and their respective names in css3
    css3_db = CSS3_NAMES_TO_HEX
    names = []
    rgb_values = []
    for color_name, color_hex in css3_db.items():
        names.append(color_name)
        #print (color_hex, color_name)
        rgb_values.append(hex_to_rgb(color_hex))
    
    kdt_db = KDTree(rgb_values)
    distance, index = kdt_db.query(rgb_tuple)
    return f'{names[index]}'


def updateJson(photo):
  photo = photo.replace('.jpg','.json')
  try:
       with open(photo, "w", encoding='utf-8') as handler:
        text = json.dumps(currentJson, ensure_ascii=True)
        handler.write(text)
  except:
    pass
  return 

def loadJson(photo):
  newrecord={}
  photo = photo.replace('.jpg','.json')
  try:
      with open(photo, "r",encoding='utf-8') as fh:
        text = fh.read()
        newrecord = json.loads(text)
  except:
    pass
  return newrecord

def clearJson(photo):
  photo = photo.replace('.jpg','.json')
  try:
      newrecord=loadJson(photo)
      newrecord['childs']=[]
      newrecord['man_color']=''
      newrecord['man_hexcolor']=''
      newrecord['images']=[]
      with open(photo, "w", encoding='utf-8') as handler:
        text = json.dumps(newrecord, ensure_ascii=True)
        handler.write(text)
  except:
    pass
  
def instructions():
  print(" n = next, p = previous,  q = quit, d=delete image, x=reset image,")
  print(" a = Switch between AsIs (no zoom) or based on Zoom")
  print(" + = offset color          - = offset color ")
  print(" u = incr (+) offset HSV   y = decr (-) offset HSV ")
  print(" ] = incr (+) offset ZOOM  [ = decr (-) offset ZOOM ")
  print("=====================================")

def pick_color(event,x,y,flags,param):
  global currentFile
  global image_normal
  global currentJson
  global image_hsv
  global offset
  if event == cv2.EVENT_LBUTTONDOWN:
        #print (image_hsv)
        pixel = image_normal[y,x]
        rec = image_normal[y:y+offset,x:x+offset]
        print('Pixel: ',pixel)
        print('Average color (BGR): ',cv2.mean(rec))
        #you might want to adjust the ranges(+-10, etc):

        #upper =  np.array([pixel[0] + 20, pixel[1] + 20, pixel[2] + 60])
        #lower =  np.array([pixel[0] - 20, pixel[1] - 20, pixel[2] - 20])
        #print(pixel)
        #bgr
        avgcolor = cv2.mean(rec)
        #bgr 0 1 2
        #rgb 2 1 0
        avg=[avgcolor[0],avgcolor[1],avgcolor[2]]
        #print (avg)
        hex = BGR2HEX(avg)
        #color= webcolors.rgb_to_name((int(pixel[1]),int(pixel[1]),int(pixel[0])), spec='css3')
        #print (color)
        rgb = (int(avgcolor[2]),int(avgcolor[1]),int(avgcolor[0]))
        name = (rgbToColor(rgb))
        
        currentJson['man_color']=name
        currentJson['man_hexcolor']=hex
        currentJson['colorxy']={}
        currentJson['colorxy']['x']=x 
        currentJson['colorxy']['y']=y
        #photo,rec, childnr, childimage, color,colorhex):
        #print ("current")
        #print (currentFile)
        rec, newimage = createCopiesImages(currentFile, currentJson, 0, image_normal,'','')
        image_hsv = cv2.cvtColor(newimage, cv2.COLOR_BGR2HSV)

        #updateJson(currentFile,rec,False)
        print("=====================================")
        print("File       : "+currentFile)
        print("Color      : "+name)
        print("HEX Color  : "+hex)
        print("Offset     : "+str(offset))
        print("Offset HSV : "+str(offsetHSV))
        #Update HSV window
        #if ('gray' in name or 'black' in name):
        #  print ('Gray or black not usefull for Grouping')
        #else:
        cv2.imshow('image_hsv',image_hsv)

        #instructions()
        #image_mask = cv2.inRange(image_hsv,lower,upper)
        #cv2.imshow("mask",image_mask)

def getColor(image, x,y):
    pixel = image[y,x]
    rec = image[y:y+offset,x:x+offset]
    #you might want to adjust the ranges(+-10, etc):
    avgcolor = cv2.mean(rec)
    avg=[avgcolor[0],avgcolor[1],avgcolor[2]]
    #print (avg)
    hex = BGR2HEX(avg)
    #color= webcolors.rgb_to_name((int(pixel[1]),int(pixel[1]),int(pixel[0])), spec='css3')
    #print (color)
    rgb = (int(avgcolor[2]),int(avgcolor[1]),int(avgcolor[0]))
    name = (rgbToColor(rgb))
    return hex,name

def getColorNoOffset(image, x,y):
    pixel = image[y,x]
    #rec = image[y:y+offset,x:x+offset]
    #you might want to adjust the ranges(+-10, etc):
    avgcolor = pixel
    avg=[avgcolor[0],avgcolor[1],avgcolor[2]]
    #print (avg)
    hex = BGR2HEX(avg)
    #color= webcolors.rgb_to_name((int(pixel[1]),int(pixel[1]),int(pixel[0])), spec='css3')
    #print (color)
    rgb = (int(avgcolor[2]),int(avgcolor[1]),int(avgcolor[0]))
    name = (rgbToColor(rgb))
    return hex,name

def pick_option1(event,x,y,flags,param):
  global currentFile
  global image_normal
  global image_hsv
  global image_option1
  global image_option2
  global image_option3
  global currentJson
  global offset
  if event == cv2.EVENT_LBUTTONDOWN:
      #saveTheImage
      print("Saving Option1")
      x = currentJson['colorxy']['x']
      y = currentJson['colorxy']['y']
      hex, color = getColorNoOffset(image_option1,x,y)
      print("=====================================")
      print("Color    : "+color)
      print("HEX Color: "+hex)

      rec={}
      #photo,rec, childnr, childimage, color,colorhex):
      rec, newimg = createCopiesImages(currentFile, currentJson, 1, image_option1, color,hex)
      #updateJson(currentFile,rec,False)


def pick_option2(event,x,y,flags,param):
  global currentFile
  global image_normal
  global image_hsv
  global image_option1
  global image_option2
  global image_option3
  global offset
  global currentJson
  if event == cv2.EVENT_LBUTTONDOWN:
      #saveTheImage
      print("Saving Option2")
      x = currentJson['colorxy']['x']
      y = currentJson['colorxy']['y']
      hex, color = getColorNoOffset(image_option2,x,y)
      print("Color    : "+color)
      print("HEX Color: "+hex)
      rec={}
      #photo,rec, childnr, childimage, color,colorhex):
      rec, newimg = createCopiesImages(currentFile, currentJson, 2, image_option2, color,hex)
      #updateJson(currentFile,rec,False)

def pick_option3(event,x,y,flags,param):
  global currentFile
  global image_normal
  global image_hsv
  global image_option1
  global image_option2
  global image_option3
  global offset
  global currentJson
  if event == cv2.EVENT_LBUTTONDOWN:
      #saveTheImage
      print("Saving Option3")
      x = currentJson['colorxy']['x']
      y = currentJson['colorxy']['y']
      hex, color = getColorNoOffset(image_option3,x,y)
      print("Color    : "+color)
      print("HEX Color: "+hex)
      rec={}
      #photo,rec, childnr, childimage, color,colorhex):
      rec, newimg = createCopiesImages(currentFile, currentJson, 3, image_option3, color,hex)
      #updateJson(currentFile,rec,False)


def pick_color_hsv(event,x,y,flags,param):
  global currentFile
  global image_normal
  global image_hsv
  global image_option1
  global image_option2
  global image_option3
  global offset
  global offsetHSV
  if event == cv2.EVENT_LBUTTONDOWN:
        #print (image_hsv)
        pixel = image_hsv[y,x]
        rec = image_hsv[y:y+offset,x:x+offset]
        print('Pixel (HSV): ',pixel)
        print('Average HSV: ',cv2.mean(rec))
        #you might want to adjust the ranges(+-10, etc):
        avgcolor = cv2.mean(rec)
        h = avgcolor[0]
        t = offsetHSV # tolerance value
        
        # create a binary mask for pen color
        min_hue = np.array([h - t])
        max_hue = np.array([h + t])

        image_option1 = image_hsv.copy()
        image_option2 = image_hsv.copy()
        image_option3 = image_hsv.copy()
        hue1 = image_option1[:,:,0]
        hue2 = image_option2[:,:,0]
        hue3 = image_option3[:,:,0]
        mask_hue1 = cv2.inRange(hue1, min_hue, max_hue)
        mask_hue2 = cv2.inRange(hue2, min_hue, max_hue)
        mask_hue3 = cv2.inRange(hue3, min_hue, max_hue)
        #cv2.imshow('mask1',mask_hue1)
        #cv2.imshow('mask2',mask_hue2)
        #cv2.imshow('mask3',mask_hue3)
        # modfiy hue values satisfying the condition
        hue1[mask_hue1 > 0] = hue1[mask_hue1 > 0] + (h/3)
        hue2[mask_hue2 > 0] = hue2[mask_hue2 > 0] + h
        hue3[mask_hue3 > 0] = hue3[mask_hue3 > 0] + (h*2)

        # assign the modified hue channel back to the hsv image
        image_option1[:,:,0] = hue1
        image_option2[:,:,0] = hue2
        image_option3[:,:,0] = hue3

        image_option1 = cv2.cvtColor(image_option1, cv2.COLOR_HSV2BGR)
        image_option2 = cv2.cvtColor(image_option2, cv2.COLOR_HSV2BGR)
        image_option3 = cv2.cvtColor(image_option3, cv2.COLOR_HSV2BGR)
        cv2.imshow('image_option1',image_option1)
        cv2.imshow('image_option2',image_option2)
        cv2.imshow('image_option3',image_option3)
        #x = currentJson['colorxy']['x']
        #y = currentJson['colorxy']['y']
        currentJson['colorxy']['x']=x
        currentJson['colorxy']['y']=y
        print ("Option1:")
        hex, color = getColor(image_option1,x,y)
        print (" Color    : "+color)
        print (" Color HEX: "+hex)
        print ("Option2:")
        hex, color = getColor(image_option2,x,y)
        print (" Color    : "+color)
        print (" Color HEX: "+hex)
        print ("Option3:")
        hex, color = getColor(image_option3,x,y)
        print (" Color    : "+color)
        print (" Color HEX: "+hex)
        print ("TO CONFIRM AN IMAGE GROUP, CLICK ON THE OPTION WINDOW")


        #instructions()
        #image_mask = cv2.inRange(image_hsv,lower,upper)
        #cv2.imshow("mask",image_mask)


def process(image):
    global image_hsv
    global image_normal
    global currentJson
    photo=image
    currentJson = loadJson(image)
    theimage = cv2.imread(photo)
    theimage = imutils.resize(theimage, width=800)
    image_normal = theimage
    image_hsv = cv2.cvtColor(theimage, cv2.COLOR_BGR2HSV)
    cv2.imshow('image_normal',image_normal)
    #return data
    #return image, newfile

def getMeta(data, field):
  if field in data:
    return data[field]
  else:
    return ''

def createCopiesImages(photo,rec, childnr, childimage, color,colorhex):
    global currentJson
    global offsetZoom
    global asIs
    childrec={}
    if 'childs' not in rec:
      rec['childs']=[]
    if childnr>0:
      childrec['color']=color
      childrec['colorhex']=colorhex
      childrec['images']=[]
    #Zoom image
    originalimage = childimage.copy()
    rename=''
    photo_number=0
    if childnr>0:
      #change brightness
      #First save the original
      originalimage = change_brightness(originalimage,-30)
      rename = photo.replace(".jpg","_"+str(childnr)+"_"+str(photo_number)+'.jpg')
      childrec['images'].append(rename)
      photo_number = photo_number+1
      cv2.imwrite(rename, originalimage)
      rename = photo.replace(".jpg","_"+str(childnr)+"_"+str(photo_number)+'.jpg')
      childrec['images'].append(rename)
    else:
      rename = photo.replace(".jpg","_"+str(photo_number)+'.jpg')
      #first one, initialize images again
      rec["images"]=[]
      rec["childs"]=[]
      #We do not want the original, we want to zoom one
      #rec["images"].append(photo)
      rec["images"].append(rename)
      h,w,_ = originalimage.shape
      y = rec['colorxy']['y']
      x = rec['colorxy']['x']
      x = x - offsetZoom
      y = y - offsetZoom
      height = y + (2*offsetZoom)
      width = x + (2*offsetZoom)
      if y<0:
        y=0
        height=(2*offsetZoom)
      if x<0:
        x=0
        width=(2*offsetZoom)

      if height>h:
        height=(2*offsetZoom)
        y= h-height
        height = y+height
        if y<0:
          y=0
          height = height
        #if (height-y)<(2*offsetZoom):
        #  y=0
        #  height=(2*offsetZoom)
      if width>w:
        width=(2*offsetZoom)
        x=w-width
        width = x+width
        if x<0:
          x=0
          width=width
        #if width-x<(2*offsetZoom):
        #  x=0
        #  width = 2*offsetZoom
      #if (height-y<400):
      #  y = y-(400-(height-y))
      #if (width-x<400):
      #  x = x-(400-(width-x))
      print ("x: "+str(x))
      print ("y: "+str(y))
      print ("H: "+str(h))
      print ("W: "+str(w))
      print ("Height: "+str(height))
      print ("Width: "+str(width))
      if (asIs):
        newimage2 = originalimage.copy()
        newimage2 = imutils.resize(newimage2, width=400)
      else:
        newimage2 = originalimage[y:height, x:width]
      cv2.imshow('Zoom',newimage2)
      originalimage = newimage2.copy()
      cv2.imwrite(rename, newimage2)
      photo_number = photo_number+1
      #rename = photo.replace(".jpg","_"+str(photo_number)+'.jpg')
      #rec['images'].append(rename)
    #print (originalimage)
    #print (originalimage.shape)
    # h,w,_ = originalimage.shape
    # y = rec['colorxy']['y']
    # y = y - 100
    # height = y + 200
    # if y<0:
    #   y=0
    # if height>h:
    #   height=h
    # newimage2 = originalimage[y:y+height, 0:w]
    # cv2.imshow('Zoom',newimage2)
    # print (rename)
    # cv2.imwrite(rename, newimage2)
    # photo_number = photo_number+1

    #flip image
    newimage = originalimage.copy()
    if childnr>0:
      rename = photo.replace(".jpg","_"+str(childnr)+"_"+str(photo_number)+'.jpg')
      childrec['images'].append(rename)
    else:
      rename = photo.replace(".jpg","_"+str(photo_number)+'.jpg')
      rec["images"].append(rename)
    newimage2 = cv2.flip(newimage,1)
    cv2.imwrite(rename, newimage2)
    photo_number = photo_number+1
    #b/w
    if childnr>0:
      rename = photo.replace(".jpg","_"+str(childnr)+"_"+str(photo_number)+'.jpg')
      childrec['images'].append(rename)
      rec['childs'].append(childrec)
    else:
      rename = photo.replace(".jpg","_"+str(photo_number)+'.jpg')
      rec["images"].append(rename)
    newimage2 = cv2.cvtColor(newimage, cv2.COLOR_BGR2GRAY)
    cv2.imwrite(rename, newimage2)
    photo_number = photo_number+1
    currentJson=rec
    updateJson(currentFile)
    return rec, originalimage

def next():
  #cv2.destroyWindow('image_normal')
  #cv2.destroyWindow('image_hsv')
  #cv2.destroyWindow('image_option1')
  #cv2.destroyWindow('image_option2')
  #cv2.destroyWindow('image_option3')
  return


def change_brightness(img, value=30):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    v = cv2.add(v,value)
    v[v > 255] = 255
    v[v < 0] = 0
    final_hsv = cv2.merge((h, s, v))
    img = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
    return img

def processImages(filename):
  #Get All files
  settings, config = loadConfiguration(filename)

  global offset
  global offsetHSV
  global currentFile
  global offsetZoom
  global asIs
  offset = config['global']['offsetColor']
  offsetHSV = config['global']['offsetHSV']
  total=0
  cv2.namedWindow('image_normal')
  cv2.setMouseCallback('image_normal', pick_color)
  cv2.namedWindow('image_hsv')
  cv2.setMouseCallback('image_hsv', pick_color_hsv)
  cv2.namedWindow('image_option1')
  cv2.setMouseCallback('image_option1', pick_option1)
  cv2.namedWindow('image_option2')
  cv2.setMouseCallback('image_option2', pick_option2)
  cv2.namedWindow('image_option3')
  cv2.setMouseCallback('image_option3', pick_option3)
  #per category
  k=0
  category=config['categories']
  catnr = 0
  imgnr = 0
  offset=5
  nocheck = False
  while catnr<len(category):
    cat = category[catnr]['searchFor']
    urls = glob.glob(config['global']['fileLocation']+cat+'\\*.jpg',recursive=True)
    imgnr=0
    prevnr=-1
    while imgnr<len(urls):
      image = urls[imgnr]
      if ('_' not in image):
        if (prevnr!=imgnr):
          nocheck = False
          prevnr = imgnr
        print( "")
        if asIs:
          print(" Click on the image for the color of the "+cat.upper()+" !!! (No Zoom)")
        else:
          print(" Click on the image where the "+cat.upper()+" is !!! (Zoom will be used)")
        print( "")
        currentFile = image
        print (str(total)+" =>"+image)
        instructions()
        process(image)
        #if already done
        if 'colorxy' not in currentJson or nocheck:
          total=total+1
          k=cv2.waitKey()
          print(k)
          if k==43: #+
            offset = offset+5
            print(" Offset is now: "+str(offset))
            nocheck=True
          if k==45: #-
            offset = offset-5
            if (offset<=0):
              offset=2
            nocheck=True
            print(" Offset is now: "+str(offset))
          if k==117: #u (+)
            offsetHSV = offsetHSV+5
            print(" Offset HSV is now: "+str(offsetHSV))
            nocheck=True
          if k==121: #y
            offsetHSV = offsetHSV-5
            if (offsetHSV<=0):
              offsetHSV=2
            nocheck=True
            print(" Offset HSV is now: "+str(offsetHSV))
          if k==93: #]
            offsetZoom = offsetZoom+100
            print(" Offset ZOOM is now: "+str(offsetZoom))
            nocheck=True
          if k==91: #[
            offsetZoom = offsetZoom-100
            if (offsetZoom<=0):
              offsetZoom=200
            nocheck=True
            print(" Offset ZOOM is now: "+str(offsetZoom))
          if k==97: #a
            #no zoom, save as is
            nocheck=True
            if asIs:
              asIs = False
              print(" Take image based on Zoom level")
            else:
              print(" Take image as Is (no zoom)")
              asIs = True
          if k==120: #x
            clearJson(currentFile)
            print(" JSON reset ")
            next()
          if k==100: #d
            #delete images
            delcmd = image.replace(".jpg","*.jpg")
            fileList = glob.glob(delcmd)
            # Iterate over the list of filepaths & remove each file.
            for filePath in fileList:
                try:
                    os.remove(filePath)
                except:
                    print("Error while deleting file : ", filePath)
            print(" Images "+image+" DELETED ")
            next()
            imgnr=imgnr+1
          if k==105: #i
            #color = input("Enter your color: ")
            #rec={}
            #rec['man_color']=color
            #rec['man_hexcolor']=color
            #updateJson(currentFile,rec,False)
            imgnr=imgnr+1
          if k==113: #q
            break
          if k==110: #n
            imgnr=imgnr+1
            next()
          if k==112: #p
            imgnr=imgnr-1
            prevnr=-1
            next()
        else:
          # childnr=0
          # for child in currentJson['childs']:
          #   if (len(child['images'])==3):
          #     filen = child['images'][1]
          #     theimage = cv2.imread(filen)
          #     theimage = cv2.flip(theimage,1)
          #     filen = filen.replace("_1.jpg","_a.jpg")
          #     cv2.imwrite(filen, theimage)              
          #     currentJson['childs'][childnr]['images'].insert(0,filen)
          #   childnr=childnr+1
          # updateJson(image)

          imgnr = imgnr+1
          next()
      else:
        imgnr = imgnr+1
        next()
    catnr=catnr+1
    if k==113:
      break
    

  print("We are done!\n")
  print("Processed: "+str(total)+" results\n")
  print("NEXT STEP: 3. identifyLargeImagesAWS.")


try:
  fileconfig = sys.argv[1]
  processImages(fileconfig)
except Exception as e: 
  print(e)
  traceback.print_exception(*sys.exc_info())
  print ("Specify configuration json (like config.json) on startup")
