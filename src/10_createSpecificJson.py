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

import glob

DIRECTORY='sfdc'


def transformToSFDCCase(jsondata):
  #input:
  #   {
  #   "filename": "CASE_Mercury_1_activating the assistent",
  #   "case": "C1004066",
  #   "title": "On my Mercury, how do i fix: activating the assistent is shutting down the Assistente Boat Assisted Software Suite application.",
  #   "boat": "Mercury",
  #   "version": "1",
  #   "problem": "On my Mercury, how do i fix: activating the assistent is shutting down the Assistente Boat Assisted Software Suite application.",
  #   "symptoms": "The Mercury Assistent boat assisted software suite was shut down because the manual activation process.",
  #   "comments": {
  #     "filename": "CASECOMM_Mercury_1_C1004066",
  #     "comment": "Actually, Mercury's Assist software suite was shut down because it had not been properly updated in some time and its proprietary manual activation process no longer functioned. The Assist software suite is now available through the Mercury Service Dashboard.",
  #     "case": "C1004066"
  #   }
  # }
  ######################################
  #output:
  # {
  #           "attributes": {
  #               "type": "Case",
  #               "referenceId": "CaseRef1"
  #           },
  #           "Subject": "charges button is not working",
  #           "Origin": "Web",
  #           "Reason": "Equipment Complexity",
  #           "Description": "My charges button is not working (couldn't prees it) but I found out that I could tap the Speedbit and it will still working but then I had trouble scanning and I would change something in the settings and it wouldn't change so I decided to make a new account so I deleted the old one but now I need to hold the button for 3 seconds but I can't can someone plz help",
  #           "Priority": "Medium",
  #           "Status": "New",
  #           "Type": "Electrical"
  #       }
  newjson={}
  newjson["attributes"]={}
  newjson["attributes"]["type"]="Case"
  newjson["attributes"]["referenceId"]=jsondata["case"]
  newjson["Subject"]=jsondata["title"]
  newjson["Origin"]="Web"
  newjson["Reason"]="Setup"
  newjson["Description"]=jsondata["symptoms"]
  newjson["Priority"]="Medium"
  newjson["Status"]="New"
  newjson["Type"]=jsondata["boat"]
  return newjson

def transformToSFDCComment(jsondata):
  #input:
  #   {
  #   "filename": "CASE_Mercury_1_activating the assistent",
  #   "case": "C1004066",
  #   "title": "On my Mercury, how do i fix: activating the assistent is shutting down the Assistente Boat Assisted Software Suite application.",
  #   "boat": "Mercury",
  #   "version": "1",
  #   "problem": "On my Mercury, how do i fix: activating the assistent is shutting down the Assistente Boat Assisted Software Suite application.",
  #   "symptoms": "The Mercury Assistent boat assisted software suite was shut down because the manual activation process.",
  #   "comments": {
  #     "filename": "CASECOMM_Mercury_1_C1004066",
  #     "comment": "Actually, Mercury's Assist software suite was shut down because it had not been properly updated in some time and its proprietary manual activation process no longer functioned. The Assist software suite is now available through the Mercury Service Dashboard.",
  #     "case": "C1004066"
  #   }
  # }
  ######################################
  #output:
  # {
  #           "attributes": {
  #               "type": "CaseComment",
  #               "referenceId": "CaseCommentRef1"
  #           },
  #           "CommentBody": "SteveH Wrote : If the button is broken then the only option would be to replace the Speedbit as it tends to not be repairable.\r\n \r\nIf you are still within warranty (see www.fitbit.com/returns ) then you can start the process by contacting customer support via one of the options in this link:",
  #           "ParentId": "@CaseRef1"
  #       }
  newjson={}
  newjson["attributes"]={}
  newjson["attributes"]["type"]="CaseComment"
  newjson["attributes"]["referenceId"]=jsondata["case"]+"1"
  newjson["CommentBody"]=jsondata["comments"]["comment"]
  newjson["ParentId"]='@'+jsondata["case"]
  return newjson


def loadJson(filename):
  newrecord={}
  with open(filename, "r",encoding='utf-8') as fh:
        text = fh.read()
        newrecord = json.loads(text)
  return newrecord

def process(filename):
  total=0
  alljsoncases=[]
  alljsoncomments=[]
  jsons = glob.glob('json\\CASE_*.json',recursive=True)
  for filename in jsons:
    print("Processing: "+filename)
    jsondata = loadJson(filename)
    case = transformToSFDCCase(jsondata)
    casecomment = transformToSFDCComment(jsondata)
    alljsoncases.append(case)
    alljsoncomments.append(casecomment)
    total+=1
  #save the files
  with open(DIRECTORY+"\\Cases.json", "w", encoding='utf-8') as handler:
        jsondata={}
        jsondata["records"]=alljsoncases
        text = json.dumps(jsondata, ensure_ascii=True)
        handler.write(text)
  with open(DIRECTORY+"\\CasesComments.json", "w", encoding='utf-8') as handler:
        jsondata={}
        jsondata["records"]=alljsoncases
        text = json.dumps(jsondata, ensure_ascii=True)
        handler.write(text)
  
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
