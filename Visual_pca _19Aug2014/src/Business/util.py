'''
Created on Mar 29, 2013

@author: sob016

'''
import pandas as pd
import numpy as np
import DataAccess
from DataAccess.data import MicroArray, ProbSet, Gen
from string import split
from DataAccess.PCA import PCA, Batch
from Business.pca_algurithm import PCA_Algorithm 



def readPhenotypesFromCSVFile_pd(filename):
    df = pd.read_csv(filename)
    phenotypes = list(df.columns)
    phenotypes[0]='None'
    print(phenotypes)
    pheno_dict={}
    pheno_dict['None'] = ['None']
    #pheno_dict[phenotypes[0]].append('') 

    for i in range(1,len(df.columns)):
        pheno_dict[df.columns[i]]=[]
        #a=list(set(list(df[df.columns[i]])))
        a = df[df.columns[i]].unique().tolist()
        if isinstance(a[0],(float)):
            for j in range(len(a)):
                #print(j)
                pheno_dict[df.columns[i]].append(str(a[j]))
        elif isinstance(a[0], long):
            for j in range(len(a)):
                #print(j)
                pheno_dict[df.columns[i]].append(str(a[j]))
        else: 
            pheno_dict[df.columns[i]]=a 
            
        #print (df.columns[i],pheno_dict[df.columns[i]])
    #return phenotypes[1:], pheno_dict
    return phenotypes, pheno_dict    


def readPhenotypesFromCSVFile(fileName):
    file1 = open(fileName)
    line = file1.readline()
    phenotypes = line.strip().split(',')
    dic = {}
    for phenotype in phenotypes:
        dic[phenotype] = [];
    while 1:
        line = file1.readline()
        if line == "":
            break
        parts = line.strip().split(',')
        for i in range(len(parts)):
            if parts[i] in dic[phenotypes[i]]:
                pass
            else:
                dic[phenotypes[i]].append(parts[i])
    print(phenotypes,dic)        
    return phenotypes, dic


def readMicroArrayFromFile(fileName):
    file2 = open(fileName)
    array = MicroArray()
    while 1:
        line = file2.readline()
        if line == "":
            break
        parts = line.strip().split('\t')
        prob = ProbSet(parts[0])
        
        for j in range(len(parts)-2):
            genParams = parts[j+1].split(',')
            print(genParams)
            gen = Gen()
            gen.genName = genParams[0]  
            gen.coromsumName = genParams[1]
            gen.startCodon = genParams[2]
            gen.stopCodon = genParams[3]
            gen.strandDirection = genParams[4]
            prob.addGene(gen)
        array.addProbSet(prob)
    return array


def makeFakeMicroArray():
    array = MicroArray()
    for i in range(10):
        prob = ProbSet(i)
        for j in range(3):
            gen = Gen()
            gen.genName = "genName"+str(i+j)
            gen.coromsumName = "corom_name"+str(i+j)
            gen.startCodon = 0
            gen.stopCodon = 100
            gen.strandDirection = -1
            prob.addGene(gen)    
        array.addProbSet(prob)
    return array



'''def makeFakePCAArray():    
    path = '../NewPCADATA.txt'
    file1 = open(path,'w' )
    pca = PCA_Algorithm()
    for i in range(32):
        batch = Batch()
        batch.number = i//8    #floor divide i by 8              
        batch.type = np.mod(i//2,4)
        batch.comment = 0 
        batch.prescores = np.random.randn(31)
        batch.postscores = np.random.randn(31)
        batch.isSelected = True
        pca.addBatch(batch)
        file1.writelines(str(batch)+'\n')
    return pca'''
            
            
def makeFakePCAArray():    
    path = '..\..\IOdata\NewPCADATA.txt'
    file1 = open(path,'w' )
    pca = PCA()
    for i in range(48):        # 48 samples in 6 batches, each batch includes 8 treatments 
        batch = Batch()
        batch.number = i//8    #floor divide i by 8              
        batch.type = np.mod(i,8)
        batch.comment = 0 
        batch.prescores = np.random.randn(47)
        batch.postscores = np.random.randn(47)
        batch.isSelected = True
        pca.addBatch(batch)
        file1.writelines(str(batch)+'\n')
    return pca            

def makeFakeArray():    
    path = 'c:\pythondata\NewPCADATA.txt'
    #path = '..\..\IOdata\NewPCADATA.txt'
    file1 = open(path,'w' )
    pca = PCA()
    for i in range(48):        # 48 samples in 6 batches, each batch includes 8 treatments 
        batch = Batch()
        batch.number = i//8    #floor divide i by 8              
        batch.type = np.mod(i,8)
        batch.comment = 0
        batch.score = np.random.randn(1000)
        batch.prescores = np.random.randn(47)
        batch.postscores = np.random.randn(47)
        batch.isSelected = True
        pca.addBatch(batch)
        file1.writelines(str(batch)+'\n')
    return pca

def readPCAFromFile(fileName):
    file3 = open(fileName)
    #pca = PCA_Algorithm()
    pca=PCA()
    while 1:
        line = file3.readline()
        if line == "":
            break
        #batch = DataAccess.PCA_Algorithm.Batch()
        batch = DataAccess.PCA.Batch()
        parts = line.strip().split(',')
        batch.number = eval(parts[0]) 
        batch.type = eval(parts[1])
        batch.comment = eval(parts[2])
        batch.prescores = [eval(i) for i in parts[3:26]]
        batch.postscores = [eval(i) for i in parts[26:]] 
        batch.isSelected = True
        pca.addBatch(batch)
    return pca


