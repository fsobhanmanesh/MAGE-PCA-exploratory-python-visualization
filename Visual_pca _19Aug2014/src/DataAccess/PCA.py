'''
Created on Mar 26, 2013

@author: sob016

'''

class PCA:
    nums = 60       # Upper limit on no of Principal Components
    def __init__(self):
        self.batchs = []
        
    def addBatch(self, batch):
        self.batchs.append(batch)
        
    def insertProbSet(self, index, batch):
        self.probSets.insert(index, batch)
    
    def getBatchByIndex(self, index):
        return self.batchs[index]
            
    def __len__(self):
        return len(self.batchs)
    
    def __str__(self):
        ret = ''
        for batch in self.batchs:
            ret=ret+"\n"+ str(batch)
        return ret


class Batch:
    def __init__(self):
        self.number = 0
        self.type = 0
        self.comment = None
        self.prescore = []
        self.postscore = []
        self.isSelected = False

    def __str__(self):
        
        ret = str(self.number)
        ret = ret+ "," + str(self.type)
        ret = ret+ "," + str(self.comment)
        for i in range(len(self.prescores)):
            ret = ret + "," + str(self.prescores[i])
        #ret = ret+ "  " + str(self.prescores)
        #ret = ret+ "  " + str(self.postscores)
        for i in range(len(self.postscores)):
            ret = ret + "," + str(self.postscores[i])
        return ret