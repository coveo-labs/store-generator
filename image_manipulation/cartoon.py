import cv2
import os
import numpy as np
import imutils

def read_file(filename):
  img = cv2.imread(filename)
  #cv2.imshow('here',img)
  return img

def edge_mask(img, line_size, blur_value, blur2):
  gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  gray_blur = cv2.medianBlur(gray, blur_value)
  edges = cv2.adaptiveThreshold(gray_blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, line_size, blur2)
  #cv2.imshow('here2',edges)
  return edges

def edge(img, line_size, blur_value):
  gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, line_size, blur_value)
  return edges

def blur(img, line_size, blur_value):
  #gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  gray_blur = cv2.medianBlur(img, blur_value)
  return gray_blur

def color_quantization(img, k):
# Transform the image
  data = np.float32(img).reshape((-1, 3))

# Determine criteria
  criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 0.001)

# Implementing K-Means
  ret, label, center = cv2.kmeans(data, k, None, criteria, 1, cv2.KMEANS_RANDOM_CENTERS)
  center = np.uint8(center)
  result = center[label.flatten()]
  result = result.reshape(img.shape)
  return result

def auto_canny(image, sigma=0.33):
	# compute the median of the single channel pixel intensities
	v = np.median(image)
	# apply automatic Canny edge detection using the computed median
	lower = int(max(0, (1.0 - sigma) * v))
	upper = int(min(255, (1.0 + sigma) * v))
	edged = cv2.Canny(image, lower, upper)
	# return the edged image
	return edged

def posterization(img, n):
    x = np.arange(256)                   #0,1,2...An array of integers up to 255

    ibins = np.linspace(0, 255, n+1)     #Input from LUT is 255/(n+1)Split with
    obins = np.linspace(0,255, n)        #Output from LUT is 255/Split by n

    num=np.digitize(x, ibins)-1          #Number the input pixel values to posterize
    num[255] = n-1                       #Correct the number of pixel value 255 that is off by digitize processing

    y = np.array(obins[num], dtype=int)   #Create a posterizing LUT
    #pos_LUT(n, y)                         #Create LUT diagram
    pos = cv2.LUT(img, y)                 #Perform posterization

    return pos

