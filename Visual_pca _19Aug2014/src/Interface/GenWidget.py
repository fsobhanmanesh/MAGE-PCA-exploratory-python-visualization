# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ProbFrame.ui'
#
# Created: Wed Feb 20 20:28:19 2013
#      by: PyQt4 UI code generator 4.9.6
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

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

class GenFrame(QtGui.QWidget):
    owner = None
    def __init__(self):
        super(GenFrame, self).__init__()
        self.setObjectName(_fromUtf8("Form"))
        self.resize(550, 377)
        self.horizontalLayout = QtGui.QHBoxLayout(self)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.tableWidget = QtGui.QTableWidget(self)
        self.tableWidget.setObjectName(_fromUtf8("tableWidget"))
        self.tableWidget.setColumnCount(5)
        self.tableWidget.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item.setText(_translate("TabedForm", "Gen Name", None))
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item.setText(_translate("TabedForm", "Chromosum Name", None))
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, item)
        item.setText(_translate("TabedForm", "Start Codon", None))
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(3, item)
        item.setText(_translate("TabedForm", "Stop Codon", None))
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(4, item)
        item.setText(_translate("TabedForm", "Strand Direction", None))
        self.horizontalLayout.addWidget(self.tableWidget)

        QtCore.QMetaObject.connectSlotsByName(self)

    def removeAllRow(self):
        while self.tableWidget.rowCount() >0:
            self.tableWidget.removeRow(0)
    
    def addRow(self, gen):
        
        self.tableWidget.setRowCount(self.tableWidget.rowCount()+1)
        
        self.genName = None
        self.coromsumName = None 
        self.startCodon = None
        self.stopCodon = None
        self.strandDirection  = None
        
        genName = QtGui.QTableWidgetItem(str(gen.genName))
        chroName = QtGui.QTableWidgetItem(str(gen.coromsumName))
        startCodon = QtGui.QTableWidgetItem(str(gen.startCodon))
        stopCodon = QtGui.QTableWidgetItem(str(gen.stopCodon))
        strandDirection = QtGui.QTableWidgetItem(str(gen.strandDirection))
        
        genName.setFlags(QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled)
        chroName.setFlags(QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled)
        startCodon.setFlags(QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled)
        stopCodon.setFlags(QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled)
        strandDirection.setFlags(QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled)
        
        
        self.tableWidget.setItem(self.tableWidget.rowCount()-1, 0, genName)
        self.tableWidget.setItem(self.tableWidget.rowCount()-1, 1, chroName)
        self.tableWidget.setItem(self.tableWidget.rowCount()-1, 2, startCodon)
        self.tableWidget.setItem(self.tableWidget.rowCount()-1, 3, stopCodon)
        self.tableWidget.setItem(self.tableWidget.rowCount()-1, 4, strandDirection)
        
        #self.tableWidget.setCellWidget(self.tableWidget.rowCount()-1, 1, pushButton)
    def setData(self, prob):
        for gen in prob.gens:
            self.addRow(gen)

def getGenWidget():
    if GenFrame.owner == None:
        GenFrame.owner = GenFrame()
    return  GenFrame.owner