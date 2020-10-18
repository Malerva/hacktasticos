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

PATH=os.path.dirname(os.path.realpath(__file__))
ac_key="AKIAV2EWUFAKQ3YOI5G5"
s_key="SQ51A+CFCeNh4ltfn6SbcbDZSsjghkrmcL+7ttM2"
print(PATH)
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
def medida_aux(medida,texto):
    len_medida = len(medida.split())
    len_texto = len(texto.split())
    if len_medida != len_texto:
        medida = " ".join(texto.split()[:len_medida+1])
    return medida

def unidad_medida(data):
    texto=" ".join(data["Text"].values)
    texto=texto.lower()
    list_medida= ['millones de pesos', 
                  'miles de pesos', 
                  'miles de', 
                  'millones de pesos', 
                  'miles',
                  'millones',
                  'pesos',
                  'usd',
                  'dolares',
                  'euros'
                         ]
    lista_aux = []
    for x in list_medida:
        if x in texto:
            lista_aux.append(x)
            aux = x
            break
    try:
        data["medida"] = data["Text"].map(lambda x:(find(x,lista_aux))*1)
        medida = [x for x in data[data['medida']==1]['Text'].unique()][0].lower()
        texto_medida = medida[medida.find(aux):]
        medida_final = medida_aux(aux, texto_medida)
        medida_final =  medida_final.replace(')','').replace(',','').replace(',','')
    except:
        data['medida'] = 0
        texto_medida = 0
    return medida_final,data
#MAKE PDF
def plot_points(path_im,data,path_to_save):
    data["point"]=data[['left_rectangle', 'top_rectangle','width_rectangle', 'height_rectangle']].apply(lambda x:[x[0],x[1],x[2],x[3]],axis=1)
    im = np.array(Image.open(path_im).convert('RGB'))
    fig,ax = plt.subplots(1)
    ax.imshow(im)
    for i in data["point"].values:
        ax.add_patch(patches.Rectangle((i[0],i[1]),i[2],i[3],linewidth=.3,edgecolor='b',facecolor='none'))
    plt.axis('off')
    spec = plt.imshow
    plt.savefig(path_to_save,bbox_inches='tight', pad_inches=0,dpi=600)
def plot_wo_points(path_im,path_to_save):
    im = np.array(Image.open(path_im).convert('RGB'))
    fig,ax = plt.subplots(1)
    ax.imshow(im)
    plt.axis('off')
    spec = plt.imshow
    plt.savefig(path_to_save,bbox_inches='tight', pad_inches=0,dpi=600)
def makePdf(pdfFileName, listPages, directory = ''):
    if (directory):
        directory += "/"

    cover = Image.open(directory + str(listPages[0]) )
    width, height = cover.size

    pdf = FPDF(unit = "pt", format = [width, height])

    for page in listPages:
        pdf.add_page()
        pdf.image(directory + str(page) , 0, 0)

    pdf.output(directory + pdfFileName + ".pdf", "F")

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



def costo_ventas(data):
    utilidad=['costos de ventas',"costo de ventas","costo de venta"
 'costos por ventas',
 'costo de actividades ordinarias',"costos por verta","costo por verta"]
    texto=" ".join(data["Text"].values)
    texto=texto.lower()
    
    dictio={}
    for uti in utilidad:
        text_p=texto[texto.find(uti) :texto.find(uti)+80]
        text_p=cut_string(uti,text_p)
        if len(text_p)>0:
            text_p=" ".join(text_p).replace("(nota 12)","")
          
            uti_text=text_p.split(" ")
            uti_text=[x.strip() for x in uti_text]
           
            mon=montos(uti_text)
            dictio.update({uti:mon})
    print(dictio)
    dictio = dict(filter(lambda elem: len(elem[1]) > 0, dictio.items()))
    dictio = dict(filter(lambda elem: elem[1]== max(dictio.values()), dictio.items()))
    try:
        search=list(dictio.keys())[0]+" ".join(list(dictio.values())[0])
        data["costos_ventas"]=data["Text"].map(lambda x:((search in x.lower())*1 or (x.lower() in search)*1) and len(x)>3)
        search=list(dictio.values())[0]
    except:
        search=[]
        data["costos_ventas"]=0
    return search,data


