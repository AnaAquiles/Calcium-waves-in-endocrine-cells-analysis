# -*- coding: utf-8 -*-
"""
Created on Tue Jun  5 15:22:57 2018

@author: kirex
"""


##
##
##               Código ARTÍCULO DE REDES

import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import simps
from scipy import signal
from scipy import stats 
from matplotlib import cm
import pandas as pd
import seaborn as sns 


filename="P190617C"
data=np.loadtxt(filename + ".csv",delimiter=',')

#bins = np.loadtxt('P190617bins0.csv', delimiter= ',') 

#coors = np.loadtxt('coordenadasD190617.csv', delimiter= ',') 
#zz = np.loadtxt('BaseDeDatosP190617corrDA.csv', delimiter= ',')

datos=np.array([data[i:i+700] for i in range(0,4900,700)])
datos=np.swapaxes(datos,1,2)  

#Normalization respect the baseline: total of datos - min baseline / min baseline. We considere only the first 50 images of basal activity
def NormF(datos):
    baseline=np.amin(datos[:,:,:700],-1)[:,:,None]          #Hasta dónde se vamos a tomar de la actividad basal; hasta el valor 25     
    return datos/baseline
#Correction of activity cells debleach with linear regress of the first 50 values for each condition
def detrend(datos,window=700):#arreglo indicado para las 300 imágenes,con regresión líneal 
    x=np.arange(0,window)
    x = x[None,:]*np.ones((datos.shape[-2],1))
    x=np.ravel(x)
    slopes=[]
    intercepts=[]
    for dat in datos:
        y = np.ravel(dat[:,:window])
        slope,inter,_,_,_=stats.linregress(x,y)
        slopes.append(slope)
        intercepts.append(inter)
        #-1 is the axis of ROI's
    slopes=np.array(slopes)
    intercepts=np.array(intercepts)
    t=np.arange(0,datos.shape[-1])
    trends=np.array((intercepts)[:,None] + np.array(slopes)[:,None] * t[None,:])
    return datos - trends[:,None,:]
  #direction of filtred the data      
b,a = signal.bessel(3,0.1,btype='lowpass') #grado del filtrado 0.1
datosfilt=signal.filtfilt(b,a,datos,axis=-1)
datosNorm=detrend(NormF(datos))
datosNormFilt=detrend(NormF(datosfilt))
dt=0.2
time=np.arange(0,dt*datosNorm.shape[-1],dt) 



#%%
#    Gráficas de cada célula. Se guardan en la carpeta Origen

ini=6
plt.figure(0,figsize=(12,12))
ppp=8


for ini in range(0,datos.shape[1],ppp):
    for i in range(ppp):
        ax1=plt.subplot2grid((ppp,8),(i,0),colspan=6) 
        for j in range(len(datos)):
            plt.plot(time + max(time)*j,datosNorm[j,i+ini,:],alpha=0.5, c = 'slategray' )
            plt.plot(time + max(time)*j,datosNormFilt[j,i+ini,:], c='dodgerblue')
            _,Ymax=plt.ylim()
        plt.text(50,Ymax*0.95,"ROI %g"%(i+ini),va='top')
        if i!=(ppp-1):
            ax1.set_xticklabels([])
        ax1.tick_params(labelsize='x-small')
        ax1.set_ylim(-0.3,0.50)# disminuímos el tamaño de las letras 
#        ax2=plt.subplot2grid((ppp,8),(i,6))
#        plt.plot(abc[:,i+ini])
#        if i!=(ppp-1):
#            ax2.set_xticklabels([])
#        ax2.tick_params(labelsize='x-small')
        
#        ax2=plt.subplot2grid((ppp,8),(i,7))
#        plt.plot(maxVmin[:,i+ini])
#        if i!=(ppp-1):
#            ax2.set_xticklabels([])
#        ax2.tick_params(labelsize='x-small')
        
#    plt.tight_layout()
    plt.savefig(filename + "-ROIS%g-%g"%(ini,ini+ppp-1) + ".png",dpi=200)

#%%

#     Señales acumuladas
plt.style.use('seaborn-poster')

fig, ax = plt.subplots(figsize=(200,100))


