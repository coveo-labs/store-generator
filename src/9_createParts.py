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
import openai
import csv
import random

import glob

P_ENGINE = 'text-curie-001'
FILECOUNTER=2000
FILENAME=''
FILENAME_PARTS='Parts.csv'
CASES_ONLY = True
ALL_PARTS=[]
PARTS=[]
PARTS_POINTER=0

def readCSV():
  global ALL_PARTS
  with open(FILENAME_PARTS, mode='r') as csv_file:
    ALL_PARTS = list(csv.DictReader(csv_file, delimiter=';'))
  level1=''
  level2=''
  level3=''
  #Fix the parts, because level1, level2, level3 might not be there
  for part in ALL_PARTS:
    #print (part)
    part['Level1']=part['ï»¿Level1']
    if part['Level1']=='':
      part['Level1']=level1
    else:
      level1 = part['Level1']
    if part['Level2']=='':
      part['Level2']=level2
    else:
      level2 = part['Level2']
    if part['Level3']=='':
      part['Level3']=level3
    else:
      level3 = part['Level3']
    #clean field 'Power (EcPowerOutput)'
    field = part['Field']
    regex = r"(.* \()"
    result = re.sub(regex, "", field, 0, re.MULTILINE).replace(")","")
    #print (result)
    if (result.startswith('Ec') and not result.startswith('Ec_')):
       result = result.replace("Ec","Ec_")
    part['Field']=result.lower()
    #print (ALL_PARTS[1])

