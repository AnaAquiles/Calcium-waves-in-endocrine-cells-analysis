# Calcium-waves-in-endocrine-cells-analysis
This code are available in python 3.5.2 The strucuture and divisions has follow the next list :


import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import simps
from scipy import signal
from scipy import stats 
from matplotlib import cm
import pandas as pd
import seaborn as sns 


filename="" # select your data filename 
data=np.loadtxt(filename + ".csv",delimiter=',')


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

