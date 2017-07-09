# -*- coding: utf-8 -*-
"""
Created on Sat Apr 29 15:57:19 2017

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
from datetime import datetime 
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import Normalizer

os.getcwd()
os.chdir("C:/Users/Ri/Dropbox/paper/python_result")
h = Hannanum()  #한나눔 사전사용

#kkma=Kkma()


#Read text files and generate term documnet matrix(tdm)
def buildTDM(path):
    
    tdm_f=pd.DataFrame({'Term':[]})
    
    for filename in os.listdir(path):        
        
        #Read text files
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
        
        #Extract nouns and build tdm
        nouns = h.nouns(new_contents) #use Hannanum dictionary
        count = Counter(nouns)
        print(filename)
        tdm = pd.DataFrame.from_dict(count, orient='index').reset_index()
        tdm = tdm.rename(columns={'index':'Term', 0:filename[0:4]})
        tdm_f=pd.merge(tdm_f,tdm, on='Term', how='outer')
       
#        print(tdm_f)
        tdm_f=tdm_f.fillna(0)
        tdm_f=tdm_f.rename(columns={'count_y':filename[0:4]})
#        print(tdm_f)


    tdm_f=tdm_f.sort(['Term'])
    tdm_f['isAlphabet']=pd.Series(tdm_f.Term.str.isalpha(),index=tdm_f.index)  #remove numbers
    tdm_f=tdm_f.ix[(tdm_f['isAlphabet']==True)]
    del tdm_f['isAlphabet']
    
    tdm_f.index=list(tdm_f['Term']) #Term을 인덱스로 만듬
    tdm_f=tdm_f[tdm_f.index.map(len) >1] #remove one sylabble
    del tdm_f['Term']
    
    return tdm_f

#Weighting words: Term freqency-inverse document frequency
def TfIdf(tdm):
    n = len(tdm.columns) # number of documents
    n_t = (tdm.iloc[:,:]>0).sum(1)  # number of documents including t term
    global_t=np.log10(n/n_t) #global term weights
    global_t=global_t.to_frame()
    
    max_t=tdm.iloc[:,:].max(axis=0) #max number of a term in a document
    max_t=max_t.to_frame()
    max_t=max_t.transpose()
    local_td=tdm.iloc[:,:]/max_t.values[0,:] 
     
    numerator=pd.DataFrame(local_td.values*global_t.values,columns=local_td.columns, index=local_td.index)
    
    sumproduct = np.dot(local_td.T,global_t)
    sqrt_sumproduct = np.sqrt(sumproduct)
    sqrt_sumproduct = pd.DataFrame(sqrt_sumproduct.tolist())
    
    tf_idf=pd.DataFrame(numerator.values/sqrt_sumproduct.T.values, columns=numerator.columns,index=numerator.index)

    return tf_idf

#Cosine similarity_time series
def cosineSimilaritybyTime(idf):
    
    cosineSim=pd.DataFrame()
    for i in range((len(idf.columns)-1)):
        cols=idf.columns[i+1]
        date = datetime(year=int('20'+ cols[0:2]),month=int(cols[2:]),day=15)
        res=1-cosine(idf.iloc[:,i],idf.iloc[:,i+1]) 
        res=pd.Series(res)
        cosineSim[date]=res
        
    return cosineSim.T


def topTenScores(tdm):
    
    topTenScores = pd.DataFrame()
    for i in range(len(tdm.columns)):
        top=tdm.iloc[:,i].nlargest(10).to_frame()
        top=topten.reset_index(drop=True)
        topTenScores=pd.concat([topTenScores,top], axis=1)
#        print(topTenScore)

    return topTenScores


def topTenWords(tdm):    
#    termData['Term']=pd.DataFrame(tdm.index)
    topWords = pd.DataFrame()
    for i in range(len(tdm.columns)):
        top=tdm.iloc[:,i].nlargest(10).to_frame()   
        for j in range(len(top.index)):
            top.iloc[j]=top.index[j]
        top=top.reset_index(drop=True)
        topWords=pd.concat([topWords,top], axis=1)

    return topWords



#### init  ######
#1. BUild TDM
path='C:/Users/Ri/Dropbox/paper/bok_monetary_policy_kor_txt'
tdm=buildTDM(path)
tdm.to_csv('result.csv', encoding='utf-8')

totalwordcount=tdm.sum()
date = datetime(year=int('20'+ cols[0:2]),month=int(cols[2:]),day=15)
totalwordcount.to_csv('totalwordcount.csv', encoding='utf-8')
fig=plt.figure()
plt.plot(totalwordcount,linestyle='dashed', color='g', marker='o')

#2. Transform to TF-IDF
Tf_Idf=TfIdf(tdm)
Tf_Idf.to_csv('Tf_Idf.csv',encoding='utf-8')

tdm_audited=pd.DataFrame.from_csv("C:/Users/Ri/Dropbox/paper/python_result/tdm_audit.csv") 
tdm_audited.columns = tdm.columns
Tf_Idf_audited=TfIdf(tdm_audited)
Tf_Idf_audited.to_csv('Tf_Idf_audited.csv',encoding='utf-8')


#3. See top ten words 
topwords=topTenWords(Tf_Idf_audited)
topwords.to_csv('topwords.csv', encoding='utf-8')

#4. Cosine Similarity
cosineSim=cosineSimilaritybyTime(Tf_Idf_audited)
cosineSim.to_csv('cosineSimbyTime.csv')

fig=plt.figure()
ax1=fig.add_subplot(1,1,1)
plt.plot(cosineSim,linestyle='dashed', color='g', marker='o')

