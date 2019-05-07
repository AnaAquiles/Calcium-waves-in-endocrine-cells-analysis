# -*- coding: utf-8 -*-
"""
Created on Mon Jan 28 16:04:15 2019

@author: akire
Aquí va la parte de clasificación (América)
"""
import cv2
import numpy as np
from skimage.draw import circle
from skimage.feature import blob_log
from math import sqrt
import matplotlib.pyplot as plt
import scipy.stats
from collections import Counter
import math


#Función que calcula la entropía de la serie
def Entropia(Serie):
    longitud = len(Serie)
    diccionario = Counter(np.round(Serie, decimals=1));
    prob = np.asarray(list(diccionario.values()));
    prob = prob/longitud;
    suma = 0;
    NoOperaciones = len(prob);
    for k in range(NoOperaciones):
        suma = suma + (prob[k]*math.log(prob[k]));
    diccionario.clear();    
    return[abs(suma)]


#Función que clasifica la serie
def Clasification(Serie):
    #Calcular el mínimo de la serie 
    #Dividir la serie entre el mínimo
    #Ajustar una recta a todas las series de un solo tratamiento (esto no se puede hacer)
    #Restar a la serie la recta encontrada
    
    
    #Serie-promedio/promedio ó *Serie/minimo de la Serie    
    #*Ajustar una recta a la serie y restarla a la original, pero esto va a traer problemas!!!    
    #O primero hacer el ajuste y luego dividir entre el mínimo??
    #Calcular el sesgo    
    #Calcular la entropía    
    #Normalizar en el eje Y    
    #Cálculo del área en pasos de 1/#frames
    
    
    #Longitud de la serie
    longitud = len(Serie)
    #(Serie-promedio)/promedio
#    Serie = (Serie-np.mean(Serie))/np.mean(Serie)
    
    #Sesgo
    sesgo = scipy.stats.skew(Serie);
#    print('Sesgo: '+ str(sesgo))
    
    #Entropía
    entrop = Entropia(Serie)
#    print('entropía: '+ str(entrop))
    
    #Normalización de la serie
    Serie_min = np.amin(Serie);
    Serie_max = np.amax(Serie);
    Serie = (Serie - Serie_min)/(Serie_max-Serie_min);
    
    #Cálculo del área bajo la curva
    area = scipy.integrate.simps(Serie, dx=1/longitud);
#    print('área: '+ str(area))
    
    #Clasificación
    resultado = -1.06907683 - 0.58335174*area + 2.46826548*sesgo - 0.24431587*entrop[0]
    
    return(resultado)
    

#Función que hace la segmentación con el video original limitado en frames por el usuario    
def PituitarySegm(frame0, frame1, CellDiam, SerieProm, data):
    #abs(F - Fmean)/Fmean para aplanarla 
    #buscar la forma de normalizarla en el dominio!!!

    #Información de los datos
    (NoFrames, alto, ancho) = data.shape
    DiameterDict = {3:1, 5:2, 7:2.5, 9:3, 11:4, 13:4.5}                        #Variación sigma con el diámetro (impar)
    Sigma = DiameterDict[CellDiam]                                              #Sigma para el blob

    #Detección de spots    
    DesVest = np.std(data, 0)                                                  #Imagen de la desviación estándar    
    blobs_log = blob_log(DesVest, min_sigma=Sigma, max_sigma=Sigma, \
                         num_sigma=1, threshold=.1)                            #Detección de spots
    
    blobs_log[:, 2] = blobs_log[:, 2] * sqrt(2)                                #Compute radii in the 3rd column.    

    
    #Para mostrar la imagen de la desvest con los círculos superpuestos usando matplotlib 
    fig, axes = plt.subplots()
    axes.imshow(DesVest, cmap='seismic')
    
    for blob in blobs_log:                                                     
        y, x, r = blob
        c = plt.Circle((x, y), r, color='yellow', linewidth=1, fill=False)
        axes.add_patch(c)
    
    axes.set_axis_off()    
    plt.tight_layout()
    plt.show()
    
    
    #Imagen final de la máscara binaria!! con cv2 van a salir cruces y cosas raras!!
    mask = np.zeros((alto, ancho))                                             #Máscara final de la que se obtendrán los contornos
    mask2 = np.zeros((alto, ancho))
    
    
    #Esto solo es para pruebas
    blobs_log2 = blobs_log[0:3]
    
    #Generación de las series para cada spot    
    LenSerie = int(frame1-frame0)                                              #Longitud de la serie de tiempo (va a depender de lo que el usuario haya determinado inicialmente)
    
    for blob in blobs_log:                                                    #Para cada spot encontrado
#        binaria = np.zeros((alto, ancho), dtype=np.uint8)                      #Imagen binaria que contendrá la máscara del spot
        y, x, r = blob                                                         #Centro y radio del spot
        rr,cc = circle(int(y), int(x), CellDiam/2, shape = (alto, ancho))          #Da las coordenadas que tendrá el círculo de acuerdo al centro y radio dado, usando skimage                                       
        mask2[rr, cc] = 255                                                    #Dadas las coordenadas anteriores, se rellenan de blanco

        #Para crear un array de coordenadas, que servirá para el for anidado
        rr = np.expand_dims(rr, axis=1)
        cc = np.expand_dims(cc, axis=1)
        coordenadas = np.concatenate((rr,cc), axis=1)
        area = len(rr)
        