for ini in range(0,datos.shape[1]):
    for j in range(len(datos)):
#        plt.plot(time + max(time)*j,datosNormFilt[j,ini,:], c ='dimgrey')
        ax.set_rasterized(datosNormFilt[j,ini,:].all)
        
ax.set_xlim(0,850)
ax.set_ylim(0,1)
ax.set_xlabel('Time adquisition')
ax.set_ylabel('F-Fmin')


plt.grid(False)    
plt.show() 

#%%


#   RASTER PLOt of each condition 

# RASTER MATPLOTLIB  
 
from matplotlib import pyplot 
 
series = [] 
 
for ini in range(0,datos.shape[1]): 
    for j in range(len(datos)): 
        series.append(datosNormFilt[j,ini,:]) 
 
 
series = np.array(series) 
series = pd.DataFrame(series) 
 
pyplot.matshow(series, interpolation=None, aspect = 'auto', cmap='bone') 
pyplot.colorbar() 
 
 
pyplot.xlabel('Time adquisition') 
pyplot.ylabel('Cells') 
pyplot.yticks(np.arange(0,686,98)) 
pyplot.xticks(np.arange(700,0,)) 
pyplot.show()
 

#%%

#       SELECCIONA EL NÚMERO i= x DE TRATAMIENTO QUE QUIERES GRAFICAR 


i= 1
 #Número de tratamiento
plt.figure(3)
plt.clf()
plt.subplot(321)
plt.plot(datos[i,:,:].T)

plt.subplot(323)
plt.plot(NormF(datos)[i,:,:].T)

plt.subplot(325)
plt.plot(detrend(NormF(datos))[i,:,:].T)
    

plt.subplot(322)
plt.plot(datosfilt[i,:,:].T)

plt.subplot(324)
plt.plot(NormF(datosfilt)[i,:,:].T)

plt.subplot(326)
plt.plot(detrend(NormF(datosfilt))[i,:,:].T)


#%%

#  DISCRIMINACIÓN DE GPOS.CELULARES Y CONTEO DE RESPUESTAS
import pandas as pd
# Delimitación de la señal 
End = (datosNormFilt[:,:,:300]) #límite
Begin = (End[:,:,150:]) #inicio
signals = Begin 

General = simps(signals,axis=-1) #ABC GENERAL                                                                                                                                       

trh = np.array(General[(1,2,3,4),:]) #seleccionar los rois que no tienen respuesta
df = pd.DataFrame(trh)
p = (df.ix[:,df.gt(0).any()]) #Seleccionamos los Rois que responden a TRH
rois = np.array(p.columns) #los convertimos en arreglo              
Rtrh = np.take(trh, (rois), axis=1) #Rois CON respuesta

da = np.array(General[5,:]) #A partir de x= np.std(da), decir da<x
Rda = np.take(da, (rois), axis=0) # igual que Rtrh

Basal = np.array(General[(0),:]) 
rbasal = np.take(Basal, (rois), axis=0) # resp basal de cels responsivas

                
x = np.std(Rda) #A partir de x= np.std(da), decir da<x
da = (Rda<x)
RoiLact = np.array(np.where(da==True)).T  #Rois lactotropos
RoiTir = np.array(np.where(da==False)).T #Rois Tirotropos

TotalCellsRoi = np.union1d(RoiLact,RoiTir)  #AMBOS Tipos celulares ROIS

# Repsuesta cada dósis de TRH y basal, lactotropos 

Bas = np.take(rbasal,RoiLact)
basalLact = np.array(np.where(Bas>0))

Lacto = np.take(Rtrh[0],RoiLact) # en: [] indicar el número de dósis
resplact = np.array(np.where(Lacto>0))

# Repsuesta cada dósis de TRH y basal, tirotropos 
Bas = np.take(rbasal,RoiTir)
basalTiro = np.array(np.where(Bas>0))

Tiro = np.take(Rtrh[0],RoiTir) # en: [] indicar el número de dósis
resptiro = np.array(np.where(Tiro>0))


#%%

#   Construye la gráfica de actividad por región
##          en cada Fase del ciclo: LACTOTROPOS


sns.set(style="whitegrid")
sns.set(font_scale = 1.20)

input = pd.read_csv("Lactotrophs.csv")  

