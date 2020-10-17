import pandas as pd
import numpy as np
import unicodedata
import re
import boto3
import webbrowser, os
import os
import json
import natsort
import io
import csv
import warnings
warnings.filterwarnings("ignore")
import PIL
import sys
from text_to_num import alpha2digit
import unicodedata
import re, string
import itertools
from itertools import chain
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
from pprint import pprint
from natsort import natsorted
from fpdf import FPDF
from PIL import Image
from itertools import chain
from text_to_num import alpha2digit
from pdf2image import convert_from_path
from glob import glob
from io import BytesIO




def textract_respond(file_doc,ACCESS_KEY ,SECRET_KEY):
    with open(file_doc, 'rb') as document:
        imageBytes = bytearray(document.read())
    textract = boto3.client('textract',    aws_access_key_id = ACCESS_KEY,    aws_secret_access_key =SECRET_KEY,region_name="us-east-1")
    response = textract.detect_document_text(Document={'Bytes': imageBytes})
    response_lines = [ item for item in response["Blocks"] if item["BlockType"] == "LINE" ]
    data_respond_textract = pd.json_normalize(response_lines)
    try:
        data_respond_textract["Text"] = data_respond_textract["Text"].str.replace(chr(34), '').str.replace(chr(39),"")  
    except:
        data_respond_textract["Text"]=""
    return data_respond_textract


def textract_respond_dos(file_doc,ACCESS_KEY,SECRET_KEY):
    image = Image.open(file_doc)    
    data_respond_textract = textract_respond(file_doc,ACCESS_KEY = ACCESS_KEY,SECRET_KEY=SECRET_KEY)
    width,height = image.size
    data_respond_textract["left_rectangle"] = round(width * data_respond_textract["Geometry.BoundingBox.Left"])
    data_respond_textract["top_rectangle"] = round(height * data_respond_textract["Geometry.BoundingBox.Top"])
    data_respond_textract["width_rectangle"] = round(width * data_respond_textract["Geometry.BoundingBox.Width"]) 
    data_respond_textract["height_rectangle"] = round(height * data_respond_textract["Geometry.BoundingBox.Height"])
    return data_respond_textract

def hackaton(images,n_doc,ac_key,s_key):
    data=pd.DataFrame()
    for i in range(len(images)):
        try:
            df_text=textract_respond_dos(images[i],ac_key,s_key)
            df_text["n_page"]=i
        except:
            df_text=pd.DataFrame()
        data=pd.concat([data,df_text])
    data.reset_index(drop=True,inplace=True)
    data["n_doc"]=n_doc
    return data



##UTILIDAD NETA
def montos(lista_texto):
    lista=[]
    for ele in lista_texto:
        if ("." in ele or "," in ele ) and len([x for x in "2.2.2" if x.isdigit()])>2:
            lista.append(ele)
    return lista
def cut_string(uti,text):   
    leng=len(uti.split(" "))
    text=text.split()
    lista=[]
    for i in text[leng:]:
        if sum(map(i.lower().count, "aeiouáéíóúü"))<2:
            lista.append(i)
        else:
            break
       
    return text[:leng]+lista

def utilidad_neta(data):
    utilidad=['utilidad neta',
 'utilidad meta',
 'utilidad (perdida) neta consolidada',
 'resultado neto del año',
 'resultado neto del ano',
 'utilidad neta consolidada',
 'utilidad neta del ano',
 'utilidad del año',
 'utilidad del ano',
 '(perdida), neto',
 'utilidad netta',
 'perdida neta',
 'resultado neto del año',
 'perdida neta del año',
 'utilidad neta del periodo',
 'utilidad neta del ejercicio',
 'participacion en la utilidad neta de asociadas',
 'utilidad (perdida) neta',
 'utilidad (perdida) del periodo',
 'ganancia neta del ejercicio',
 'ganancia neta',
 'utilidad del periodo',
 'utilidad neta del año']
    texto=" ".join(data["Text"].values)
    texto=texto.lower()
    
    dictio={}
    for uti in utilidad:
        text_p=texto[texto.find(uti) :texto.find(uti)+80]
        text_p=cut_string(uti,text_p)
        if len(text_p)>0:
            text_p=" ".join(text_p)
          
            uti_text=text_p.split(" ")
            uti_text=[x.strip() for x in uti_text]
           
            mon=montos(uti_text)
            dictio.update({uti:mon})
    dictio = dict(filter(lambda elem: len(elem[1]) > 0, dictio.items()))
    dictio = dict(filter(lambda elem: elem[1]== max(dictio.values()), dictio.items()))
    try:
        search=list(dictio.keys())[0]+" ".join(list(dictio.values())[0])
        data["utilidad_neta"]=data["Text"].map(lambda x:((search in x.lower())*1 or (x.lower() in search)*1) and len(x)>3)
        utilidad_neta=list(dictio.values())[0]
    except:
        data["utilidad_neta"]=0
        utilidad_neta=[]
    return utilidad_neta,data
