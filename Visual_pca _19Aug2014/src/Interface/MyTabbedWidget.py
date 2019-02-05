'''
Created on Mar 28, 2013

@author: sob016

'''

from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import *
from DataAccess.data import MicroArray
from Interface import GenWidget
from Interface.GenWidget import getGenWidget

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class MyTabFrame(QtGui.QWidget):
    
    def __init__(self):
        self.microArray = None
        super(MyTabFrame, self).__init__()
        self.setObjectName(_fromUtf8("TabedForm"))
        self.resize(548, 441)
        self.horizontalLayout = QtGui.QHBoxLayout(self)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.tableWidget = QtGui.QTableWidget(self)
        self.tableWidget.setObjectName(_fromUtf8("tableWidget"))
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, item)
        self.horizontalLayout.addWidget(self.tableWidget)

        self.retranslateUi(self)
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self, TabedForm):
        TabedForm.setWindowTitle(_translate("TabedForm", "Form", None))
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("TabedForm", "Prob ID", None))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("TabedForm", "Prob Information", None))
        item = self.tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("TabedForm", "Description", None))
        
    def addRow(self, probSet):
        self.tableWidget.setRowCount(self.tableWidget.rowCount()+1)
        
        item = QtGui.QTableWidgetItem(str(probSet.probID))
        
        item.setFlags(QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled)
        self.tableWidget.setItem(self.tableWidget.rowCount()-1, 0, item)
        pushButton = QPushButton('View Genome');
        pushButton.id = probSet.probID
        
        QtCore.QObject.connect(pushButton, QtCore.SIGNAL('clicked()'), lambda who=str(probSet.probID): self.buttonClicked(who))
        self.tableWidget.setCellWidget(self.tableWidget.rowCount()-1, 1, pushButton)
   
    def buttonClicked(self, probId):
        #print("Hi " + str(probId))
        
        #array = self.microArray.getProbSetByIndex(probId)
        prob = self.microArray.getProbSetByID(probId)
        frame = getGenWidget()
        frame.removeAllRow()
        frame.setData(prob)
        frame.show()
        
        print(probId)
       
       
    def setData(self, microArray):
        self.microArray = microArray 
        for i in range(len(microArray)):
            self.addRow(microArray.getProbSetByIndex(i))