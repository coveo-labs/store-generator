import os
import json
import re
import sys
import base64
import operator
import traceback
from webcolors import (
    CSS3_NAMES_TO_HEX,
    hex_to_rgb,
)
import glob
import random

currentJson=[]

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

def basicColors():
  mainColors = ["black","silver","gray","white","maroon","red","purple","fuchsia","green","lime","olive","yellow","navy","blue","teal","aqua"]
  return mainColors

def normalizeColors(color):
   mainColors = basicColors() 
   for col in mainColors:
     if col in color:
       color += ' '+col
   return color.title()


def removeNumbers(input):
  r=re.compile(r'\d')
  output = r.sub('', input)
  return output

def getAllColors():
    css3_db = CSS3_NAMES_TO_HEX
    names = []
    rgb_values = []
    for color_name, color_hex in css3_db.items():
        names.append(color_name)
    for color_name in basicColors():
      names.append(color_name)
    return names

def checkCat(data,config,allcolors):
  #Is Person|Man in there
  #Is Person|Female in there
  gender='Men;Women'
  if 'categories' in data:
    if 'Person|Man' in data['categories']:
      gender='Men'
    if 'Person|Female' in data['categories']:
      gender='Women'
  title=getMeta(data,'category')
  author = getMeta(data,'photographer')
  if author:
    #only first name
    author = author.split(' ')[0]
    title = title +' by '+author
    title = title.title()
  url = getMeta(data,'url')
  #color in url is leading
  colorurl = ''
  for col in allcolors:
    if col in url:
      colorurl = col
  if colorurl:
    data['bestcolor']=colorurl.title()

  #title is also based upon url
  titleurl = url
  titleurl = titleurl.replace('https://www.pexels.com/photo/','')
  #print (titleurl)
  #check for gender in title
  if 'woman' in titleurl or 'women' in titleurl:
    gender='Women'
  else:
    if 'men-' in titleurl or 'man-' in titleurl:
      gender='Men'
  if config['useGender']:
    if not config['defaultGender']=='':
      gender = config['defaultGender']
  else:
    gender=''
  #print (gender+' = '+colorurl)
  titleurl = removeNumbers(titleurl.replace('-',' ').replace('/',' ')).title()
  #/women-s-yellow-floral-v-neck-top
  data['titledescr']=titleurl
  data['gender']=gender
  return data



def updateJson(photo):
  photo = photo.replace('.jpg','.json')
  #newimages=[]
  #if ('images' in updaterec):
  #  newimages=updaterec['images']
  try:
      # with open(photo, "r",encoding='utf-8') as fh:
      #   text = fh.read()
      #   newrecord = json.loads(text)
      #   updaterec.update(newrecord)
      # #print (updaterecorig)
      # for img in newimages:
      #   if not img in updaterec['images']:
      #     updaterec['images'].append(img)
      #   #break
      # if not loadonly:
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

def cleanLabels(data):
  toremove=["Person","Human"]
  newdata=[]
  for item in data:
    if item not in toremove:
      newdata.append(item)
  return newdata

def fixImages(images, config, baseurl, fileloc):
  newimages=[]
  for image in images:
    #..\\images\\hat\\601168.jpg
    newfile = image.replace(fileloc,baseurl)
    newfile = newfile.replace('..\\images\\',baseurl)
    newfile = newfile.replace('../images/',baseurl)
    newfile = newfile.replace('\\','/')
    newimages.append(newfile)
  return newimages

def getMeta(data, field):
  if field in data:
    return data[field]
  else:
    return ''


def createCategories(json, config):
  categories=[]
  if config['useGender']:
    genders=' and '.join(getMeta(json,'gender').split(';'))
    categories.append(genders)
    for cat in getMeta(config,'categoryPath').split('|'):
      categories.append(cat)
  else:
    for cat in getMeta(config,'categoryPath').split('|'):
      categories.append(cat)

  #categories = list(set(categories))

  return categories


def createCategoriesPaths(categories):
  catpath=''
  catpaths=[]
  for cat in categories:
     if catpath=='':
       catpath=cat #man
       catpaths.append(catpath)
     else:
       catpath=catpath+'|'+cat
       catpaths.append(catpath)
  #catpaths = list(set(catpaths))
  return catpaths