colors = ["bright red", "azure", "teal", "marine blue"]


graph = sns.factorplot(x="TRH concentration", y="Percentage", hue= "Phase", 
                       col="Region",data=input, capsize=.2, 
                        palette=sns.xkcd_palette(colors),
                       size=8, aspect=.75, legend_out=False) 


graph.despine(left=True)
sns.plt.ylim(30,100)

#%%
#   Construye la gráfica de actividad por región
##          en cada Fase del ciclo: TIROTROPOS

sns.set(style="white")
sns.set(font_scale = 1.20)


inputt = pd.read_csv("Thyrotrophs.csv")  

colors = ["bright red", "azure", "teal", "marine blue"]

graph = sns.factorplot(x="TRH concentration", y="Percentage", hue= "Phase", 
                       col="Region",data=inputt, capsize=.2, 
                       palette=sns.xkcd_palette(colors),
                       size=8, aspect=.75, legend_out=False) 

                       
graph.despine(left=True)
sns.plt.ylim(30,100)

#%%


##    Construye la gráfica de las proporcions celulares
#            Central y Lateral 
sns.set(style="white")

celltype = pd.read_csv("ThyroBasal.csv")


flatui = ["r","k"]

graph = sns.factorplot(x="Phase", y="Percentage", hue="Region",
                       data=celltype, size=6, 
                       palette=sns.color_palette(flatui),
                       legend_out=False)

graph.despine(left=True) 
plt.legend(loc='upper left')
sns.plt.ylim(0,100)
graph.set_ylabels("Percentage") 

#%%
# ANOVA tEST OF BASAL ACTIVITY FOR EACH CONDITION IN & OR INDEPENDENT REGION 

CB = ([59.46,63.64,40.0,31.52,17.02,13.16], 
      [54.55,33.33,41.49,44.0,36.96,26.83],
      [36.67,41.07,41.3,50.0,33.33,33.33],
      [44.44,57.14,84.21,48.78,33.33,25.0])


F, p= stats.f_oneway(CB[0],CB[1],CB[2],CB[3])

CL = ([40.77,38.1,30.61,38.46,29.69,37.04],
      [56.06,61.4,52.63,60.24,41.18,25.0],
      [35.71,53.85,44.0,47.06,40.0,45.45],
[50.0,
44.83,
71.79,
30.43,
31.25,
56.25])



F, p= stats.f_oneway(CL[0],CL[1],CL[2],CL[3])

C = ([59.46,63.64,40.0,31.52,17.02,13.16,54.55,33.33,
      41.49,44.0,36.96,26.83,36.67,41.07,41.3,50.0,
      33.33,33.33,44.44,57.14,84.21,48.78,33.33,25.0],
      [40.77,38.1,30.61,38.46,29.69,37.04,56.06,61.4,
       52.63,60.24,41.18,25.0,35.71,53.85,44.0,47.06,
       40.0,45.45,50.0,44.83,71.79,30.43,31.25,56.25])

F, p= stats.f_oneway(C[0],C[1])


#%%
#   Exporta las coordenadas de las céulas en cada caso
##    Dibuja el mapa de dispersion de los dos grupos celulares, en region
###                    central y lateral

#coorsL= np.loadtxt('cL290617L.csv', delimiter= ',') # lateral
coorsC= np.loadtxt('L290617C.csv', delimiter= ',') # central


ll=[]      
     
for i in range(0, len(RoiLact)):
    ll.append(coorsC[int(RoiLact[i]),:])

#      Coordenadas Tirotropos 

tt=[]
   
#coors[int(t1[0]),:]

for i in range(0, len(RoiTir)):
    tt.append(coorsC[int(RoiTir[i])-1,:])    
    
tt=np.array(tt) 
ll=np.array(ll)

# Red LACTOTROPOS
plt.figure(9)
#plt.clf
#img = mpimg.imread ('D280709.png')
#imgplot = plt.imshow(img, cmap ='gray')
#xminmax=plt.xlim()
#yminmax=plt.ylim()
#   Extracción de coordenadas de ROI's
#Lactotropos
x1 = ll[:,0]
y1 = ll[:,1]

#Tirotropos
x2 = tt[:,0]
y2 = tt[:,1]

