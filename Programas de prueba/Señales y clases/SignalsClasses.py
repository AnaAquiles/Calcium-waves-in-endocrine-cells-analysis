# -*- coding: utf-8 -*-
"""
Created on Tue Aug 13 12:32:07 2019

@author: akire
Revisar https://stackoverflow.com/questions/3891465/how-to-connect-pyqtsignal-between-classes-in-pyqt
Este programa es para ejemplificar la comunicación entre clases mediante señales
Primero se abre una ventana principal, que tiene un botón, al presionarlo se abre
una ventana de diálogo con otro botón, al presionarlo se emite una señal que es
recibida por la ventana principal, y escribe una frase en la terminal desde la 
ventana principal, finalmente se escriben unas frases pero desde la ventana de 
diálogo
"""

import sys
from pyqtgraph.Qt import QtGui, QtWidgets
from PyQt5 import uic
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5 import QtCore
#from GUI5_Principal import MainWinClass

Principal = uic.loadUiType("MainWin.ui")[0] 
Dialog = uic.loadUiType("DialogWin.ui")[0] 


class MainWinClass(QtGui.QMainWindow, Principal):    
    def __init__(self, ROI, close, parent=None):
        super().__init__(parent)        
        self.setupUi(self)
        
        self.pushButtonMW.clicked.connect(self.VentanaDialogo)
                                          
        
    def VentanaDialogo(self):
        self.dialogo = DialogClass(5)                 #Si no se pone el self la ventana se abre y cierra instantáneamente
        self.dialogo.okClicked.connect(self.frase)
        self.dialogo.show()
        
#        print("Abrir ventana de diálogo")

    def frase(self):
        print("Estoy en la MainWin")
    


class DialogClass(QtGui.QMainWindow, Dialog):             
    
    okClicked = QtCore.pyqtSignal()
    
    def __init__(self, gato, parent = None):
        super(DialogClass, self).__init__()
        self.setupUi(self)
        self.gato = gato
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint )    
        self.setWindowModality(QtCore.Qt.ApplicationModal) 
        self.pushButtonD.clicked.connect(self.Ssignal)
        
        
    def Ssignal(self):
        self.okClicked.emit()
        print("Se presionó el botón de la ventana diálogo")
        print("el valor de gato es:")
        print(self.gato)
        
        

app = QtGui.QApplication(sys.argv)
MyWindow = MainWinClass(0,None)
MyWindow.show()
app.exec_()