def createCategoriesSlug(categories):
  slug=[]
  catpath=''
  for cat in categories:
    cat=cat.lower().replace(' ','-')
    if catpath=='':
      catpath=cat #man
      slug.append(catpath)
    else:
      catpath=catpath+'/'+cat
      slug.append(catpath)
  
  #slug = list(set(catpaths))

  return slug

def createFacets(rec, facets, variant):
  facetData = ''
  createVariant=False
  for facet in facets:
    if facet['variant']==variant:
      facetname='cat_'+facet['name'].replace(' ','_').lower()
      if not facet['useWhenPropertyValue']=="":
        #then do not use random values, but the values set
        if 'default' in facet and facetname not in rec:
          facetvalue = facet['default']
        #check if useWhenPropertyValue is in cat_properties
        if 'cat_properties' in rec:
          #print (rec)
          if facet['useWhenPropertyValue'] in rec['cat_properties']:
            facetvalue=facet['values']
      else:
        values = facet['values'].split(';')
        facetvalue=values[random.randint(0,len(values)-1)]

      rec[facetname]=facetvalue
      facetData = facetData+' '+facetvalue
      createVariant=True

  return rec, facetData, createVariant


def createVariants(json, productid, facets):
  rec={}
  facetData = ''
  rec['cat_properties'] = json['cat_properties']
  rec, facetData, createVariant = createFacets(rec, facets, True)

  sku = productid+'_'+facetData.replace(' ','_').replace('/','_')
  rec["DocumentId"]= json['DocumentId']+'?sku='+sku
  rec["DocumentType"]="Variant"
  rec["FileExtension"]=".txt"
  rec["ObjectType"]="Variant"
  rec['data']=json['data']+' '+facetData
  rec['ec_name']=json['title']#getMeta(json,'titledescr')+facetData
  rec["title"]=json['title']#rec['ec_name']
  rec['ec_title']=rec['ec_name']
  rec["ec_product_id"]=productid
  rec["ec_variant_sku"]=sku
  rec["permanentid"]=sku
  saveJson(rec)

def process(json, allcolors, config, fileloc, baseurl, baseurlimages,child):
  #create final json
  print("Processing: "+str(json['id']))
  json = checkCat(json,config,allcolors)
  rec={}
  color_hex = getMeta(json, 'man_hexcolor')
  color = getMeta(json, 'man_color')
  productid= json['category']+str(json['id'])+'_'+str(color_hex)
  images = getMeta(json,'images')
  if child:
    print("Processing CHILD: "+str(json['id']))
    color_hex = getMeta(child, 'colorhex')
    color = getMeta(child, 'color')
    productid= json['category']+str(json['id'])+'_'+str(color_hex)
    images = getMeta(child,'images')

  images=fixImages(images, config, baseurlimages, fileloc)

  rec['DocumentId']=baseurl+json['category']+'/'+productid
  json['DocumentId']=rec['DocumentId']
  rec['ec_item_group_id']=json['category']+str(json['id'])
  rec["DocumentType"]="Product"
  rec["FileExtension"]=".html"
  rec["ObjectType"]="Product"
  rec["cat_attributes"]=cleanLabels(getMeta(json,'labels'))
  # categories=[]
  # for cat in getMeta(json,'categories'):
  #   if 'Clothing|' in cat:
  #     cleancat = cat.replace('Clothing|','')
  #     if cleancat not in categories:
  #       categories.append(cleancat)
  # categories.sort()
  # categoriesclean=[]
  # for category in categories:
  #   for cat in category.split('|'):
  #     if cat not in categoriesclean:
  #       categoriesclean.append(cat)

  rec["cat_categories"]=createCategories(json,config)
  rec["cat_slug"]=createCategoriesSlug(rec["cat_categories"])
  rec["ec_category"]=createCategoriesPaths(rec["cat_categories"])
  rec["cat_color"]=color
  rec["cat_colorhex"]=str(color_hex)
  rec["cat_gender"]=getMeta(json,'gender')
  rec["cat_mrp"]=config['avgPrice']+random.randint(0,int(config['avgPrice']/10))+0.75
  if 'rand_retailer' in json:
    rand_retailer = getMeta(json,'rand_retailer')
  else:
    rand_retailer=random.randint(0,len(config['retailers'])-1)
    json['rand_retailer']=rand_retailer
  rec["cat_retailer"]=config['retailers'][rand_retailer]
  colors = normalizeColors(color)
  rec["data"]=" ".join(getMeta(json,'labels'))+' '+getMeta(config,'categoryPath').replace('|',' ')+' '+getMeta(json,'titledescr')+' '+colors
  json['data']=rec['data']
  rec["ec_brand"]=rec["cat_retailer"]
  rec["ec_brand_name"]=rec["cat_retailer"]
  rec["ec_description"]=rec["data"]
  rec["ec_images"]=images
  #Change title
  title = color+' '+json["category"]+' by '+getMeta(json,'photographer')
  title = title.title()
  rec["ec_name"]=title#getMeta(json,'titledescr')
  rec["title"]=title#rec['ec_name']
  json['title']=title
  rec["ec_price"]=rec["cat_mrp"]
  rec["ec_product_id"]=productid
  rec["permanentid"]=rec['ec_product_id']
  rec["pexel_url"]=json['url']
  json['categories'].sort()
  rec["cat_properties"]=json['categories']
  json['cat_properties']=rec['cat_properties']

  #add facets
  createVariant = False
  rec, facetData, createVariant = createFacets(rec, config['facets'], False)
  rec['data']+= ' '+facetData

  saveJson(rec)
  if createVariant:
    createVariants(json, productid, config['facets'])

  return json


