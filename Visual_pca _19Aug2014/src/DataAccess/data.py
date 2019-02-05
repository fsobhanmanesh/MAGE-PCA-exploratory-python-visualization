'''
Created on Mar 18, 2013

@author: sob016
'''

class Gen():
    
    def __init__(self):
        self.genName = None
        self.coromsumName = None 
        self.startCodon = None
        self.stopCodon = None
        self.strandDirection  = None
    def __str__(self):
        return str(self.coromsumName)+', '+str(self.startCodon)+', '+str(self.stopCodon)+', '+str(self.strandDirection)
    
        
    
class ProbSet():
    # list of gens
    def __init__(self, id):
        self.gens =[]
        self.probID = id
    def addGene(self, gen):
        self.gens.append(gen)
        
    def __str__(self):
        ret ='ProbID = ' + str(self.probID) + ' ['
        for gen in self.gens:
            ret = ret+'{'+str(gen)+'}, '
        ret+=']'
        return ret

class MicroArray():
    def __init__(self):
        self.probSets = []
    def addProbSet(self, probSet):
        self.probSets.append(probSet)
    def insertProbSet(self, index, probSet):
        self.probSets.insert(index, probSet)
    
    def getProbSetByIndex(self, index):
        return self.probSets[index]
    def getProbSetByID(self, probId):
        for prob in self.probSets:
            if prob.probID == probId:
                return prob
            
    def __len__(self):
        return len(self.probSets)
    def __str__(self):
        ret = ''
        for prob in self.probSets:
            ret=ret+'\n'+ str(prob)
        return ret
    
