#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=C0301,C0325,C0111

import json
import traceback
import os
import sys
import re
import urllib
import requests
import time
import ssl
import urllib.parse

import os


# Script will query all results from an index
# Will download the metadata + text into a json for each file
# Use: Filter as the initial query
# Make sure you have openssl > 1.0 installed
#   Check:
#     python2 -c "import json, urllib2; print json.load(urllib2.urlopen('https://www.howsmyssl.com/a/check'))['tls_version']"
#     Or:
#     python3 -c "import json, urllib.request; print(json.loads(urllib.request.urlopen('https://www.howsmyssl.com/a/check').read().decode('UTF-8'))['tls_version'])"
#     --> TLS 1.2
#   brew install python --with-brewed-openssl
#     Or if you have 2.7
#   brew install python@2 --with-brewed-openssl
#   echo 'export PATH="/usr/local/opt/openssl/bin:$PATH"' >> ~/.bash_profile
#   source ~/.bash_profile


# ---------------------------------------------------------
# setup
# API KEY Priviliges:
#   Search : Exeucte Queries + View All Content
#   Organization: View
# ---------------------------------------------------------
querydelay = 0.07  # in seconds
fotodelay = 1  # in seconds
filelocation = '../images/'

# ---------------------------------------------------------
# general functions
# ---------------------------------------------------------
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


def get_image(querystr, length, page,key):
    #print("Coveo Query: " + query)
    query = "https://api.pexels.com/v1/search?"+"query= "+querystr+"&per_page="+str(length)+"&page="+str(page)
    #color gives bad results
    #+"&color="+color
    response = requests.request('GET', query, headers={
                                'Authorization': 'Bearer '+key})

    if response.status_code == 200:
        response = response.json()
        response['error'] = False
    elif response.status_code == 401:
        response = response_error("Authentication error TEXT ")
    else:
        response = response_error("Server error "+str(response.status_code))

    return response

def response_error(err):
    message = "There was an issue with the request. Please contact your administrator. (%s)" % err
    print(message)
    return message


def saveImage(foto,downloadurl,category,location, filepath):
   path = filepath+category+'/'
   img = path+str(location)+'.jpg'
   foto['images']=[img]
   foto['groupid']=location
   if (not os.path.isfile(path+str(location)+'.json')):
    if ('https' in downloadurl):
      downloadurl = downloadurl.replace('h=350','w=400')
      img_data = requests.get(downloadurl).content
      time.sleep(0.2)
      if (not os.path.isdir(path)):
        os.makedirs(path) 
      with open(path+str(location)+'.jpg', 'wb') as handler:
        handler.write(img_data)
   with open(path+str(location)+'.json', "w", encoding='utf-8') as handler:
              text = json.dumps(foto, ensure_ascii=True)
              handler.write(text)


def parsePhotos(json,category,allids, path):
  lastid=0
  for foto in json['photos']:
    size = 'medium'
    print ("Image: "+foto['src'][size])
    sizes = len(str(foto['id']))
    id = int(str(foto['id'])[:sizes-2])
    print (str(id))
    if id not in allids:
      foto['category']=category
      saveImage(foto,foto['src'][size],category, foto['id'],path)
      allids.append(id)
    else:
      print("Same id, skipping")
  return allids

def getImages(searchstring, cat, page, allids, key, path):
   imageresponse = get_image(searchstring, 80,page, key)
   allids=parsePhotos(imageresponse,cat,allids, path)
   return imageresponse, allids

def getAllResults(filename):
    # ---------------------------------------------------------
    # Execute the query
    #  We will use rowidfield for sorting and to go through all the results
    #  Keep continue until no more results left
    # ---------------------------------------------------------
    settings, config = loadConfiguration(filename)
    allids=[]
    print("Start...\n")
    for category in config['categories']:
          cat = category['searchFor']
          #Check if directory exists
          path = config['global']['fileLocation']+cat+'/'
          if (os.path.exists(path)) and config['global']['GetImagesSkipExistingCategories']:
            print ("Skipping existing category")
          else:
            #Reset allids if we want to force unique ids accross all categories
            if (not config['global']['forceUniqueImageAllCategories']):
              allids=[]
            searchstring = ""+category['searchFor']#+" "+gender
            for page in range(1,6):
              imageresponse, allids = getImages(searchstring, cat, page, allids, settings['pexelsApiKey'], config['global']['fileLocation'])
              if 'next_page' not in imageresponse:
                break
              else:
                if not imageresponse['next_page']:
                  break

    print("NEXT STEP: Manual check if the photos are in the right category.")
    print("NEXT STEP: Else remove, remove children and weird photos")
    print("WHEN DONE: 2_indentifyImagesAWS")

try:
  fileconfig = sys.argv[1]
  getAllResults(fileconfig)
except Exception as e: 
  print(e)
  traceback.print_exception(*sys.exc_info())
  print ("Specify configuration json (like config.json) on startup")