def montos_1(lista_texto):
    lista=[]
    for ele in lista_texto:
        if ("." in ele or "," in ele  or ":" in ele or '' in ele) and len([x for x in ele if x.isdigit()])>2:
            lista.append(ele)
    return lista

dic_variables = {'Caja y bancos':['caja y bancos',
                             'efectivo y equivalentes de efectivo (nota',
                             'total disponibl',
                             'efectivo y equivalentes de effectivo, neto',
                             'efectivo y equivalentes al efectivo (nota',
                             'efective y equivalentes de effectiva (nota',
                             'efective y equivalentes de efective (nota',
                             'efectivo y equivalentes en efectiv',
                             'efectiva y equivalentes al efectiv',
                             'effective y equivalentes de efectives',
                             'efectivo y equivalentes de efectivo',
                             'efectivoy equivalentes al efectivo',
                             'efectivo y equivalentes all efective', 
                             'electivo y equivalentes de efectiv',
                             'efectivo y equivalentes de efectiv',
                             'efectivo v equivalentes al efectiv', 
                             'efective y equivalentes all efectiv',
                             'efectivo y equivalentes efectiv',
                             'efectivo v equivalentes de efectiv', 
                             'efectivo y equivalentes al efectiv',
                             'efectivo y equivalent',
                             'caja y disponible',
                             'efective y equivalentes de effectiv',
                             'efectivo y valores de realizacion inmediat',
                             'efective y equivalent',
                             'efectivo y bancos',
                             'efectiva v equivalentes de efectiv',
                             'elective y equivalentes al effcctiv',
                             'efectivo y equivalentes de efectiv',
                             'efectivo y equivalentes de efectiv',
                             'efectiv',
                             'disponible'
                            ],
                    'Ventas':['ventas por operación ordinacia',
                        'ingresos por operación',
                        'ventas netas y servicios',
                        'ventas netas',
                        'total ingresos operacionales',
                        'total ingresos de actividades ordinarias',
                        'ingresos de actividades de asociacion',
                        'ingresos de actividades ordinarias por venta de bebidas',
                        'ingresos de actividades ordinarias procedentes de contratos con clientes',
                        'ingresos totales',
                        'ingresos por ventas',
                        'ventas brutas',
                        'ingresos de operacion',
                        'ingresos por venta de bienes',
                        'ingresos netos operacionales (nota',
                        'ingresos por actividades ordinarias (nota',
                        'ingresos de actividades ordinarias (nota',
                        'ingreso por actividades ordinarias',
                        'ingreso de actividades ordinarias',
                        'ingresos de actividades ordinarias',
                        'ingresos por operación ordinaria',
                        'ingresos operacionales',
                        'ingresos ordinarios',
                        'venta de bienes',
                        'total ingresos',
                        'ingresos de actividades',
                        'ingresos',
                        'ventas'
                       ],
            'Total patrimonio':['patrimonio total', 
                               'total patrimonio neto'
                               'suma de los patrimonios',
                               'patrimonio total',
                               'suma el capital contable',
                               'total capital contable',
                               'total patrimonie',
                               'capital contable total',
                               'total capital',
                               'patrimonio de los accionistas, ver estado adjunto',
                               'patrimonio de los accionistas'
                               'patrimonio neto',
                               'total parrtmenia',
                               'total patrimonio',
                               'total patrimoni',
                               'patrimonio'
                    ]
           }

def find(text, list_find):
    for x in list_find:
        if x in text.lower():
            return True
            break
        else:
            continue
    return False
    