def processFile2(filen, rename):
  img = read_file(filen)
  gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  gray = cv2.medianBlur(gray, 3)
  #gray = cv2.GaussianBlur(gray, (3,3), 2)

  #color = cv2.bilateralFilter(gray, 5, 150, 150)
  #edge = auto_canny(gray);#cv2.Canny(gray,100,200)
  edge = cv2.Canny(gray,100,150)
  kernel = np.ones((3,3),np.uint8)
  edge = cv2.dilate(edge,kernel,1)
  #cv2.imshow('here2',edge)
  #cv2.waitKey(0)
  drawing = np.zeros((gray.shape[0], gray.shape[1], 3), dtype=np.uint8)
  drawing = cv2.cvtColor(drawing, cv2.COLOR_BGR2GRAY)
   
  contours, hierarchy= cv2.findContours(edge.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
  for i in range(len(contours)):
    area = cv2.contourArea(contours[i])
    #print (area)
    if (area>300):
      print (area)
      cv2.drawContours(drawing, contours, i, (255,255,255), 5, cv2.LINE_8, hierarchy, 0)
  
  #edge = cv2.dilate(drawing,kernel,1)

  kernel = np.ones((5,5),np.uint8)
  #edge = cv2.dilate(drawing,kernel,1)
  drawing = cv2.bitwise_not(drawing)
  #cv2.imshow('here2',drawing)
  #cv2.waitKey(0)
  cartoon = cv2.bitwise_and(img, img, mask=drawing)
  #cartoon = posterization(cartoon,15)
  #cartoon = color_quantization(cartoon, 20)
  cv2.imwrite(rename, cartoon)
  #cv2.imshow('here2',cartoon)
  #cv2.waitKey(0)

def processFile4(filen, rename, rename_res):
  img = read_file(filen)
  if img is not None:
   if (img.shape[0]>200):
    #img = cv2.bilateralFilter(img, d=19, sigmaColor=100,sigmaSpace=200)
    #cartoon = cv2.stylization(img, sigma_s=60, sigma_r=0.15)
    #cartoon = cv2.edgePreservingFilter(img, flags=1, sigma_s=60, sigma_r=0.4)
    #img = cv2.detailEnhance(img, sigma_s=60, sigma_r=0.15)
    cartoon = cv2.stylization(img, sigma_s=200, sigma_r=0.15)
    #gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    #edge = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 53, 25)
    #kernel = np.ones((2,2),np.uint8)
    #edge = cv2.bitwise_not(edge)
    #edge = cv2.dilate(edge,kernel,2)
    #edge = cv2.bitwise_not(edge)
    #cartoon = cv2.bitwise_and(img, img, mask=edge) 


    res = imutils.resize(cartoon, width=400)
    cv2.imwrite(rename, cartoon)
    cv2.imwrite(rename_res, res)
    #cv2.imshow('here2',cartoon)
    #cv2.waitKey(0)


def processFile3(filen, rename, rename_res):
  img = read_file(filen)
  if img is not None:
   if (img.shape[0]>200):
    #img = cv2.bilateralFilter(img, d=19, sigmaColor=100,sigmaSpace=200)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    #gray = cv2.medianBlur(gray, 5)
    gray = cv2.GaussianBlur(gray, (3,3), 1)

    edge = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 53, 16)
    kernel = np.ones((2,2),np.uint8)
    #edge = cv2.bitwise_not(edge)
    #edge = cv2.dilate(edge,kernel,2)
    #edge = cv2.bitwise_not(edge)
    cartoon = cv2.bitwise_and(img, img, mask=edge) 
    #color = cv2.bilateralFilter(gray, 5, 150, 150)
    #edge = auto_canny(gray);#cv2.Canny(gray,100,200)
    #edge = cv2.Canny(gray,100,150)
    """ kernel = np.ones((3,3),np.uint8)
    edge = cv2.dilate(edge,kernel,1)
    #cv2.imshow('here2',edge)
    #cv2.waitKey(0)
    drawing = np.zeros((gray.shape[0], gray.shape[1], 3), dtype=np.uint8)
    drawing = cv2.cvtColor(drawing, cv2.COLOR_BGR2GRAY)
    
    contours, hierarchy= cv2.findContours(edge.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    for i in range(len(contours)):
      area = cv2.contourArea(contours[i])
      #print (area)
      if (area>0):
        print (area)
        cv2.drawContours(drawing, contours, i, (255,255,255), 5, cv2.LINE_8, hierarchy, 0)
    
    #edge = cv2.dilate(drawing,kernel,1)

    kernel = np.ones((5,5),np.uint8)
    #edge = cv2.dilate(drawing,kernel,1)
    drawing = cv2.bitwise_not(drawing)
    #cv2.imshow('here2',drawing)
    #cv2.waitKey(0)
    #img = cv2.GaussianBlur(img, (3,3), 2)
    cartoon = cv2.bitwise_and(img, img, mask=drawing) """
    #cartoon = posterization(cartoon,15)
    #cartoon = color_quantization(cartoon, 20)

    #kernel = np.ones((3,3),np.uint8)
    #cartoon = cv2.dilate(cartoon,kernel,1)

    res = imutils.resize(cartoon, width=400)
    cv2.imwrite(rename, cartoon)
    cv2.imwrite(rename_res, res)
    #cv2.imshow('here2',cartoon)
    #cv2.waitKey(0)

def processFile(filen,rename):
  img = read_file(filen)
  line_size = 9
  blur_value = 9
  blur_val2 = 9
  edges = edge_mask(img, line_size, blur_value, blur_val2)
  kernel = np.ones((5,5),np.uint8)
  edges = cv2.dilate(edges,kernel,1)
  #edges = blur(img, line_size, blur_value)
  #edges = edge(img, line_size, blur_value)

  total_color = 29
  cartoon3 = cv2.bitwise_and(img, img, mask=edges) 
  #cv2.imshow('here2',cartoon3)
  #cv2.waitKey(0)

  #cartoon3 = color_quantization(cartoon3, total_color)
  #blurred = cv2.bilateralFilter(img, d=7, sigmaColor=200,sigmaSpace=200)

  #cartoon = cv2.bitwise_and(blurred, blurred, mask=edges)
  blur_value = 9
  #cartoon = blur(cartoon, line_size, blur_value)
  #cartoon = cv2.flip(cartoon3, 1)
  #cv2.imshow('here2',cartoon)
  cv2.imwrite(rename, cartoon3)
  #cv2.waitKey(0)

count=0
processFile4('c:/fashion/cn10567284.jpg','c:/fashion/out/cn10567284.jpg','c:/fashion/out_res/cn10567284.jpg')
processFile4('c:/fashion/cn10567279.jpg','c:/fashion/out/cn10567279.jpg','c:/fashion/out_res/cn10567279.jpg')
for url in os.listdir('c:/fashion'):
#url='cn7629899.jpg'
  print (url)
  count=count+1
  if (url!='out' and '.zip' not in url):
    processFile4('c:/fashion/'+url,'c:/fashion/out/'+url,'c:/fashion/out_res/'+url)
    #if (count>50):
    #  break
