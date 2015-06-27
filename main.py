from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
import pandas as pd
import random
import json
from py2neo import neo4j
import numpy as np
from id3 import id3
from rf import rf
from collections import Counter
from ete2 import Tree
from random import randint
import math


neo4j.authenticate("http://localhost:7474", "neo4j", "pytpytpyt")
graph_db = neo4j.GraphDatabaseService("http://neo4j:pytpytpyt@localhost:7474/db/data/")

tipo = "personnage"
target = "nationalite"
vtarget = "Romain"
nnodes =400


cuenta1 = neo4j.CypherQuery(graph_db, "match (n:"+tipo+") where n."+target+" = '"+vtarget+ "' return count(n) as cuenta LIMIT "+str(nnodes)).execute()
cuenta2 = neo4j.CypherQuery(graph_db, "match (n:"+tipo+") where n."+target+" <> '"+vtarget+ "' return count(n) as cuenta LIMIT "+str(nnodes)).execute()
for c in cuenta1:
    valor1 = c.cuenta
for c in cuenta2:  
    valor2 = c.cuenta

if valor1 < valor2:
    mini = valor1
else:
    mini = valor2
if mini> nnodes:
    mini = nnodes/2
nodes1 = neo4j.CypherQuery(graph_db, "match (n:"+tipo+") where n."+target+" <> '"+vtarget+ "' return n,id(n) as id,n."+target+" as "+target+" LIMIT "+str(mini)+" UNION ALL "+"match (n:"+tipo+") where n."+target+" = '"+vtarget+ "' return n,id(n) as id,n."+target+" as "+target+" LIMIT "+str(mini)).execute()
print "Conjunto de nodos cargado: "+str(len(nodes1.data))+" elementos."
nodestrain = []
nodestest = []
for z in nodes1:
    if random.randint(0,5)>1:
        nodestrain.append(z)
    else:
        nodestest.append(z) 
print "Conjunto de entrenamiento: "+str(len(nodestrain))+" elementos."
print "Conjunto de prueba: "+str(len(nodestest))+" elementos."
#graph, tipo, target, vtarget, narboles, nnodos, nrels, maxdepth, exrels,umbral
rf = rf(graph_db,nodestrain,tipo,target,vtarget,1,nnodes,100,2,[],0   )
rf.train()

rf.test(nodestest) 

np.save("rf2", rf)