def caja_bancos(data):
    list_caja=dic_variables['Caja y bancos']
    data['Text'] = data['Text'].map(lambda x: str(x).replace(' ','.') if str(x).replace(' ','').isdigit() else x)
    texto=" ".join(data["Text"].values)
    texto=texto.lower()
    
    dictio={}
    for caja in list_caja:
        text_p=texto[texto.find(caja) :texto.find(caja)+len(caja)+80]
        text_p=cut_string(caja,text_p)
        if len(text_p)>0:
            text_p=" ".join(text_p)
          
            caja_text=text_p.split(" ")
            caja_text=[x.strip() for x in caja_text]
           
            mon=montos_1(caja_text)
            dictio.update({caja:mon})
            break
    try:
        #search=list(dictio.keys())+list(dictio.values())[0]
        search1 = list(dictio.keys())[0]
        search2 = list(dictio.values())[0]
        data["caja_y_bancos"]=data["Text"].map(lambda x:(((search1 in x.lower())*1 or ((find(x,search2))*1)) and len(x.replace('.',''))>=3)*1)
        #data["caja_y_bancos"]=data["Text"].map(lambda x:((((find(x,search))*1) and len(x.replace('.',''))>=3)*1))
        efectivo=list(dictio.values())[0]
        index = data[(data['caja_y_bancos']==1)&(data['Text'].map(lambda x: search1 in x.lower()))].index[0]
        data['caja_y_bancos'].loc[:index-1] = 0
        data['caja_y_bancos'].loc[index+10:] = 0
    except:
        data["caja_y_bancos"]=0
        efectivo=[]
    return efectivo,data

def ventas(data):
    list_ventas=dic_variables['Ventas']
    data['Text'] = data['Text'].map(lambda x: str(x).replace(' ','.') if str(x).replace(' ','').isdigit() else x)
    texto=" ".join(data["Text"].values)
    texto=texto.lower()
    
    dictio={}
    for venta in list_ventas:
        text_p=texto[texto.find(venta) :texto.find(venta)+len(venta)+80]
        text_p=cut_string(venta,text_p)
        if len(text_p)>0:
            text_p=" ".join(text_p)
          
            venta_text=text_p.split(" ")
            venta_text=[x.strip() for x in venta_text]
           
            mon=montos_1(venta_text)
            dictio.update({venta:mon})
            break
    try:
        search1 = list(dictio.keys())[0]
        search2 = list(dictio.values())[0]
        if search1 == 'ingresos' or search1 == 'ingresos operacionales': 
            data["ventas"]=data["Text"].map(lambda x:(((search1 == x.lower())*1 or ((find(x.lower(),search2))*1)) and len(x.replace('.',''))>=3)*1)
        else:
            data["ventas"]=data["Text"].map(lambda x:(((search1 in x.lower())*1 or ((find(x,search2))*1)) and len(x.replace('.',''))>=3)*1)
        ventas=list(dictio.values())[0]
        index = data[(data['ventas']==1)&(data['Text'].map(lambda x: search1 in x.lower()))].index[0]
        data['ventas'].loc[:index-1] = 0
        data['ventas'].loc[index+10:] = 0
        
    except:
        data["ventas"]=0
        ventas=[]
    return ventas,data




def patrimonio(data):
    list_pat = dic_variables['Total patrimonio']
    data['Text'] = data['Text'].map(lambda x: str(x).replace(' ','.') if str(x).replace(' ','').isdigit() else x)
    texto=" ".join(data["Text"].values)
    texto=texto.lower()
    
    dictio={}
    for pat in list_pat:
        text_p=texto[texto.find(pat) :texto.find(pat)+len(pat)+80]
        text_p=cut_string(pat,text_p)
        if len(text_p)>0:
            text_p=" ".join(text_p)
          
            pat_text=text_p.split(" ")
            pat_text=[x.strip() for x in pat_text]
           
            mon=montos(pat_text)
            dictio.update({pat:mon})
            break
    try:
        #search=list(dictio.keys())+list(dictio.values())[0]
        search1 = list(dictio.keys())[0]
        search2 = list(dictio.values())[0]
        if search1 == 'total patrimonio' or search1 == 'patrimonio': 
            data["patrimonio"]=data["Text"].map(lambda x:(((search1 == x.lower())*1 or ((find(x,search2))*1)) and len(x.replace('.',''))>=3)*1)                 
        else:
            data["patrimonio"]=data["Text"].map(lambda x:(((search1 in x.lower())*1 or ((find(x,search2))*1)) and len(x.replace('.',''))>=3)*1)
        #data["patrimonio"]=data["Text"].map(lambda x:((((find(x,search))*1) and len(x.replace('.',''))>=3)*1))
        patri=list(dictio.values())[0]
        index = data[(data['patrimonio']==1)&(data['Text'].map(lambda x: search1 in x.lower()))].index[0]
        data['patrimonio'].loc[:index-1] = 0
        data['patrimonio'].loc[index+10:] = 0
    except:
        data["patrimonio"]=0
        patri=[]
    return patri,data