colors = ['lightslategray','tomato']

plt.scatter([x1],[y1], s=9, c=colors[0], marker='o', alpha = 0.7, label ='Other Cells')
plt.scatter([x2],[y2], s=9, c=colors[1], marker='o', alpha = 0.7, label = 'thyrotrophs')

plt.legend()
plt.show

#%%

#     CORRELACIÓN DE ACTIVIDAD DE CADA CÉLULA EN CADA TRATAMIENTO

datosNorm=detrend(NormF(datos))



def SurrogateCorrData(datos,N=1000): #Número de veces en las que se generará las matrices aleatorizadas
    fftdatos=np.fft.fft(datos,axis=-1)
    ang=np.angle(fftdatos)
    amp=np.abs(fftdatos)
    #Cálculo de la matriz de correlación de los datos aleatorizados
    CorrMat=[]
    for i in range(N):
        angSurr=np.random.uniform(-np.pi,np.pi,size=ang.shape)
        angSurr[:,350:]= - angSurr[:,350:0:-1] #trabajamos sólo en dos dimensiones: tiempo y población
        angSurr[:,350]=0
        
        fftdatosSurr=np.cos(angSurr)*amp + 1j*np.sin(angSurr)*amp
    
        datosSurr=np.real(np.fft.ifft(fftdatosSurr,axis=-1)) #arroja la valores reales de los datos aleatorizados
        spcorr2,pval2=stats.spearmanr(datosSurr,axis=1)
        CorrMat.append(spcorr2)
        
    CorrMat=np.array(CorrMat)
    return CorrMat
  

SCM=SurrogateCorrData(datosNorm[i])     

#Calculate the standart desviation and mean of SCM=SurrogateCorrData
meanSCM=np.mean(SCM,0)
sdSCM=np.std(SCM,0)



# GRÁFICOS DE LAS MATRICES DE CORRELACIÓN     v  



#   Ploteo de las matrices de correlación considerando la desviación estándar (2) de la distribución de la matriz aleatorizada

spcorr,pval=stats.spearmanr(datosNorm[i],axis=1) 
#spcorr[pval>=0.0001]=0


#Filtro de la matriz original, que tomará como 0 a los valores abs de la correlación que sean menores a 2SD del promedio de SCM, 
 #          Cambiamos a tres derviaciones estándar
spcorr[np.abs(spcorr)<(meanSCM + 2*sdSCM)]=0

np.savetxt(filename +"01spcorr.csv", spcorr, delimiter=',')


plt.figure(4)
plt.clf()

 
plt.subplot(231)
plt.plot(datosNorm[i].T)

plt.subplot(232)
plt.imshow(spcorr,interpolation='none',cmap='inferno',vmin=-1,vmax=1)
plt.colorbar()
plt.grid(False)    

plt.subplot(233)
plt.hist(spcorr.ravel(),bins=50)

plt.subplot(234)
plt.plot(SCM[i])

plt.subplot(235)
plt.imshow(np.std(SCM,0),interpolation='none',cmap='viridis')
#plt.imshow(spcorr2,interpolation='none',cmap='jet')

plt.grid(False)    

plt.subplot(236)
plt.hist(SCM[:,5,8],bins=50)



#%% 
#
filename ='L120917-L100spcorr'
spcorr = np.loadtxt(filename + ".csv",delimiter=',')

#%%
spcorrT = [] 

for i in range(0, len(TotalCellsRoi)):
   spcorrT.append(spcorr[int(TotalCellsRoi[i]),:])

spcorrT=np.array(spcorrT)

spcorr2=np.tril(spcorrT)
z = np.where((spcorr2>0.3) & (spcorr2<0.9)) # forma de usar doble condición en un where

zz=[]

#usando zip para iterar las parejas 
for i1,i2 in zip(z[0],z[1]):
    zz.append((i1,i2, spcorr2[i1,i2]))
#def remove_duplicates(i):
#    return list (set(i))
zz=np.array(zz)  

#%%


spcorr2=np.tril(spcorr)
z = np.where((spcorr2>0.3) & (spcorr2<0.9)) # forma de usar doble condición en un where

zz=[]

