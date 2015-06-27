#GENERA UN ARBOL RECUBRIDOR SOBRE EL ESQUEMA MULTIPLICADO DEL GRAFO CON ORIGEN EN EL TIPO DE NODO A CLASIFICAR
import ast
import random
import json
from py2neo import neo4j
import numpy as np
import math
from ete2 import Tree
from sklearn.cluster import MeanShift, estimate_bandwidth
from sklearn.datasets.samples_generator import make_blobs

class id3:
    target = ""
    graph_db = ""
    vtarget = ""
    arbol  = ""
    TC = ""

    def __init__(self,gr,target,vtarget,TC):
        self.graph_db = gr
        self.target = target
        self.vtarget = vtarget
        self.TC  =TC
       
    def execute(self,nodes,path1,node,c,maximo,maxinf,exrel,umbral,padre):
        a,b = path1.rsplit(':', 1)
        if (a[-1:] != "n"):
            path = a+"d:"+b
            cyprop = "/(count(distinct(d))+1)"
        else:
            path = path1
            cyprop = ""
        TC = self.TC
        graph_db = self.graph_db
        if len(nodes) == 0: 
            self.arbol = Tree("("+str(padre)+"*"+str(len(nodes))+");")
            return Tree("("+str(padre)+"*"+str(len(nodes))+");")
 
        if not any(n[self.target] == self.vtarget for n in nodes):
            self.arbol = Tree("(not "+str(self.vtarget)+"*"+str(len(nodes))+");")
            return Tree("(not "+str(self.vtarget)+"*"+str(len(nodes))+");")
        if not any(n[self.target] != self.vtarget for n in nodes):
            self.arbol = Tree("("+str(self.vtarget)+"*"+str(len(nodes))+");")
            return Tree("("+str(self.vtarget)+"*"+str(len(nodes))+");")
        if (c <= 0 or maxinf == 0 or maxinf <=  umbral or TC == [] or len(nodes) < 2):
            temp = []
            for n in nodes:
                if n[self.target] == self.vtarget:
                    temp.append(self.vtarget)
                else:
                    temp.append("not "+self.vtarget)
            self.arbol = Tree("("+str(max(set(temp), key=temp.count))+"*"+str(len(nodes))+");")
            return Tree("("+str(max(set(temp), key=temp.count))+"*"+str(len(nodes))+");")
        else:
            posibles = ""
            cont = 0
            while (len(posibles) == 0 and cont < 10):
                cont += 1
                posibles = "MATCH (a)-[r]->(b) WHERE labels(a) <> [] AND labels(b) <> [] AND ( "
                for t in TC:
                    posibles = posibles + "type(r) = '"+t.To+"' OR "
                posibles = str(posibles[:-3]) + ") AND ("
                for z in random.sample(nodes, random.randint(1,(len(nodes)/2))):
                    posibles += "id(a) = " + str(z.id) + " OR "
                posibles = str(posibles[:-3]) + " ) RETURN DISTINCT head(labels(a)) AS This, type(r) as To, head(labels(b)) AS That limit "+str(len(TC))+" UNION ALL MATCH (a)<-[r]-(b) WHERE labels(a) <> [] AND labels(b) <> [] AND ("
                for t in TC:
                    posibles = posibles + "type(r) = '"+t.To+"' OR "
                posibles = str(posibles[:-3]) + ") AND ("
                for z in random.sample(nodes, (random.randint(1,len(nodes)/2))):
                    posibles += "id(a) = "+str(z.id)+" OR "
                posibles = str(posibles[:-3]) + " ) RETURN DISTINCT head(labels(b)) AS This, type(r) as To, head(labels(a)) AS That limit "+str(len(TC))
                posibles = neo4j.CypherQuery(self.graph_db, posibles).execute()
            if cont >= 10 or len(posibles)==0 or len(nodes)<15:
                temp = []
                for n in nodes:
                    if n[self.target] == self.vtarget:
                        temp.append(self.vtarget)
                    else:
                        temp.append("not "+self.vtarget)
                self.arbol = Tree("("+str(max(set(temp), key=temp.count))+"*"+str(len(nodes))+");")
                return Tree("("+str(max(set(temp), key=temp.count))+"*"+str(len(nodes))+");")
            maxinf = -1000
            tc_c = posibles[0]

            for tc in posibles:#random.sample(posibles, random.randint(1,(len(posibles)))):
                cluster_centers = []
                if((tc.This == node or tc.That == node) and tc.To not in exrel):
                    if(tc.That == node):
                        consulta = path + "<-[:"+tc.To+"]-(e:"+tc.This+")"
                    else:
                        consulta = path + "-[:"+tc.To+"]->(e:"+tc.That+")"
                    if self.relValida(graph_db,consulta,nodes,cyprop) :
                        cluster_centers, group = self.centers_y_clusters(graph_db,nodes,consulta,cyprop)

                        newentropy = 0
                        if (len(cluster_centers))> 0:
                            for idx,v in enumerate(cluster_centers):
                                newentropy += (len(group[idx])/(len(nodes)))*self.entropy(group[idx])
                            information =  self.entropy(nodes) - newentropy
                            temp = []
                            for n in nodes:
                                if n[self.target] == self.vtarget:
                                    temp.append(self.vtarget)
                                else:
                                    temp.append("not "+self.vtarget)
                            self.arbol = Tree("("+str(max(set(temp), key=temp.count))+"*"+str(len(nodes))+");")
                            return Tree("("+str(max(set(temp), key=temp.count))+"*"+str(len(nodes))+");")                        

                            if (information >= maxinf):
                                maxinf = information 
                                tc_c = tc
            if maxinf > maximo:
                maximo = maxinf
            if (tc_c.That == node):
                consultacon = path + "<-[:"+tc_c.To+"]-(e:"+tc_c.This+")"
                consultasin = path1 + "<-[:"+tc_c.To+"]-(:"+tc_c.This+")"                
                label = "<-[:"+tc_c.To+"]-(:"+tc_c.This+") "
                nextnode = tc_c.This
            else:   
                consultacon = path + "-[:"+tc_c.To+"]->(e:"+tc_c.That+")"
                consultasin = path1 + "-[:"+tc_c.To+"]->(:"+tc_c.That+")"
                nextnode = tc_c.That
                label = "-[:"+tc_c.To+"]->(:"+tc_c.That+")"
            group = []
            neg = []
            suma = 0
            for n in nodes:
                tiene = neo4j.CypherQuery(graph_db, consultacon+" where id(n) ="+str(n.id)+" return count(distinct(e))"+cyprop+" as cuenta").execute()

                for r in tiene:
                    todo.append([r.cuenta])
                    rr.append(r.cuenta)
            ms = MeanShift(bin_seeding=True)
            ms.fit(np.asarray(todo))
            labels = ms.labels_
            cluster_centers = sorted(ms.cluster_centers_,key=lambda x: x[0])
            for idx,cl in enumerate(cluster_centers):
                cluster_centers[idx] = round(float(cl[0]),3)
            for u in cluster_centers:
                group.append([])
            for n in nodes:
                tiene = neo4j.CypherQuery(graph_db, consultacon+" where id(n) ="+str(n.id)+" return count(distinct(e))"+cyprop+" as cuenta").execute().data
                for r in tiene:
                    valor = r.cuenta
                    for idx,v in enumerate(cluster_centers):
                        if idx == 0:
                            temp1 = -9999
                        else:
                            temp1 = (cluster_centers[idx-1] + cluster_centers[idx])/2
                        if idx == len(cluster_centers) - 1:
                            temp2 = 99999
                        else:
                            temp2 = (cluster_centers[idx+1] + cluster_centers[idx])/2
                        if temp1 <= valor < temp2:
                            group[idx].append(n)
            temp = []
            for n in nodes:
                if n[self.target] == self.vtarget:
                    temp.append(self.vtarget)
                else:
                    temp.append("not "+self.vtarget)
            padre1 = str(max(set(temp), key=temp.count))
            t = Tree()
            t.name=label+" "+str(cluster_centers).replace(". ",".0").replace(" ", "").replace("[","").replace("]","").replace("\n",",")
            t = t.search_nodes(name=label+" "+str(cluster_centers).replace(". ",".0").replace(" ", "").replace("[","").replace("]","").replace("\n",","))[0]
            if umbral < 0:
                umbral = umbral - maxinf
            else:
                umbral = 0
            for idx,v in enumerate(cluster_centers):
                t.add_child(self.execute(group[idx],consultasin,str(nextnode),c-1,maximo,maxinf,[],umbral,padre1))
            self.arbol = t
            if maxinf > umbral and maxinf != 0:
                return t
            else:
                temp = []
                for n in nodes:
                    if n[self.target] == self.vtarget:
                        temp.append(self.vtarget)
                    else:
                        temp.append("not "+self.vtarget)
                 
                self.arbol = t
                return Tree("("+str(max(set(temp), key=temp.count))+"*"+str(len(nodes))+");")

    def entropy(self,nodes):
        if(len(nodes)>0):
                result = 0
                pos = 0.000000001
                neg = 0.000000001
                for n in nodes:
                    if n[self.target] == self.vtarget:
                        pos +=1
                    else:
                        neg +=1
                parcial = 0.000000001
                result = result + (pos / len(nodes) ) * math.log(pos / len(nodes) ,2)
                result = result + (neg / len(nodes) ) * math.log(neg / len(nodes) ,2)
                return - float(result)
        else:
            return  math.log(1,2)

    def clasif(self,s,node,path1):
        if ":" in path1:
            a,b = path1.rsplit(':', 1)
            if (a[-1:] != "n"):
                path = a+"d:"+b
                cyprop = "/(count(distinct(d))+1)"
            else:
                path = path1
                cyprop = ""
        else:
            path = path1
            cyprop = ""
        graph_db = self.graph_db
        if len(s.get_children())==1:
            return s
        else:
            head, sep, limite = s.name.partition('(')
            a,b,c = limite.partition(')')            
            consulta = head+sep+a+b
            tiene = neo4j.CypherQuery(graph_db, path+head+sep+"e"+a+b+" where id(n) ="+str(node.id)+" return count(distinct(e))"+cyprop+" as cuenta").execute().data
            for r in tiene:
                valor = r.cuenta
            c = c.replace(". ",".0").replace(" ", "").replace("[","").replace("]","")
            c = c.split(',')
            for z in c:
                z = float(z)
            for idx,v in enumerate(set(c)):
                if idx == 0:
                    temp1 = -9999
                else:
                    temp1 = (float(c[idx-1]) + float(c[idx]))/2
                if idx == len(c) - 1:
                    temp2 = 99999
                else:
                    temp2 = (float(c[idx+1]) + float(c[idx]))/2
                if temp1 <= valor < temp2:
                    return self.clasif(s.children[idx],node,path1+consulta)

    def relValida(self,graph_db,consulta,nodes,cyprop):
        rr = []
        for n in nodes:
            tiene = neo4j.CypherQuery(graph_db, consulta+" where id(n) ="+str(n.id)+" return count(distinct(e))"+cyprop+" as cuenta").execute()
            for r in tiene:
                rr.append(r.cuenta)
        if(len(set(rr))> 1 ):
            return True
        else:
            return False
    def centers_y_clusters(self,graph_db,nodes,consulta,cyprop):
        group = []
        todo = []
        rr = []
        for n in nodes:
            tiene = neo4j.CypherQuery(graph_db, consulta+" where id(n) ="+str(n.id)+" return count(distinct(e))"+cyprop+" as cuenta").execute()
            for r in tiene:
                todo.append([r.cuenta])
                rr.append(r.cuenta)
            
        ms = MeanShift(bin_seeding=True)
        ms.fit(np.asarray(todo))
        labels = ms.labels_
        cluster_centers = sorted(ms.cluster_centers_ , key=lambda x: x[0])
        for idx,cl in enumerate(cluster_centers):
            cluster_centers[idx] = float(cl[0])
        for u in cluster_centers:
            group.append([])
        for n in nodes:
            tiene = neo4j.CypherQuery(graph_db, consulta+" where id(n) ="+str(n.id)+" return count(distinct(e))"+cyprop+" as cuenta").execute()
            for r in tiene:
                valor = r.cuenta
            for idx,v in enumerate(cluster_centers):
                if idx == 0:
                    temp1 = -9999
                else:
                    temp1 = (cluster_centers[idx-1] + cluster_centers[idx])/2
                if idx == len(cluster_centers) - 1:
                    temp2 = 99999
                else:
                    temp2 = (cluster_centers[idx+1] + cluster_centers[idx])/2
                if temp1 <= valor < temp2:
                    group[idx].append(n)
        return cluster_centers, group