def total_activo(data):
    activo=['total',
              'total actives corrientes',
              'total actives',
              'total activos corrientes',
              'total activos',
              'total del activo',
              'total activo',
              'total active',
              'activos corrientes totales',
              'activo total',
              'total activos no corrientes',
              'total activo corriente',
              
]
    texto=" ".join(data["Text"].values)
    texto=texto.lower()
    
    dictio={}
    for uti in activo:
        text_p=texto[texto.find(uti) :texto.find(uti)+80]
        text_p=cut_string(uti,text_p)
        if len(text_p)>0:
            text_p=" ".join(text_p)
          
            activo_text=text_p.split(" ")
            activo_text=[x.strip() for x in activo_text]
           
            act=montos(activo_text)
            dictio.update({uti:act})
    dictio = dict(filter(lambda elem: len(elem[1]) > 0, dictio.items()))
    dictio = dict(filter(lambda elem: elem[1]== max(dictio.values()), dictio.items()))
    try:
        search=list(dictio.keys())[0]+" ".join(list(dictio.values())[0])
        data["total_activo"]=data["Text"].map(lambda x:((search in x.lower())*1 or (x.lower() in search)*1) and len(x)>3)
        total=list(dictio.values())[0]
    except:
        data["total_activo"]=0
        total=[]
    return total,data

def total_pasivo(data):
    pasivo=['total',
              'total pasives corrientes',
              'total pasives',
              'total pasivo corrientes',
              'total pasivos',
              'total del pasivo',
              'total pasivos',
              'total pasivo',
              'pasivos corrientes totales',
              'pasivo total',
              'total pasivos no corrientes',
              'total pasivo corriente',
              
]
    texto=" ".join(data["Text"].values)
    texto=texto.lower()
    
    dictio={}
    for uti in pasivo:
        text_p=texto[texto.find(uti) :texto.find(uti)+80]
        text_p=cut_string(uti,text_p)
        if len(text_p)>0:
            text_p=" ".join(text_p)
          
            pasivo_text=text_p.split(" ")
            pasivo_text=[x.strip() for x in pasivo_text]
           
            pas=montos(pasivo_text)
            dictio.update({uti:pas})
    dictio = dict(filter(lambda elem: len(elem[1]) > 0, dictio.items()))
    dictio = dict(filter(lambda elem: elem[1]== max(dictio.values()), dictio.items()))
    try:
        search=list(dictio.keys())[0]+" ".join(list(dictio.values())[0])
        data["total_pasivo"]=data["Text"].map(lambda x:((search in x.lower())*1 or (x.lower() in search)*1) and len(x)>3)
        total=list(dictio.values())[0]
    except:
        data["total_pasivo"]=0
        total=[]
    return total,data

def utilidad_operacional(data):
    utilidad_ope=['utilidad operacional',
            'utilidad neta operaciones continuadas',
            'perdida neta de operaciones discontinuadas',
            'ganancias (perdidas) de actividades operacionales',
            'ganancia (perdida) procedente de operaciones continuadas',
            'utilidad (perdida) antes impuestos a la utilidad de operacionescontinuas y participacion en los resultados de asociadasy negocios conjuntos registrada utilizando el metodo de participacion',
            'utilidad (perdida) neta operaciones continuas',
            'ganancia (perdida), antes d e impuestos',
            'utilidad operativa',
            'utilidad de actividades operativas',
            'utilidad (perdida) por operaciones continuas',
            '(perdida) por diferencia en cambio no operacionales (nota 29)',
            
]
    texto=" ".join(data["Text"].values)
    texto=texto.lower()
    
    dictio={}
    for uti in utilidad_ope:
        text_p=texto[texto.find(uti) :texto.find(uti)+80]
        text_p=cut_string(uti,text_p)
        if len(text_p)>0:
            text_p=" ".join(text_p)
          
            utilidad_ope_text=text_p.split(" ")
            utilidad_ope_text=[x.strip() for x in utilidad_ope_text]
           
            pas=montos(utilidad_ope_text)
            dictio.update({uti:pas})
    dictio = dict(filter(lambda elem: len(elem[1]) > 0, dictio.items()))
    dictio = dict(filter(lambda elem: elem[1]== max(dictio.values()), dictio.items()))
    try:
        search=list(dictio.keys())[0]+" ".join(list(dictio.values())[0])
        data["utilidad_operacional"]=data["Text"].map(lambda x:((search in x.lower())*1 or (x.lower() in search)*1) and len(x)>3)
        total=list(dictio.values())[0]
    except:
        data["utilidad_operacional"]=0
        total=[]
    return total,data