def storeJson(jsond,config):
  try:
       filename = config['global']['catalogJsonFile']
       directory = os.path.dirname(os.path.abspath(filename))
       if (not os.path.isdir(directory)):
        os.makedirs(directory) 
       with open(filename, "w", encoding='utf-8') as handler:
         text = json.dumps(jsond, ensure_ascii=True)
         handler.write(text)
  except:
    print("Error storing json")
    pass
  return 

def saveJson(json):
  global currentJson
  currentJson.append(json)
  return

def processImages(filename):
  global currentJson
  
  allcolors=getAllColors()

  total=0
  totalf=0
  totalchild=0
  uniqueproducts=0
  #per category
  k=0
  settings, config = loadConfiguration(filename)
  
  catnr = 0
  while catnr<len(config['categories']):
    totalnochild=0
    totalwithchild=0
    cat = config['categories'][catnr]['searchFor']
    urls = glob.glob(config['global']['fileLocation']+cat+'\\*.jpg',recursive=True)
    print ("Path: "+config['global']['fileLocation']+cat+'\\*.jpg')
    imgnr=0
    prevnr=-1
    while imgnr<len(urls):
      image = urls[imgnr]
      #print (image)
      if ('_' not in image):
        currentFile = image
        #print (str(total)+" =>"+image)
        json=loadJson(image)
        #print (json)
        #if already done
        if 'colorxy' in json:
          total=total+1
          kids=False
          json=process(json,allcolors,config['categories'][catnr], config['global']['fileLocation'],config["global"]["baseUrl"],config["global"]["baseUrlImages"],None)
          if 'childs' in json:
            for child in json['childs']:
                json=process(json, allcolors, config['categories'][catnr],config['global']['fileLocation'],config["global"]["baseUrl"],config["global"]["baseUrlImages"],child)
                totalchild=totalchild+1
                kids=True
          if kids:
            totalwithchild += 1
          else:
            totalnochild +=1
          imgnr = imgnr+1
        else:
          imgnr = imgnr+1
          totalf=totalf+1
      else:
        imgnr = imgnr+1
    #catnr = catnr+1

    print("CATEGORY: "+cat)
    print("Processed with Childs   : "+str(totalwithchild)+" results\n")
    print("Processed without Childs: "+str(totalnochild)+" results\n")
    print("==========================================\n")
    catnr=catnr+1

  #print (currentJson)
  storeJson(currentJson,config)  
  print("We are done!\n")
  print("Processed       : "+str(total)+" results\n")
  print("Processed BAD      : "+str(totalf)+" results\n")
  print("Processed Childs: "+str(totalchild)+" results\n")
    

print("NEXT STEP: 5. Push Catalog.")


try:
  fileconfig = sys.argv[1]
  processImages(fileconfig)
except Exception as e: 
  print(e)
  traceback.print_exception(*sys.exc_info())
  print ("Specify configuration json (like config.json) on startup")
