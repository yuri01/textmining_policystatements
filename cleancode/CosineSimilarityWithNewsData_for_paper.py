# -*- coding: utf-8 -*-
"""
Created on Wed May 24 23:25:17 2017

@author: Ri
"""

from konlpy import data ###how to update user dictionary
from konlpy.tag import Kkma, Hannanum
from konlpy.utils import pprint
from collections import Counter
import pandas as pd
import numpy as np
import os
from scipy.spatial.distance import cosine
import matplotlib.pyplot as plt

os.getcwd()
os.chdir("C:/Users/Ri/Dropbox/paper/python_result")
h = Hannanum()  #한나눔 사전(카이스트)
k = Kkma()  #꼬꼬마형태소 분석기(서울대 IDS)


def mergingNews(filepath):
    news=pd.DataFrame()   
    for filename in os.listdir(filepath):               
        print(filename)
        loc = filepath + '/' + filename 
        f = pd.read_csv(loc, encoding='UTF8')
        f['datetime']=f['datetime'].apply(lambda x: x[:10])
        f['body']=f['body'].map(lambda x: x.replace(u"// flash 오류를 우회하기 위한 함수 추가 function _flash_removeCallback() {}",""))
        f['contents']=f['title'].map(str)+"/"+f['body']
        f['filename']=filename[:-4]
        news=news.append(f)
#        news.to_csv("news.csv")
    news_unique=news.drop_duplicates(subset='url',keep='first')
    
    return news_unique

      
def mergingStatements(path):
    statements=pd.DataFrame({'Contents':[]})
    for filename in os.listdir(path): 
#        print(filename)
        loc = path + '/' + filename 
        f = open(loc, 'rt',encoding='UTF8')
        contents = f.read()
        new_contents=contents.replace("□","")      
        new_contents=new_contents.replace(u"“한국은행","")
        new_contents=new_contents.replace(u"정책기획국","")
        new_contents=new_contents.replace(u"정책총괄팀","")
        new_contents=new_contents.replace(u"차장","")
        new_contents=new_contents.replace(u"통화정책국","")
        new_contents=new_contents.replace(u"MERS","")
        f.close()  
               
        statements.ix[(filename[:4])]=new_contents        
#        print(statements)
        
    return statements


def buildMonthlyTDM(newsDB,statements,month):
    #Prepare contents data
    monthlyData=pd.DataFrame(columns=['source','month','contents'])
    
    statements['month']=statements.index
    stat=statements.loc[statements['month']==month]
    stat.loc[stat.index,'source']='Statement'+'_'+month
    stat.columns=['contents','month','source']
    monthlyData=monthlyData.append(stat)
        
    news=newsDB.loc[newsDB['month']==month]
    news=news[['id','month','contents']]
    news.columns=['source','month','contents']
    monthlyData=monthlyData.append(news)
    
    monthlyData=monthlyData.reset_index()
    
    #Extract nouns and make TDM
    tdm_f=pd.DataFrame({'Term':[]})
    for i in range(len(monthlyData)):
        body=monthlyData.ix[i]['contents']
        nouns = k.nouns(body) #use Hannanum dictionary
        count = Counter(nouns)
        tdm = pd.DataFrame.from_dict(count, orient='index').reset_index()
        tdm = tdm.rename(columns={'index':'Term', 0:monthlyData.ix[i]['source']})
        tdm_f=pd.merge(tdm_f,tdm, on='Term', how='outer')
        tdm_f=tdm_f.fillna(0)

    tdm_f=tdm_f.sort(['Term'])   
    tdm_f['isAlphabet']=pd.Series(tdm_f.Term.str.isalpha(),index=tdm_f.index)  #remove numbers
    tdm_f=tdm_f.ix[(tdm_f['isAlphabet']==True)]
    del tdm_f['isAlphabet']
    
    tdm_f.index=list(tdm_f['Term']) #Term을 인덱스로 만듬
    tdm_f=tdm_f[tdm_f.index.map(len) >1] #remove one sylabble
    del tdm_f['Term']
    
    return tdm_f

#Cosine similarity_cross-sectional
def cosineSimilarity_cross(tdm,month):
    
    cosineSim=pd.DataFrame()
    for i in range((len(tdm.columns)-1)):
        print(i)
        col_name=month+"_"+str(i)
        res=1-cosine(tdm.iloc[:,0],tdm.iloc[:,i+1])
        res=pd.Series(res)
        cosineSim[col_name]=res
    mean=cosineSim.mean(axis=1)
    std=cosineSim.std(axis=1)
                
    return mean, std

#Cosine similarity_cross-sectional for individual data points
def datapoints_cosineSimilarity_cross(tdm,month):
    
    cosineSim=pd.DataFrame()
    for i in range((len(tdm.columns)-1)):
        print(i)
        col_name=month+"_"+str(i)
        res=1-cosine(tdm.iloc[:,0],tdm.iloc[:,i+1])
        res=pd.Series(res)
        cosineSim[col_name]=res                
    return cosineSim

###################################3
#1. Read all news data
newsPath="C:/Users/Ri/Dropbox/paper/R_crawling_result"
newsDB=pd.DataFrame()
for foldername in os.listdir(newsPath):
    print(foldername)
    filepath=newsPath+"/"+foldername
    news=mergingNews(filepath)
    newsDB=newsDB.append(news)
newsDB=newsDB.reset_index()
newsDB['id']=newsDB.index
newsDB['month']=newsDB['datetime'].apply(lambda x: x[2:4]+x[5:7])    
newsDB.to_csv('newsDB.csv')

#2. Get Policy statments
statementPath='C:/Users/Ri/Dropbox/paper/bok_monetary_policy_kor_txt'      
statements=mergingStatements(statementPath)
statements.to_csv('statements.csv')

#3. Build monthly TF-IDF by using both news and statements and calculate cosine similarity

periods=statements.index
cosine_sim=pd.DataFrame(columns=['month','mean_similarity','std_similarity'])
for j in range(len(periods)):
    print(periods[j])
    month=periods[j]
    tdm=buildMonthlyTDM(newsDB,stat,month)      
    mean, std = cosineSimilarity_cross(tdm,month)
    res={'month':month,'mean_similarity':mean, 'std_similarity':std}
    res=pd.DataFrame(res)
    cosine_sim=cosine_sim.append(res)
    
cosine_sim.columns= ['mean_similarity','month','std_similarity']
cosine_sim.index=cosine_sim['month']
del cosine_sim['month']
cosine_sim.to_csv("cosine_sim_mean.csv")


#3-1. For each data points
periods=statements.index
cosine_sim_each=pd.DataFrame(columns=['month','similarity'])
for j in range(len(periods)):
    print(periods[j])
    month=periods[j]
    tdm=buildMonthlyTDM(subDB,stat,month) 
    res=datapoints_cosineSimilarity_cross(tdm,month)
    res=res.transpose()
    res.loc[res.index,'month']=month
    res=res.rename(columns={0:"similarity"})
    cosine_sim_each=cosine_sim_each.append(res)
cosine_sim_each.to_csv("cosine_sim_each_sub.csv")


#################################