def func_extract_text(text,type_):
    text = text.lower()
    if type_ == 'utilidadBruta':
        try:
            name = re.findall('utilidad\\sbruta\\s|perdida\\sbruta\\s|ganancia\\sbruta\\s|\\sbruta\\s',text)[0].strip()
            span = re.search('utilidad\\sbruta\\s|perdida\\sbruta\\s|ganancia\\sbruta\\s|\\sbruta\\s',text).span()[1]
            aux = text[span:span+100]
            list_ = aux.split(' ')
            result = func_tranform_text(list_,name,type_)
            return result
        except:
            return ('np')
        
    elif type_ == 'fecha':
        try:
            name = re.findall('((por)\\s(los|el)\\s(anos|ano)\\s(terminados|terminado))|(situacion\\sfinanciera)',text)[0][-1] #|(que\\sterminaron) #(anos|ano\\sterminado)
            span = re.search('((por)\\s(los|el)\\s(anos|ano)\\s(terminados|terminado))|(situacion\\sfinanciera)',text).span()[0] #|(que\\sterminaron) #(anos|ano\\sterminado)
            aux = text[span:span+130]
            list_ = aux.split(' ')
            result = func_tranform_text(list_,name,type_)
            return result
        except:
            return ('np')

def func_tranform_text(list_,name, type_):
    list_r = []
    if type_ == 'utilidadBruta':
        try:
            b = ' '.join(list_)
            span2 = re.search('\\sotros\\s|\\sgastos|\\sgasto|\\sen|\\soperacional|\\scostos',b).span()[0]
            b[:span2]
            list_ = b[:span2].split(' ')
            for x in list_:
                if x.replace('.','').replace(',','').replace('(','').replace(')','').isdigit():
                    if len(x)>4 and x!='otros':
                        list_r.append(x.replace('(','').replace(')',''))
        except:
            for x in list_:
                if x.replace('.','').replace(',','').replace('(','').replace(')','').isdigit():
                    if len(x)>4 and x!='otros':
                        list_r.append(x.replace('(','').replace(')',''))
    
    elif type_ == 'fecha':
        days = [str(x) for x in range(1,32)]
        anios = [str(x) for x in range(2015,2020)]
        months = ['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre']
        v_date = days+months+anios
        try:
            b = ' '.join(list_)
            span2 = re.search('(ingresos\\spor|de\\sventas|actividades)|((expresadas|expresados|expresado)\\sen\\s(miles|millones)\\sde\\s(pesos|dolares))|(intereses)|(ingresos)|(efectivo)|(utilidad\\sneta)|(operaciones\\scontinuadas)|(activo)',b).span()[1]
            list_ = b[:span2].split(' ')
            for x in list_:
                if x in v_date:
                    list_r.append(x)
        except:
            for x in list_:
                if x in v_date:
                    list_r.append(x)
    return {'etiqueta':name, 'val':pd.unique(list_r)}

def func_data(data,type_):
    flag_=[]
    if type_ == 'utilidadBruta':
        for x,y in data:
            if str(y)!='np':
                aux=0
                for z in y['val']:
                    if z.strip() in x or y['etiqueta'] in x.lower():
                        aux= aux + 1
                if aux >= 1:
                    flag=1
                else:
                    flag=0
            else:
                flag = 0
            flag_.append(flag)
            
    elif type_=='fecha':
        for x,y in data:
            if str(y)!='np':
                b = y['val']
                aux = len(set(b).intersection(set(x.lower().split(' '))))
                if aux >= 1:
                    flag=1
                else:
                    flag=0
            
            flag_.append(flag)
    return flag_