#sacamos lista de las parejas que tienen un spcorr !=0 y <1 con zz.append  
#sacamos los valores de la correlación !=0 y <1 anexando al append, sp[i]

#usando zip para iterar las parejas 
for i1,i2 in zip(z[0],z[1]):
    zz.append((i1,i2, spcorr2[i1,i2]))
#def remove_duplicates(i):
#    return list (set(i))
zz=np.array(zz)  
  
    
#%%

#     SACAMOS LA CANTIDAD DE CONEXIONES QUE TIENE CADA CÉLULA 


binsp = 1*(np.abs(spcorr2>0.3) & (spcorr2<0.9)).astype(float)

conex = (sum(binsp).astype(float)) 

Nodes = (np.where(conex!=0)) #regresa tuple

Conex = (conex[conex!=0])

#np.savetxt(filename +"100conex.csv", Conex, delimiter=',')
 #CONEXIONES DE TODAS LAS CÉLULAS RESPONSIVAS
 
Nodes = np.array(Nodes).T.astype(float) 
Nodos= np.vstack((Nodes.T[0],Conex)).T  ####Número de nodo más el número de conexiones que tiene
Nod = Nodos[:,0] 
NodosCells = np.intersect1d(Nod, TotalCellsRoi).astype(float)

Resp = []
for i in range(0, len(NodosCells)):
    Resp.append(Nodos[int(NodosCells[i])])

Resp = np.array(Resp)

zzT = []
for i in range(0, len(NodosCells)):
    zzT.append(zz[int(NodosCells[i]),:])

zzT = np.array(zzT)
#
#ROIS lact o tir que son nodos conectados Coordenadas


coorsC= np.loadtxt('cL290617L.csv', delimiter= ',') # central , 

Total=[]      
     
for i in range(0,len(TotalCellsRoi)):
    Total.append(coorsC[int(TotalCellsRoi[i]),:])

Total = np.array(Total) #Coordenadas del número total de células
#%%

# Plot network of interest
plt.style.use('seaborn-whitegrid')

#plt.clf()

x = Total[:,0]
y = Total[:,1]

plt.plot([x],[y],'k.',ms=8)
for link in zz:
    plt.plot((x[link[0]],x[link[1]]),(y[link[0]],y[link[1]]),'-',linewidth=0.8,
             c=cm.seismic(link[2]/2+0.3),lw=np.abs(link[2])*1)

##plt.colorbar()
plt.grid(False)
#plt.colorbar()
#plt.show


#%%

#   Histograma de densidad de la red, con funciones ajustadas
#Resp = np.loadtxt('LLConex100T.csv', delimiter= ',')


plt.style.use('seaborn-whitegrid')

fig, axes = plt.subplots(
                         )

plt.hist(Resp,bins=50, facecolor='k', normed= True) 
xt = plt.xticks()[0]  
xmin, xmax = min(xt), max(xt)  
lnspc = np.linspace(xmin, xmax, len(Conex))


u = np.mean(lnspc) 
v = np.var(lnspc)
K = stats.kurtosis(lnspc)

m, s = stats.norm.fit(Conex) # get mean and standard deviation  
pdf_g = stats.norm.pdf(lnspc, m, s) # now get theoretical values in our interval  
plt.plot(lnspc, pdf_g, label="Norm") # plot it

ag,bg,cg = stats.gamma.fit(Conex)  
pdf_gamma = stats.gamma.pdf(lnspc, ag, bg,cg)  
plt.plot(lnspc, pdf_gamma, label="Gamma")

ab,bb,cb,db = stats.beta.fit(Conex)  
pdf_beta = stats.beta.pdf(lnspc, ab, bb,cb, db)  
plt.plot(lnspc, pdf_beta, label="Beta")

#axes.set_ylabels('Probability')
#axes.set_xlabels('Degree')


axes.axis([0,150,0,0.1])


plt.show() 

#%%

#   MAPA DE DISPERSIÓN, DE ACUERDO AL NÚMERO DE CONEXIONES
#
sns.set(style="dark")
#sns.set(font_scale = 1.20)


df = pd.read_csv("Mapa01L290617T.csv")
ax1 = df.plot.scatter(x='X',
                      y= 'Y',
                      c = 'C',
                      alpha=.90,
                      colormap = 'coolwarm',
                      vmin=1,vmax=100)