##        cv2.circle(binaria,(int(x),int(y)), int(r), (255,255,255), -1)         #Creación de la máscara del spot
#        area = cv2.countNonZero(binaria)                                       #Encontramos el número de pixeles diferentes de cero
#        coordenadas = np.argwhere(binaria == 1)                              #Buscamos las coordenadas de los pixeles blancos en la imagen binaria
#        print(coordenadas)
        SerieTiempo = np.zeros(LenSerie)                                       #Contendrá la serie de tiempo
        j=0                                                                    #Contador para la serie de tiempo
        for frame in range(frame0,frame1,1):                                   #Para generar la serie de tiempo de una longitud determinada 
            imagen_i = data[frame,:,:]                                         #Recorremos cada frame
            suma = 0                                                           #Suma de los pixeles en el frame
            for coordenada in coordenadas:                                     #Recorremos cada coordenada
                suma = suma + imagen_i[coordenada[0],coordenada[1]]            #Suma de las intensidades
            promedio = suma/area                                               #Sacamos el promedio
            SerieTiempo[j] = promedio                                          #El promedio se guarda en la serie        
            j=j+1                                                              #Porque el frame0 puede ser diferente de cero
        
        #Normalización de la serie antes de su clasificación
        SerieTiempo = (SerieTiempo-SerieProm)/SerieProm
                
        resultado = Clasification(SerieTiempo)                                 #Función que hace la clasificación de la serie obtenida

        if resultado>=0:                                                       #Si la clasificación indica que la región sí es célula
            #Aquí hay que agregar ese spot a la imagen binaria mask, tal vez convenga 
            #hacerlo usando plt para que se marquen círculos, y no cosas pixeleadas
            #pero habrá que ver si se puede hacer
            #También hay que obtener el contorno de la célula "solita" imagen binaria
            #Y también hay que agregar dicho contorno al diccionario de contornos
            #O hasta que se tenga la mask final, hacer las dos cosas, como abajo
            mask[rr, cc] = 255 
            
        else:
            print(0)
    
    plt.figure(2)
    plt.imshow(mask)
    cv2.imwrite('Binaria_Clasificada.png', mask) 
    cv2.imwrite('Binaria_Spots.png', mask2) 
    
#%% 
    #Esta parte es la que solo llama a la imagen binaria que ya se tiene
    #No hace ningún cálculo, es para la pueba de concepto
    print('Segmentación de Hipófisis, aquí hay que poner lo que está haciendo Ame')
    
    binaria = cv2.imread("G:\\Mi unidad\\EAGV\\Proyectos\\Segmentacion y Analisis de Celulas con GUI\\Datos brutos\\Videos_Daniel\\1\\BINARIA2.png",0)                                 #Para que se abra en blanco y negro (1 solo canal)                                         #El stack de imágenes se pasa a un arreglo
    (alto, ancho)=binaria.shape 

    # Detección de contornos de la imagen binaria
    copia_bin = binaria.astype(dtype='uint8')*255;

    # Detección de contornos de la imagen binaria
    (imagen1,contours,hierarchy)=cv2.findContours(copia_bin, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE);

    #Máscara tendrá el arreglo de la imagen que se va a superponer al video, será en formato RGBA
    mascara = np.zeros((alto, ancho, 4));
    mascara1 = np.zeros((alto, ancho, 3));
    cv2.drawContours(mascara1,contours,-1,(255,255,0),1);     #-1 en lugar del 0
    mascara[:,:,0:3] = mascara1;
    mascara[:,:,3][mascara1[:,:,0]>200]=255;                               #Solo se pondrá en no transparente la parte de las ROIs
    
    mascara2 = np.transpose(mascara,(1,0,2))                          #El (1,0,2) indica cómo se va a trasponer la matriz 3D (ejes)

        
    #Se generará un diccionario con los contornos
    keys = np.arange(len(contours));                                  #Las llaves serán el número consecutivo de los contornos
    ROI_dict = dict(zip(keys, contours));                        #https://stackoverflow.com/questions/209840/convert-two-lists-into-a-dictionary-in-python        
#
#    button1.setChecked(True)                                          #Ponemos en true el botón de "Show ROIs"
#
##        print(len(self.ROI_dict))
#
#    #Hay que hacer la clasificación de las series de tiempo
#    clasificacion = Series_Clasif()
##        print(self.clasificacion)
#    
#    #Ahora hay que poner la tabla donde se muestre la clasificacion y que también deje ver las series de tiempo y permita quitarlas
#
#    self.TablaFinal()        
#
#    self.Fig_dict = {}                                                     #Diccionario que tendrá las ROIs remarcadas con los checkbox
#%%
    return (mascara2, ROI_dict)   



#def Clasification(serie, frame0, frame1, i):
#    print(i)
#    
    