def func_utilidadBruta(data):
    df = data.groupby(['n_doc']).Text.apply(lambda x: ' '.join(x)).reset_index()
    df['utilidadBruta'] = df.Text.map(lambda x: func_extract_text(x,'utilidadBruta'))
    data= data.merge(df[['n_doc','utilidadBruta']], how='left', on='n_doc')
    aux_utilidad = list(zip(data.Text, data.utilidadBruta))
    data['UtilidadBruta'] = func_data(aux_utilidad,'utilidadBruta')
    utilidad = data.utilidadBruta
    data = data.drop('utilidadBruta',axis=1)
    return utilidad,data

def func_fecha(data):
    df = data.groupby(['n_doc']).Text.apply(lambda x: ' '.join(x)).reset_index()
    df['fecha'] = df.Text.map(lambda x: func_extract_text(x,'fecha'))
    data = data.merge(df[['n_doc','fecha']], how='left', on='n_doc')
    aux_fecha = list(zip(data.Text, data.fecha))
    data['Fecha'] = func_data(aux_fecha,'fecha')
    fecha = data.fecha
    data = data.drop('fecha',axis=1)
    return fecha,data

def fecha(data):
    texto=" ".join(data["Text"].values)
    texto=texto.lower()
    año = []
    for x in range(21):
        x_ = str(x).zfill(2)
        año.append(f'20{x_}')
    list_fecha= fecha_lista = ['enero', 'febrero', 'marzo', 'abril', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']+año
    lista_aux = []
    for x in list_fecha:
        if x in texto:
            lista_aux.append(x)
    try:
        data["fecha"] = data["Text"].map(lambda x:(find(x,lista_aux))*1)
        fecha_final = [x for x in data[data['fecha']==1]['Text'].unique()]
    except:
        data['fecha'] = 0
        texto_fecha = []
    return fecha_final,data


def interpretador_inteligente(path_pdf,path_save):
    
    
    name=os.path.basename(path_pdf)
    name=name[:name.find(".")]
    images = convert_from_path(path_pdf)
    images_list=[]

    #os.makedirs(path_images)
    #print(path_images)
    for ima in range(len(images)):
        #ftp.storbinary(f"img_{ima}.png", temp.getvalue())
        #print(os.path.join(path_images,f"img_{ima}.png"))
        
        images[ima].save(os.path.join(path_save,f"img_{ima}.png"))
        
    images=glob(os.path.join(path_save,"**.png"))
    images=natsorted(images)
    n_doc=1
    data=hackaton(images,n_doc,ac_key,s_key)
    
    utilidad_neta_lista,data=utilidad_neta(data)
    unidad_medida_list,data=unidad_medida(data)
    costo_ventas_lista,data=costo_ventas(data)
    caja_bancos_lista,data=caja_bancos(data)
    ventas_lista,data=ventas(data)
    patrimonio_lista,data=patrimonio(data)
    total_activo_lista,data=total_activo(data)
    total_pasivo_lista,data=total_pasivo(data)
    utilidad_operacional_lista,data=utilidad_operacional(data)
    func_utilidadBruta_lista,data=func_utilidadBruta(data)
    func_fecha_lista,data=fecha(data)

    data_data=pd.DataFrame({"Documento":[f"Documento_{1}"],
                           "Unidad Medida":unidad_medida_list,
        #"Fecha":["|".join(func_fecha_lista)],
        "Fecha":["|".join(func_fecha_lista)],
                  "Caja y Bancos":["|".join(caja_bancos_lista)],
                  "Total Activo":["|".join(total_activo_lista)],
                  "Total Pasivo":["|".join(total_pasivo_lista)],
                  "Total Patrimonio":["|".join(patrimonio_lista)],
                  "Ventas":["|".join(ventas_lista)],
                  "Costo Ventas":["|".join(costo_ventas_lista)],
                  #"Utilidad Bruta":["|".join(func_utilidadBruta_lista)],
                  "Utilidad Bruta":"",
                  "Utilidad Operacional":["|".join(utilidad_operacional_lista)],
                  "Utilidad Neta":["|".join(utilidad_neta_lista)],
                 })
    images=glob(os.path.join(path_save,"**.png"))
    [os.remove(ima) for ima in images]
    data_data.reset_index(drop=True,inplace=True)
    data_data.to_csv(os.path.join(path_save,"doc.csv"),index=False)
    return data_data