#%%

#  Probability Density of connections in all phases 

sns.set(style='ticks') 
 
input = pd.read_csv("LCConex100L.csv") 
 
Phases = ['D', 'E', 'P', 'W'] 
 
 
 
 
for Phase in Phases: 
    # Subset to the airline 
    subset = input [input['Phase'] == Phase] 
    sns.distplot(subset['Conexion'], hist = False, kde = True, norm_hist=True, 
                   
                 kde_kws = {'shade': True, 'linewidth': 3},label = Phase) 
 
     
#    # Draw the density plot 
#    sns.distplot(subset['Conexion'], hist = False, kde = True, 
#                 kde_kws = {'linewidth': 3}, 
#                 label = Phase) 
#     
     
plt.axis([0,300,0,0.1]) 
 
plt.legend(prop={'size': 8}, title = 'Phase') 
plt.xlabel('k Degree') 
plt.ylabel('P(k)') 
 
#%% 
 
 
# Grafica de comparacion P>0.5 
 
dat = pd.read_csv("GlobalL.csv") 
 
flatui = ["r","dimgrey"] 
 
g = sns.factorplot(x="Phase", y="Count", 
                   hue="Region", col="TRH Concentration", 
                   data= dat, kind="bar", 
                   size=4, aspect=.7, palette=sns.color_palette(flatui)) 
 
sns.plt.ylim(0,5000)

#%% 

### MÉTRICAS LOCALES
import networkx as nx

G= nx.Graph()

zz_=np.delete(zz,[2],axis=1)

zzTotal_list = zz_.tolist()
       
E = G.add_edges_from(zzTotal_list)


Nnodos = nx.number_of_nodes(G)
Density = nx.density(G)
Cluster = nx.average_clustering(G)
Assortativity = nx.degree_assortativity_coefficient(G)
ShortPath = nx.average_shortest_path_length(G)   
Connected = np.array(nx.connected_component_subgraphs(G))
plt.style.use('seaborn-whitegrid')

nx.draw(G,node_size=100,node_color='lightblue',edge_color='gray')

#%% 

df = pd.read_csv("MetricasT100_01.csv") 
 
 
flatui = ["dimgrey","r"] 
 
sns.set(style="ticks", palette=sns.color_palette(flatui)) 
 
 
# Draw a nested boxplot to show bills by day and time 
sns.boxplot(x="Phase", y="Assortativity", 
            hue="Region",  
            data=df, showfliers=False) 
sns.despine(offset=10, trim=True) 
#___________________________________________________________

df = pd.read_csv("MetricasH100_01.csv") 
 
 
flatui = ["dimgrey","r"] 
 
g = sns.catplot(x="Phase", y="ShortPath", 
                hue="Region", col="TRH Concentration", 
                data=df, kind="box", 
                height=4, aspect=.7);

#%%


df = pd.read_csv("MetricasL100_01.csv") 
 
 
flatui = ["r","dimgrey"] 
sns.set(style="ticks", palette=sns.color_palette(flatui)) 
 
 
# Draw a nested boxplot to show bills by day and time 
#sns.boxplot(x="Phase", y="Assortativity", 
#            hue="Region",  
#            data=df, showfliers=False) 
#sns.despine(offset=10, trim=True) 
 
sns.factorplot(x="Phase", y="Density", 
                   hue="Region", col="TRH Concentration", 
                   data= df, kind="box", 
                   size=4, aspect=.7, palette=flatui, legend = False) 
plt.legend(loc='upper right', fontsize= 'medium') 
 
 
sns.plt.ylim(-0.1,1.1)


#%% 

community=[]

def edge_to_remove(G):
    dict1=nx.edge_betweenness_centrality(G)
    list_of_tuples = dict1.items()
    list_of_tuples.sort(key = lambda x:x[1], reverse = True)
    return list_of_tuples[0][0]
    
def girvan (G):
    c= nx.connected_component_subgraphs(G)
    l = len(list(c))
    print ('Connected Components are',l)
    
    while(l ==1):
        G.remove_edge(edge_to_remove(G))
        c= nx.connected_component_subgraphs(G)
        l = len(list(c))
        print ('Connected Components are',l)
        
    return c


    
