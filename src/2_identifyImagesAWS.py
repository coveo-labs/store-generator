import boto3
import sys
import os
import json
import traceback
import re
import logging
from botocore.exceptions import ClientError
import base64
import operator
import math

import glob


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

def addParents(json,name):
    prev=''
    if json:
      #parents = json.reverse()
      parents = json[::-1]
      for parent in parents:
        if (prev==''):
          prev=parent['Name']
        else:
          prev=prev+'|'+parent['Name']
    if prev=='':
      prev = name
    else:
      prev = prev+'|'+name
    return prev

def detect_labels(photo, settings):

    client=boto3.client('rekognition', 
    aws_access_key_id=settings['awsAccessKeyId'],
    aws_secret_access_key=settings['awsSecretAccessKey'],
    region_name=settings['awsRegionName']
    )
    data = open(photo, "rb").read()

    response = client.detect_labels(Image={'Bytes':data},
        MaxLabels=20)

    #print('Detected labels for ' + photo) 
    labels=[]
    cat=[]
    rec={}
    #print (response)
    rec['AWS']=response['Labels']
    for label in response['Labels']:
        #print ("Label: " + label['Name'])
        #print ("Confidence: " + str(label['Confidence']))
        if int(label['Confidence'])>60:
            labels.append(label['Name'])
            cat.append(addParents(label['Parents'],label['Name']))
              #labels.append('P:'+parent['Name'])
        #    print ("   " + parent['Name'])
        #print ("Instances:")
        for instance in label['Instances']:
          #print (instance)
          cat.append(addParents(label['Parents'],label['Name']))

    labels = list(set(labels))
    cat = list(set(cat))
    print (cat)
    #print (labels)
    rec['categories']=cat
    rec['labels']=labels
    return rec

def loadJson(photo):
  newrecord={}
  photo = photo.replace('.jpg','.json')
  with open(photo, "r",encoding='utf-8') as fh:
        text = fh.read()
        newrecord = json.loads(text)
  return newrecord

def updateJson(photo, updaterec,loadonly):
  photo = photo.replace('.jpg','.json')
  newimages=[]
  if ('images' in updaterec):
    newimages=updaterec['images']
  try:
      with open(photo, "r",encoding='utf-8') as fh:
        text = fh.read()
        newrecord = json.loads(text)
        updaterec.update(newrecord)
      #print (updaterecorig)
      for img in newimages:
        if not img in updaterec['images']:
          updaterec['images'].append(img)
        #break
      if not loadonly:
       with open(photo, "w", encoding='utf-8') as handler:
        text = json.dumps(updaterec, ensure_ascii=True)
        handler.write(text)
  except:
    pass
  return updaterec

def process(image, settings, skipAlreadyDone):
    rec={}
    data = loadJson(image)
    if 'AWS' in data and skipAlreadyDone:
        print("Skipping, already done in AWS")
    else:
      if (os.path.isfile(image)):
        rec=detect_labels(image, settings)
        data= updateJson(image,rec, False)
      else:
        print("Skipping, no image???")
        data= updateJson(image,rec, True)

    return data

def getMeta(data, field):
  if field in data:
    return data[field]
  else:
    return ''


def processImages(filename):
  #Get All files
  settings, config = loadConfiguration(filename)

  allCat=[]
  allColor=[]
  report={}
  total=0
  report['Total'] = 0
  
  catnr = 0
  while catnr<len(config['categories']):
    cat = config['categories'][catnr]['searchFor']
    urls = glob.glob(config['global']['fileLocation']+cat+'\\*.jpg',recursive=True)
    print ("Path: "+config['global']['fileLocation']+cat+'\\*.jpg')
    for image in urls:
      if ('_' not in image):
        print (str(total)+" =>"+image)
        total=total+1
        data = process(image,settings, config['global']['AWSSkipExisting'])
        report['Total'] = report['Total']+1
        gender = ''
        if 'bestcolor' in data:
          colprop = 'Color:'+data['bestcolor']
          if colprop in report:
            report[colprop]=report[colprop]+1
          else:
            report[colprop]=1

        if 'gender' in data:
          gender = data['gender']
          if data['gender']=='Man':
            if ('Man' in report):
              report['Man'] = report['Man']+1
            else:
              report['Man'] = 1
          if data['gender']=='Female':
            if ('Female' in report):
              report['Female'] = report['Female']+1
            else:
              report['Female'] = 1
        if 'category' in data:
          if data['category'] not in allCat:
              allCat.append(data['category'])
          if 'categories' in data:
           for cat in data['categories']:
            gendercat = gender+'|'+cat
            if gendercat in report:
              report[gendercat] = report[gendercat]+1
            else:
              report[gendercat] = 1

            if cat not in allCat:
              allCat.append(cat)
          if 'colors' in data:
           for col in data['colors']:
            color = col.replace(';','_')
            if color not in allColor:
              allColor.append(color)
    catnr=catnr+1
  allCat.sort()
  allColor.sort()
  
  with open("Cat.txt", "w", encoding='utf-8') as handler:
    for cat in allCat:
      handler.write(cat)
      handler.write(';\n')
  with open("Colors.txt", "w", encoding='utf-8') as handler:
    for col in allColor:
      handler.write(col)
      handler.write(';\n')
  with open("Report.json", "w", encoding='utf-8') as handler:
      text = json.dumps(report, ensure_ascii=True, sort_keys=True)
      handler.write(text)
  print("We are done!\n")
  print("Processed: "+str(total)+" results\n")
  print("NEXT STEP: Assign colors manual: 3_assignColors")
  
#print(rgbToColor('c6bcb1'))
#print(rgbToColor('c4bdb9'))

#main('../images/dress/blue/1375840.jpg')
#main('../images/dress/blue/767990.jpg')
#main('../images/dress/blue/1569178.jpg')
try:
  fileconfig = sys.argv[1]
  processImages(fileconfig)
except Exception as e: 
  print(e)
  traceback.print_exception(*sys.exc_info())
  print ("Specify configuration json (like config.json) on startup")
