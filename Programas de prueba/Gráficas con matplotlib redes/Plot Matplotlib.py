# -*- coding: utf-8 -*-
"""
Created on Thu Jan 10 13:37:00 2019

@author: akire
"""
import sys
from PyQt5 import QtGui, uic, QtCore

import numpy as np
import networkx as nx
#from PyQt5.QtWidgets import QPushButton


#http://blog.rcnelson.com/building-a-matplotlib-gui-with-qt-designer-part-1/
from matplotlib.figure import Figure
#from matplotlib.backends.backend_qt4agg import (
#    FigureCanvasQTAgg as FigureCanvas,
#    NavigationToolbar2QT as NavigationToolbar)



#https://stackoverflow.com/questions/12459811/how-to-embed-matplotlib-in-pyqt-for-dummies
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
import pyqtgraph as pg


form_class_0 = uic.loadUiType("G:\\Mi unidad\\GUI_HIP\\GUITHUB_VentanasSeperadas\\GUI4_MainWin.ui")[0]
form_class_1 = uic.loadUiType("G:\\Mi unidad\\GUI_HIP\\GUITHUB_VentanasSeperadas\\GUI4_PlotTableWin.ui")[0]

        

class OtherWindow(QtWidgets.QDialog, form_class_1):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setupUi(self)


        #Esto es para crear una red simulada
        B = nx.Graph()
        B.add_nodes_from([1, 2, 3, 4], bipartite=0)
        B.add_nodes_from([5,6,7,8,9, 10], bipartite=1)
        B.add_edges_from([(1, 5), (2, 7), (3, 8), (3, 9), (4, 9), (4, 10)])

        X = set(n for n, d in B.nodes(data=True) if d['bipartite'] == 0)
        Y = set(B) - X

        X = sorted(X, reverse=True)
        Y = sorted(Y, reverse=True)

        pos = dict()
        pos.update( (n, (1, i)) for i, n in enumerate(X) ) # put nodes from X at x=1
        pos.update( (n, (2, i)) for i, n in enumerate(Y) ) # put nodes from Y at x=2
        

        
        #Esta parte es para mostrar las imágenes con matplotlib a través de nx (prácticamente es directo)
        #Y también sirve para mostrar que se pueden mandar a graficar varias cosas en ventanas separadas
        figura1 = plt.figure(0)
        figura1.suptitle('test title', fontsize=20)
        nx.draw(B, pos=pos, with_labels=True)
 
    
        figura2 = plt.figure(1)
        figura2.suptitle('test title BLA', fontsize=20)
        nx.draw(B, pos=pos, with_labels=True)        
                

        #Esta parte es para mostrar la red dentro de la GUI, no en una ventana externa      
        #Los primeros 5 renglones son para crear los arreglos de nodos y conexiones
        conections = np.array([[0, 4], [1, 6], [2, 7], [2, 8], [3, 8], [3, 9]])
        positions = []
        for i in range(len(pos)):
            positions.append(pos[i+1])            
        positions = np.array(positions)
        
        #Esto es para mandar a graficarla red  a la GUI
        self.Grafo1.clear() 
        ItemGrafo = pg.GraphItem()
        ItemGrafo.setData(pos=positions, adj=conections, symbolPen='r',symbolBrush='r', symbol='o', size=0.1, pxMode=False, pen='y')
        self.Grafo1.addItem(ItemGrafo)
        
        #Esto es para poner el texto al lado de cada nodo
        for i in range(len(pos)):
            text = pg.TextItem(str(i))
            self.Grafo1.addItem(text)
            text.setPos(positions[i,0], positions[i,1])

        self.show()
        
        
        
        

#        #Con esta parte agregas una gráfica de matplotlib 
#        fig1 = Figure()
#        ax1f1 = fig1.add_subplot(111)
#        ax1f1.plot(np.random.rand(20))        
#        self.addmpl(fig1)


    def addmpl(self, fig):
        self.canvas = FigureCanvas(fig)
        self.mplvl.addWidget(self.canvas)
        self.canvas.draw()        
        self.toolbar = NavigationToolbar(self.canvas, self.mplwindow, coordinates=True)
        self.mplvl.addWidget(self.toolbar)            

        
    def samplemat(self, dims):
        aa = np.zeros(dims)
        for i in range(min(dims)):
            aa[i, i] = i
        return aa
        

class myWindow(QtGui.QMainWindow, form_class_0):
    
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        
#        super(myWindow, self).__init__()
#        self.ui = myWindow() 
        self.setupUi(self)
#        uic.loadUi("GUI4_MainWin.ui", self)
        
        self.findRoiAction.triggered.connect(self.FindCells)
        
        
        
    def FindCells(self):
        print("Entra a la función")
        self.myOtherWindow = OtherWindow()
#        self.myOtherWindow.show()
        
        

        
app = QtGui.QApplication(sys.argv)
MyWindow = myWindow(None)
MyWindow.show()
app.exec_()

#Para los grafos revisar http://www.pyqtgraph.org/documentation/graphicsItems/graphitem.html
#y el ejemplo de pyqtgraph de graphItem
