#GENERA UN BOSQUE RECUBRIDOR SOBRE EL ESQUEMA MULTIPLICADO DEL GRAFO CON ORIGEN EN EL TIPO DE NODO A CLASIFICAR

import random
import json
from py2neo import neo4j
import numpy as np
import math
from id3 import id3
from ete2 import Tree

class rf:
    arboles = []
    tipo = ""
    target = ""
    vtarget = ""
    nnodes = 0
    ntrels = 0
    graph_db = ""
    maxdepth = 0

    def __init__(self,gr,nodes,tipo,target,vtarget,narboles,nnodes,ntrels,maxdepth,exrel,umbral):
        self.graph_db = gr
        self.tipo = tipo
        self.target = target
        self.vtarget = vtarget
        self.nnodes = nnodes
        self.ntrels = ntrels
        self.maxdepth = maxdepth
        
        TC = neo4j.CypherQuery(self.graph_db, "MATCH (a)-[r]->(b) WHERE labels(a) <> [] AND labels(b) <> [] RETURN DISTINCT head(labels(a)) AS This, type(r) as To, head(labels(b)) AS That limit "+str(self.ntrels)).execute()
        print "Tipos de aristas cargadas: "+ str(len(TC.data)) + " elementos."
        while(len(self.arboles)<narboles):  
            tempn = nodes#random.sample(nodes , ( random.randint(1,len(nodes)/2))) + (random.sample(set(nodes[-len(nodes)/2:]), random.randint(1,len(nodes)/2)))
            tempr = random.sample(set(TC.data), random.randint(3,len(TC)))
            #tempr = TC.data
            arbol = id3(gr,target,vtarget,tempr)
            res = arbol.execute(tempn,"match (n:"+self.tipo+")",self.tipo,self.maxdepth,-999,999,exrel,umbral,target)
            tab = []
            for l in res.get_leaves():
                a,b,c = l.name.partition("*")
                tab.append(a) 
            entra = True
            for c in self.arboles:
               if entra == True:
                   if self.checkequals(c.arbol,res):
                    entra = not self.checkequals(c.arbol,res)
            if len(res.get_edges()) > 2 and len(set(tab)) > 1 and entra:    
                print "Arbol "+str(len(self.arboles)+1)+"("+str(len(tempn))+" nodos):"
                print res.get_ascii(show_internal=True)      
                self.arboles.append(arbol)
       
    def train(self):
        print self

    def test(self,nodes):
        aciertos = 0
        for h in nodes:
            votacion = []
            for a in self.arboles:
                a,b,c = str(a.clasif(a.arbol,h,"match (n) ")).partition("*")
                votacion.append(a)
            maximo = max(set(votacion), key=votacion.count)
            if (maximo[6:] == h[self.target]) or (h[self.target] != self.vtarget and maximo[6:] != self.vtarget):
                #print "acierto"
                aciertos = aciertos + 1
            #print "El "+self.tipo+ " es " + h[self.target] + " y ha sido clasificado como " + maximo
        print "elementos en el conjunto de prueba:" + str(len(nodes))
        print "porcentaje de acierto: " + str(aciertos*100/len(nodes))+"%"
    

    def checkequals(self,t1,t2):
        if(len(t1.children) == len(t2.children)):
            if(len(t1.get_leaves()) == 1):

                for l in t1.children[0]:
                    a,b,c = l.name.partition("*")
                for k in t2.children[0]:
                    x,b,c = k.name.partition("*")
                if(a==x):
                    return True
                else:
                    return False
            else:
                q,w,e = str(t1).partition("*")
                q1,w,e = str(t2).partition("*")
                if (q == q1):
                    return self.checkequals(t1.get_children()[0],t2.get_children()[0]) and self.checkequals(t1.get_children()[1],t2.get_children()[1])
                else:
                    return False
        else:
            return False