#   Calculamos métricas de la red, con Networkx

#from networkx.algorithms import approximation as apxa

c = girvan(G)

for i in c:
    community.array(i.nodes)



#%%

##     Análisis de componentes principales PCA1

import pandas as pd
import plotly
import plotly.graph_objs as go
import plotly.tools as tls

df = pd.read_csv("MetricasLateral.csv")

X = df.ix[:,3:7].values
y = df.ix[:,0].values

traces = []

legend = {0:False, 1:False, 2:False, 3:True}

colors = {'D': 'rgb(153, 204, 255)', 
          'E': 'rgb(255, 127, 14)', 
          'P': 'rgb(44, 160, 44)',
          'W': 'rgb(255,204,229)'}

for col in range(4):
    for key in colors:
        traces.append(go.Histogram(x=X[y==key, col], 
                        opacity=0.75,
                        xaxis='x%s' %(col+1),
                        marker=go.Marker(color=colors[key]),
                        name=key,
                        showlegend=legend[col]))

data = go.Data(traces)

layout = go.Layout(barmode='overlay',
                xaxis=go.XAxis(domain=[0, 0.25], title='ShortPath'),
                xaxis2=go.XAxis(domain=[0.3, 0.5], title='Density'),
                xaxis3=go.XAxis(domain=[0.55, 0.75], title='Cluster Coef'),
                xaxis4=go.XAxis(domain=[0.8, 1], title='Assortativity'),
                yaxis= go.YAxis(title='count'),
                title='Distribution of the different local metrics')

fig = go.Figure(data=data, layout=layout)
plotly.offline.plot(fig)


from sklearn.preprocessing import StandardScaler
X_std = StandardScaler().fit_transform(X)

import numpy as np
mean_vec = np.mean(X_std, axis=0)
cov_mat = (X_std - mean_vec).T.dot((X_std - mean_vec)) / (X_std.shape[0]-1)
print('Covariance matrix \n%s' %cov_mat)
print('NumPy covariance matrix: \n%s' %np.cov(X_std.T)) 
cov_mat = np.cov(X_std.T)

eig_vals, eig_vecs = np.linalg.eig(cov_mat)

cor_mat1 = np.corrcoef(X_std.T)

eig_vals, eig_vecs = np.linalg.eig(cor_mat1)

cor_mat2 = np.corrcoef(X.T)

eig_vals, eig_vecs = np.linalg.eig(cor_mat2)

u,s,v = np.linalg.svd(X_std.T)
u

for ev in eig_vecs:
    np.testing.assert_array_almost_equal(1.0, np.linalg.norm(ev))
print('Everything ok!')

#%%


#         PCA2
# Make a list of (eigenvalue, eigenvector) tuples
eig_pairs = [(np.abs(eig_vals[i]), eig_vecs[:,i]) for i in range(len(eig_vals))]

# Sort the (eigenvalue, eigenvector) tuples from high to low
eig_pairs.sort()
eig_pairs.reverse()

# Visually confirm that the list is correctly sorted by decreasing eigenvalues
print('Eigenvalues in descending order:')
for i in eig_pairs:
    print(i[0])

tot = sum(eig_vals)
var_exp = [(i / tot)*100 for i in sorted(eig_vals, reverse=True)]
cum_var_exp = np.cumsum(var_exp)

trace1 = go.Bar(
        x=['PC %s' %i for i in range(1,5)],
        y=var_exp,
        showlegend=False)

trace2 = go.Scatter(
        x=['PC %s' %i for i in range(1,5)], 
        y=cum_var_exp,
        name='cumulative explained variance')

data = go.Data([trace1, trace2])

layout=go.Layout(
        yaxis=go.YAxis(title='Explained variance in percent'),
        title='Explained variance by different principal components')

fig = go.Figure(data=data, layout=layout)
plotly.offline.plot(fig)
#%%
#          PCA3

matrix_w = np.hstack((eig_pairs[0][1].reshape(4,1), 
                      eig_pairs[1][1].reshape(4,1)))

Y = X_std.dot(matrix_w)

traces = []