def writeCSV(all):
  fieldnames=[]
  for rec in all:
    for key in rec.keys():
      if key not in fieldnames:
        fieldnames.append(key)

  with open('outputParts.csv', 'w', encoding='UTF8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames,delimiter=';',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writeheader()
    writer.writerows(all)


def createBigPartsList():
  global PARTS
  PARTS=[]
  currentPart={}
  for part in ALL_PARTS:
    if (part['Field']=='ec_price'):
      #this is the last record
      currentPart[part['Field']]=part['Values']
      currentPart['Level1']=part['Level1']
      currentPart['Level2']=part['Level2']
      currentPart['Level3']=part['Level3']
      #currentPart.append(part)
      PARTS.append(json.dumps(currentPart))
      currentPart={}
    else:
      currentPart[part['Field']]=part['Values']

  #for part in PARTS:
  #  print (part)

def createPartRecord():
  global PARTS_POINTER
  global PARTS
  PARTS_POINTER += 1
  if (PARTS_POINTER>=len(PARTS)):
    PARTS_POINTER=0
  record = json.loads(PARTS[PARTS_POINTER])
  print (record)
  for key in record.keys():
    if (';' in record[key]):
      #multiple values
      keys = record[key].split(';')
      thekey = random.randint(0, len(keys)-1)
      print (thekey)
      record[key] = keys[thekey]
  #update price
  print (record['ec_price'])
  try:
    if (int(record['ec_price'])>10):
      record['ec_price']=int(record['ec_price'])+random.randint(0,int(record['ec_price'])/10)
    else:
      record['ec_price']=int(record['ec_price'])+random.randint(0,int(record['ec_price']))
  except:
    print("Bad price")
  return record


def cleanUp(text):
  text = text.replace('<|endoftext|>','')
  text = text.replace('\n','').replace('* * *','').strip()
  return text

def removeUnfinishedSentence(text):
  #text bla. bla bla --> remove the last part
  if (not text.endswith('.')):
    if ('.' in text):
    	text = '.'.join(text.split('.')[:-1])
  return text


def executeOpenAI(prompt, temp, length, stop=[]):
  if len(stop)==0:
    stop=None
  results = openai.Completion.create(
    engine=P_ENGINE,
    prompt=prompt,
    temperature=temp,
    max_tokens=length,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0,
    stop=stop
  )
  return results["choices"][0]["text"].strip(' \n').replace('\n','<BR>')


def executeOpenAIv2(prompt, temp, length, stop=[]):
  if len(stop)==0:
    stop=None
  results = openai.Completion.create(
    engine=P_ENGINE,
    prompt=prompt,
    temperature=temp,
    max_tokens=length,
    top_p=1,
    frequency_penalty=0.4,
    presence_penalty=0.7,
    stop=stop
  )
  return results["choices"][0]["text"].strip(' \n').replace('\n','<BR>')

def loadConfiguration(filename):
  settings={}
  config={}
  try:
      #with open(filename, "r",encoding='utf-8') as fh:
      #  text = fh.read()
      #  config = json.loads(text)
      with open("settings.json", "r",encoding='utf-8') as fh:
        text = fh.read()
        settings = json.loads(text)
        openai.api_key = settings['openaiApiKey']
  except:
    print ("Failure, could not load settings.json or config.json")
  return settings, config

def saveOutput(html,json=None):
  global FILENAME
  file_object = open(FILENAME+'.html', 'a', encoding="utf-8")
  file_object.write(html)
  file_object.close()
  if json is not None:
    saveJSON(html,json)

def saveJSON(html,jsondata):
  global FILECOUNTER
  filename = jsondata['filename']
  file_object = open('json\\'+filename+'_'+str(FILECOUNTER)+'.json', 'w', encoding="utf-8")
  file_object.write(json.dumps(jsondata))
  file_object.close()
  file_object = open('html\\'+filename+'_'+str(FILECOUNTER)+'.html', 'w', encoding="utf-8")
  file_object.write(html)
  file_object.close()
  FILECOUNTER+=1


def createTextv2(product, keyword, boat, version, sentence, temp, length):
  sentence = sentence.replace('[PRODUCT]',product)
  sentence = sentence.replace('[KEYWORD]',keyword)
  sentence = sentence.replace('[BOAT]',boat)
  sentence = sentence.replace('[VERSION]',version)
  line = executeOpenAIv2( sentence,
      temp,
      length
    )
  return line

def createRecord(recid, boat):
  record=[]
  record = createPartRecord()
  productid='prt_'+f'{recid:07}'
  record['permanentid']=productid
  record['ec_name']=record['Level3']
  #Electrical; Electrical|Power Supplies and Charger; Electrical|Power Supplies and Charger|Marine Sonar Panels
  record['ec_category']=record['Level1']+';'+record['Level1']+'|'+record['Level2']+';'+record['Level1']+'|'+record['Level2']+'|'+record['Level3']
  record['ec_productid']=productid
  record['ec_item_group_id']=''
  descr = createTextv2('','',boat,'','Create a name to sell: '+record['Level3'],0.6,100)
  record['ec_description']=descr
  #record['ec_brand']=''
  record['ec_sku']=productid
  #record['ec_price']=''
  record['ec_shortdesc']=descr
  record['ec_in_stock']='yes'
  record['ec_cogs']=''
  record['ec_rating']=str(random.randint(2,4))+'.'+str(random.randint(1,9))
  record['ec_images']=''
  #record['ec_height']=''
  #record['ec_width']=''
  #record['ec_depth']=''
  record['ec_power_output']=''
  #record['prt_DC_voltage']=''
  record['ec_weight']=''
  record['ec_waranty']=''
  record['prt_solar_cell_type']=''
  record['prt_plug_type']=''
  record['prt_material']=''
  record['prt_features']=''
  record['ec_colors']=''
  print (record)
  print("************************")
  return record

def process(filename):
  #Get All files
  settings, config = loadConfiguration(filename)
  readCSV()
  createBigPartsList()
  total=0
  temp = 0.8
  length = 500
  recid=1000
  versions=['1','1 beta','2','2 beta','3 beta','3','1','1 beta','2','2 beta','3 beta','3','1','1 beta','2','2 beta','3 beta','3']  
  #boats=['Mercury','Yamaha','Honda','Evinrude','Suzuki','Johnson','Tohatsu','OMC','Chrysler','Force','Mariner','Mercruiser','Mercury','Nissan','Sears']
  #versions=['1']  
  boats=['Mercury','Yamaha','Honda','Evinrude','Suzuki','Johnson','Tohatsu','OMC','Chrysler','Force','Mariner','Mercruiser','Mercury','Nissan','Sears']
  all_parts=[]
  for boat in boats:
    for version in versions:
      total = total+1
      recid = recid+total
      all_parts.append(createRecord(recid,boat))

  writeCSV(all_parts)

  print("We are done!\n")
  print("Processed: "+str(total)+" results\n")
  
try:
  #fileconfig = sys.argv[1]
  #process(fileconfig)
  process('')
except Exception as e: 
  print(e)
  traceback.print_exception(*sys.exc_info())
  #print ("Specify configuration json (like config.json) on startup")
