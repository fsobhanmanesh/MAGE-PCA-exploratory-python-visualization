'''
Created on Mar 25, 2013

@author: sob016

'''
from PyQt4 import QtCore, QtGui
from Business.util import readMicroArrayFromFile, readPCAFromFile, makeFakePCAArray
from Interface.MyTabbedWidget import MyTabFrame
#from Interface.newPlot import PlotApp
from Interface.newscatterplot_19 import PlotApp2
from chaco.example_support import demo_main
from IPython.utils.traitlets import Enum

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
    
class MyMainWindow(QtGui.QMainWindow):
    owner = None
    def __init__(self):
        super(MyMainWindow, self).__init__()
        self.setObjectName(_fromUtf8("MainWindow"))
        self.resize(769, 578)
        self.centralwidget = QtGui.QWidget(self)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.tabWidget = QtGui.QTabWidget(self.centralwidget)
        self.tabWidget.setTabShape(QtGui.QTabWidget.Triangular)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.horizontalLayout.addWidget(self.tabWidget)
        self.setCentralWidget(self.centralwidget)
        
        self.menubar = QtGui.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 769, 20))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName(_fromUtf8("menuFile"))
        self.menuEdit = QtGui.QMenu(self.menubar)
        self.menuEdit.setObjectName(_fromUtf8("menuEdit"))
        self.menuAlgorithm = QtGui.QMenu(self.menubar)
        self.menuAlgorithm.setObjectName(_fromUtf8("menuAlgorithms"))
        self.menuHelp = QtGui.QMenu(self.menubar)
        self.menuHelp.setObjectName(_fromUtf8("menuHelp"))
        self.setMenuBar(self.menubar)
        
        self.statusbar = QtGui.QStatusBar(self)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        self.setStatusBar(self.statusbar)
        self.actionOpen_Database = QtGui.QAction(self)
        self.actionOpen_PCADatabase = QtGui.QAction(self)
        self.actionAlgorithm1 = QtGui.QAction(self)
        
        
        
        QtCore.QObject.connect(self.actionOpen_Database, QtCore.SIGNAL('triggered()'), self.openDatabaseEvent)
        QtCore.QObject.connect(self.actionOpen_PCADatabase, QtCore.SIGNAL('triggered()'), self.openPCADatabaseEvent)
        QtCore.QObject.connect(self.actionAlgorithm1, QtCore.SIGNAL('triggered()'), self.algorithm1Event)
        
        self.actionOpen_Database.setObjectName(_fromUtf8("actionOpen_Database"))
        self.actionOpen_PCADatabase.setObjectName(_fromUtf8("actionOpen_PCADatabase"))
        self.actionAlgorithm1.setObjectName(_fromUtf8("actionAlgorithm1"))
        self.actionSave_Table = QtGui.QAction(self)
        self.actionSave_Table.setObjectName(_fromUtf8("actionSave_Table"))
        self.actionExit = QtGui.QAction(self)
        self.actionExit.setObjectName(_fromUtf8("actionExit"))
        self.actionProgram_Help = QtGui.QAction(self)
        self.actionProgram_Help.setObjectName(_fromUtf8("actionProgram_Help"))
        self.actionAbout = QtGui.QAction(self)
        self.actionAbout.setObjectName(_fromUtf8("actionAbout"))
        
        
        self.menuFile.addAction(self.actionOpen_Database)
        self.menuFile.addAction(self.actionOpen_PCADatabase)
        self.menuFile.addAction(self.actionSave_Table)
        self.menuFile.addAction(self.actionExit)
        self.menuAlgorithm.addAction(self.actionAlgorithm1)
        self.menuHelp.addAction(self.actionProgram_Help)
        self.menuHelp.addSeparator()
        self.menuHelp.addAction(self.actionAbout)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuAlgorithm.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        
        
        self.retranslateUi(self)
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "New Bioinformatic Software- Trial Version", None))
        MainWindow.setToolTip(_translate("MainWindow", "Load from file menu", None))
        self.menuFile.setTitle(_translate("MainWindow", "File", None))
        self.menuEdit.setTitle(_translate("MainWindow", "Edit", None))
        self.menuAlgorithm.setTitle(_translate("MainWindow", "Algorithm", None))
        self.menuHelp.setTitle(_translate("MainWindow", "Help", None))
        self.actionOpen_Database.setText(_translate("MainWindow", "Open Database", None))
        self.actionOpen_PCADatabase.setText(_translate("MainWindow", "Open PCA Database", None))
        self.actionAlgorithm1.setText(_translate("MainWindow", "first Algorithm", None))
        self.actionSave_Table.setText(_translate("MainWindow", "Save Table", None))
        self.actionExit.setText(_translate("MainWindow", "Exit", None))
        self.actionProgram_Help.setText(_translate("MainWindow", "Program Help", None))
        self.actionAbout.setText(_translate("MainWindow", "About", None))
        
    def addTab(self, QWidget, QString):
        self.tabWidget.addTab(QWidget, QString)
        
    def openDatabaseEvent(self):
        fileName = QtGui.QFileDialog.getOpenFileName()
        microArray  = readMicroArrayFromFile(fileName );
        tabframe1 = MyTabFrame()
        tabframe1.setData(microArray)
        parts = fileName.split("/")
        self.addTab(tabframe1, parts[len(parts)-1])
    
    def openPCADatabaseEvent(self):
        fileName = QtGui.QFileDialog.getOpenFileName()
        PCAData = readPCAFromFile(fileName)
        
        f1 = PlotApp2(PCAData)
        #f2 = PlotApp(PCAData)
        #f2.configure_traits()
        f1.configure_traits()
        
    def algorithm1Event(self):
        print("hello")
    

def getMainPage():
    if MyMainWindow.owner == None:
        MyMainWindow.owner = MyMainWindow()
    return  MyMainWindow.owner