for name in ('D', 'E', 'P','W'):

    trace = go.Scatter(
        x=Y[y==name,0],
        y=Y[y==name,1],
        mode='markers',
        name=name,
        marker=go.Marker(
            size=12,
            line=go.Line(
                color='rgba(217, 217, 217, 0.14)',
                width=0.5),
            opacity=0.8))
    traces.append(trace)


data = go.Data(traces)
layout = go.Layout(showlegend=True,
                scene=go.Scene(xaxis=go.XAxis(title='PC1'),
                yaxis=go.YAxis(title='PC2'),))

fig = go.Figure(data=data, layout=layout)
plotly.offline.plot(fig)

#%%

#        PCA4

from sklearn.decomposition import PCA as sklearnPCA
sklearn_pca = sklearnPCA(n_components=4)
Y_sklearn = sklearn_pca.fit_transform(X_std)


traces = []

for name in ('D', 'E', 'P','W'):

    trace = go.Scatter(
        x=Y_sklearn[y==name,0],
        y=Y_sklearn[y==name,1],
        mode='markers',
        name=name,
        marker=go.Marker(
            size=12,
            line=go.Line(
                color='rgba(217, 217, 217, 0.14)',
                width=0.5),
            opacity=0.8))
    traces.append(trace)


data = go.Data(traces)
layout = go.Layout(xaxis=go.XAxis(title='PC1', showline=False),
                yaxis=go.YAxis(title='PC2', showline=False))
fig = go.Figure(data=data, layout=layout)
plotly.offline.plot(fig)


#%%

#%%

##  CLUSTERING TRIES

#PosP = np.array(np.where((spcorrT>0) & (spcorrT<0.9)))

#sns.set()
#
#a4_dims= (11,8)
#
#
#df = pd.DataFrame(spcorrT)
#
#
#used_networks = [1,2,3,4]
#used_columns = (df.columns.get_level_values('node')
#                          .astype(int)
#                          .isin(used_networks))
#df = df.loc[:, used_columns]
#
## Create a categorical palette to identify the networks
#network_pal = sns.diverging_palette(220, 10, as_cmap=True)
#
#network_lut = dict(zip(map(str, used_networks), network_pal))
#
## Convert the palette to vectors that will be drawn on the side of the matrix
#networks = df.columns.get_values("network")
#network_colors = pd.Series(networks, index=df.columns).map(network_lut)
#
## Draw the full plot
#cmap = sns.cubehelix_palette(light=1, as_cmap=True)
#
#
#fig, ax = plt.subplots(figsize=a4_dims)
#
#sns.clustermap(df.corr(), center=0, cmap='seismic',
#               row_colors=network_colors, col_colors=network_colors,
#               linewidths=.75, figsize=(10, 10))

#%%
from sklearn.cluster import FeatureAgglomeration
import pandas as pd
import matplotlib.pyplot as plt

df = pd.DataFrame(spcorrT)

def dendrogram(df, number_of_clusters=int(df.shape[1] / 1.2)):
        # Create Dendrogram
        agglomerated_features = FeatureAgglomeration(n_clusters=number_of_clusters)
        used_networks = np.arange(0, number_of_clusters, dtype=int)

        # Create a custom palette to identify the networks
        network_pal = sns.cubehelix_palette(len(used_networks),
                                            light=.9, dark=.1, reverse=True,
                                            start=1, rot=-2)
        network_lut = dict(zip(map(str, df.columns), network_pal))

        # Convert the palette to vectors that will be drawn on the side of the matrix
        networks = df.columns.get_level_values(None)
        network_colors = pd.Series(networks, index=df.columns).map(network_lut)
        sns.set(font="monospace")
        # Create custom colormap
        cmap = sns.diverging_palette(h_neg=210, h_pos=350, s=90, l=30, as_cmap=True)
        cg = sns.clustermap(df.astype(float).corr(), cmap=cmap, linewidths=.5, row_colors=network_colors,
                            col_colors=network_colors)
        plt.setp(cg.ax_heatmap.yaxis.get_majorticklabels(), rotation=0)
        plt.setp(cg.ax_heatmap.xaxis.get_majorticklabels(), rotation=90)
        plt.show() 

dendrogram(df)
