from cgitb import enable
from tracemalloc import start
from matplotlib.pyplot import magma
import numpy as np
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QDialog, QApplication, QFileDialog, QColorDialog,QListWidgetItem,QTreeWidgetItem
from sqlalchemy import false
from sympy import symbols
from db_connection import CAO_MEASURES
from reading_data import FilesReader
import pyqtgraph as pg
from plotManager import PlotManager,PlotLine
import pyqtgraph
from secondDialog import DataFileDialog
from tools_signals import ManagerTools
from itertools import repeat
import pandas as pd
import random


class WelcomeScreen(QDialog):
    def __init__(self):
        super(WelcomeScreen, self).__init__()
        loadUi("/Users/smain/Documents/TX/ui_stress-master/designer/mainW.ui", self)

        self.numPoints = 800 #valeur d'origine 100
        self.counter = 0
        self.sigVarColor = {}
        self.lengedPlot=None
        self.lengedPlotFilter=None
       
        self.isFirstPlot = False
        self.nameFirstPlot = ""
        self.disableFirstPlot = False

        self.isFirstPlotFilter = False
        self.nameFirstPlotFilter = ""
        self.disableFirstPlotFilter = False
        self.matchedPlots = False


        self.firstSearchDone = False
        self.layoutPlot = None
        self.layoutPlotFilter = None
        self.managerSignalsFilter ={"root":"Filtres","nodes":[]}

        self.timer = None
        self.timer2 =None

        self.indexColumnsFilters= 10

        self.ui_signal.setBackground("w")
        self.ui_signal_2.setBackground("w")

        self.btn_recover_file.clicked.connect(self.readFiles)
        self.btn_search_data.clicked.connect(self.searchData)
        
        self.btn_replay_plot.clicked.connect(self.replayPrincipalPlot)
        self.btn_pause_plot.clicked.connect(self.pausePrincipalPlot)


        #replay button disabled since start
        self.btn_replay_plot.setEnabled(False)
        self.horizontalSlider.setEnabled(False)
        self.horizontalSlider.setMinimum(-30)
        self.horizontalSlider.setMaximum(-1)
        self.horizontalSlider.setValue(-15)
       

        self.lst_vars_widget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        self.horizontalSlider.valueChanged.connect(self.updateTimer)
        self.label_ord_principal.setText("")
        self.rbt_ecg.toggled.connect(lambda:self.updateListVariables(self.rbt_ecg))
        self.rbt_eda.toggled.connect(lambda: self.updateListVariables(self.rbt_eda))
        self.rbt_ppg.toggled.connect(lambda: self.updateListVariables(self.rbt_ppg))
        self.rbt_emg.toggled.connect(lambda :self.updateListVariables(self.rbt_emg))

        self.lst_vars_widget.currentRowChanged.connect(self.selectColorSignal)
        self.lst_vars_widget.itemChanged.connect(self.selectedSignal)
        self.treeWidgetFilters.itemChanged.connect(self.selectedFilter)
        self.plotManager = PlotManager()




    def increaseIndexColFilters(self):
        self.indexColumnsFilters = self.indexColumnsFilters + 1

    def decreaseIndexColFilters(self):

        self.indexColumnsFilters = self.indexColumnsFilters - 1


    def readFiles(self):

        """
        Cette methode nous permet ouvrir une fenetre sur laquelle le systeme de
        fichiers de notre ordinateur sera ouvert. Il nous permet choisir le fichier 
        .mat ou .csv dont on importera des informations a la BD.
        """
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        files, _ = QFileDialog.getOpenFileNames(self, "QFileDialog.getOpenFileNames()", "",
                                                "All Files (*);;Python Files (*.py)", options=options)
        if files:
            fileReader = FilesReader()
            listSignals = fileReader.getSignalListFromFile(files)
            secondD = DataFileDialog(listSignals,files)
            secondD.exec_()


    def searchData(self):
        """
        Grace a cette methode on peut recuperer les liste des valuers des signals choisie ainsi que 
        leurs timestaps.  Au meme temps , une fois tous les informations sont recuperees on utiliser des methodes
        supplementaires pour commencer a lancer l'affichage des signals sur le premier plot.
        On prepare aussi les objets necessaires qui seron utilises pour l'affichage des filtres et features.
        """
        if not self.firstSearchDone:
            self.firstSearchDone = True
        else: 
            #set all the variables as if it were the first time we click the bottom
            plotManagerRef = PlotManager.getInstance()
            for line in plotManagerRef.getListFiltersBySignalName(self.nameFirstPlot):
                if line.getIsPlotted(): 
                    referencePlotLine = line.getLineReference()
                    lineViewBox = line.getViewBox()
                    lineViewBox.removeItem(referencePlotLine)
                    axisReference = line.getAxis()
                    self.layoutPlotFilter.removeItem(axisReference)

            plotManagerRef.clearPlotManager()
            #reinitialize flags
            self.isFirstPlot = False
            self.nameFirstPlot = ""
            self.disableFirstPlot = False
            #reinitialize layout
            self.layoutPlot = None
            #reinitialize timers
            self.timer = None
            self.timer2 =None
            #reinitialize legends
            self.lengedPlot=None
            self.lengedPlotFilter=None

            #clear plot
            self.ui_signal.clear()
            self.ui_signal_2.clear()
            self.treeWidgetFilters.clear()
            #unmatch plot
            self.matchedPlots = False

        id = self.edt_ln_id.text()
        sessionId = self.edt_ln_ss.text()
        listSignalsData = []
        caoMeasures = CAO_MEASURES()
        self.lengedPlot = self.ui_signal.addLegend(offset=(560, 30))
        self.lengedPlotFilter = self.ui_signal_2.addLegend(offset=(660, 30))
        

        managerPlot = PlotManager.getInstance()
        testListSign=[]
        managerTools = ManagerTools()
        signalType = ""

        #signal value on position 1 (dataPlotSignal[1])
        listDictFilterPerSignal = []
        listSelectedSignals =[]
        for signalVarName in self.lst_vars_widget.selectedItems():
            dataPlotSignal = caoMeasures.retrieveData(id, sessionId, signalVarName.text())
            listSelectedSignals.append(signalVarName.text())
            testListSign = dataPlotSignal[1]
            listTimeStamps = dataPlotSignal[0]
            listSignalsData.append([dataPlotSignal[0],dataPlotSignal[1],signalVarName.text(),self.getColorVarSignalByKey(signalVarName.text())])


            #change representation qlistitemwidget

            signalVarName.setFlags(signalVarName.flags() | QtCore.Qt.ItemIsUserCheckable)
            signalVarName.setCheckState(QtCore.Qt.Checked)
            if not self.disableFirstPlot:
                self.disableFirstPlot = True
                signalVarName.setFlags(QtCore.Qt.NoItemFlags)



            #prepare flag for manager tools
            print(signalVarName.text())
            if "ECG" in signalVarName.text():
                signalType = "ECG"
            elif "EDA" in signalVarName.text():
                signalType = "EDA"
            elif "EMG" in signalVarName.text():
                signalType = "EMG"
            if "PPG" in signalVarName.text():
                signalType = "PPG"


        #create reference to line on the plot
        for index,dataPlot in enumerate(listSignalsData):
            if len(dataPlot[0]) != 0 and len(dataPlot[1]) != 0:
                self.lb_isFile.setStyleSheet("background-color: green")
                penObj = pg.mkPen(color=dataPlot[3])
                dataPlot[0]=[x - dataPlot[0][0] for x in dataPlot[0]]
                if not self.isFirstPlot:
                    self.isFirstPlot = True
                    self.nameFirstPlot = dataPlot[2]
                    lineReference = pg.PlotItem()
                    self.layoutPlot = pg.GraphicsLayout()
                    self.ui_signal.setCentralWidget(self.layoutPlot)
                    self.layoutPlot.addItem(lineReference,row=2,col=1,rowspan=1,colspan=1)
                    #lineReference=self.ui_signal.plot([dataPlot[0][0]],[dataPlot[1][0]],name=dataPlot[2], pen=penObj)
                    
                    lineReferenceO = pg.PlotDataItem([dataPlot[0][0]],[dataPlot[1][0]],name=dataPlot[2], pen=penObj)

                    viewBoxPlotP = lineReference.vb
                    viewBoxPlotP.addItem(lineReferenceO)
                    viewBoxPlotP.sigResized.connect(self.updateViews)
                    #change the range for x and y axis
                    managerPlot.addElement(PlotLine(lineReferenceO,dataPlot[0][1:],
                                           dataPlot[1][1:],[dataPlot[0][0]],[dataPlot[1][0]],dataPlot[2],0,dataPlot[3],True,viewBoxPlotP))
                else:
                    newPlotView = pg.ViewBox()
                    firstPlotLien = managerPlot.getSingalPlotByName(self.nameFirstPlot)
                    referenceLienF = firstPlotLien.getLineReference()
                    firstLineVbRef = referenceLienF.getViewBox()
                    newAxis = pg.AxisItem('right')
                    self.layoutPlot.addItem(newAxis, row=2,col=index+2,rowspan=1, colspan=1)
                    self.layoutPlot.scene().addItem(newPlotView)
                    newAxis.linkToView(newPlotView)
                    newPlotView.setXLink(firstLineVbRef)
                    newAxis.setZValue(-10000)
                    #axisName = "axis "+str(index+1)
                    newAxis.setLabel(dataPlot[2], color='#ff0000')
                    lineReference=pg.PlotDataItem([dataPlot[0][0]],[dataPlot[1][0]],name=dataPlot[2], pen=penObj)
                    newPlotView.addItem(lineReference)
                    #change the range for x and y axis
                    managerPlot.addElement(PlotLine(lineReference,dataPlot[0][1:],
                                           dataPlot[1][1:],[dataPlot[0][0]],[dataPlot[1][0]],dataPlot[2],0,dataPlot[3],True,newPlotView))
            else:
                self.lb_isFile.setStyleSheet("background-color: red")


        if signalType == "EDA":
            self.label_ord_principal.setText("Conductance (uS)")
            for indexP,dataPlot in enumerate(listSignalsData):
                #dataPlot[1] : signal values
                #dataPlot[]: timestamps
                testListSign = [np.float64(x) for x in dataPlot[1]]
                listTimeStamps  = [np.float64(x) for x in dataPlot[0]]
                [processedSignal, SCR_features1,newTimeStamps] = managerTools.EDA_processing(testListSign,listTimeStamps,32)
                possibleFilters = processedSignal.columns
                print("-------------------TIMESTAMPS-----------------")
                print(type(newTimeStamps))
                print(newTimeStamps)
                print(len(newTimeStamps))
                print("-------------------END-TIMESTAMPS-----------------")
                try:

                    SCR_features1_df = managerTools.SCR_features(SCR_features1)
                    s_feat1 = managerTools.signal_features(processedSignal,signalType)
                except:
                    print("Features error") 
                
                
        if signalType == "PPG":
            self.label_ord_principal.setText("Amplitude (V)")
            for indexP,dataPlot in enumerate(listSignalsData):
                testListSign = [np.float64(x) for x in dataPlot[1]]
                listTimeStamps  = [np.float64(x) for x in dataPlot[0]]
                [processedSignal,newTimeStamps,infoSignal]=managerTools.PPG_processing(testListSign,listTimeStamps,32)
                possibleFilters = processedSignal.columns
            
                s_feat1 = managerTools.signal_features(processedSignal,signalType,infoSignal)
                    # print("Features error") 
                
                


        if signalType =="EMG":
            pass
        if signalType =="ECG":
            pass
        
        if True:

            filtersName = self.showFilterList(possibleFilters,signalType)
            listDictFilterPerSignal.append({"signal_name":listSelectedSignals[indexP], "listFilters": filtersName})

            #fill manager with filter's plot references
            for index, filter in enumerate(filtersName):
                # 'EDA_Raw', 'EDA_Clean', 'EDA_Tonic', 'EDA_Phasic'
                if filter:
                    r = lambda: random.randint(0, 255)
                    ramdomColor = '#%02X%02X%02X' % (r(), r(), r())
                    #get data from the processedSignal (filter value)
                    dfFilter = pd.DataFrame(processedSignal, columns=[filter])
                    #pass the dataframe to list
                    dataFilter = dfFilter.values.flatten(order="C")
                    penObj = pg.mkPen(color=str(ramdomColor))
                    vecTime = [num for num in range(len(dataFilter))]

                    #start - adding features names
                    #raw,clean,tonic,phasic
                    listFeaturesFilter = self.listFeaturesTree(self.listFeaturesFilter(signalType),str(filter))
                    listPlotObjFeatures =[]
                    arrayFeatureValue = []
                    for feature in listFeaturesFilter:
                        dfFeature = pd.DataFrame(s_feat1, columns=[feature])
                        #pass the dataframe to list
                        dataFeature = dfFeature.values.flatten(order="C")
                        #print(feature,dataFeature)
                        arrayFeatureValue.extend(repeat(dataFeature[0],len(dataFilter)))
                        randomNum = lambda: random.randint(0, 255)
                        ramdomColorFeature = '#%02X%02X%02X' % (randomNum(), randomNum(), randomNum())

                        #listPlotObjFeatures.append(PlotLine(None, vecTime[1:], arrayFeatureValue[1:], [vecTime[0]], [arrayFeatureValue[0]], feature, 0,
                        #       ramdomColorFeature,False,None))
                        listPlotObjFeatures.append(PlotLine(None, newTimeStamps[1:], arrayFeatureValue[1:], [newTimeStamps[0]], [arrayFeatureValue[0]], feature, 0,
                                ramdomColorFeature,False,None))
                        
                        arrayFeatureValue = []
                                
                            
                    managerPlot.addListFeaturesFilter(listSelectedSignals[indexP],filter,listPlotObjFeatures)
                    #end - adding features names 

                    if not self.isFirstPlotFilter:
            
                        self.isFirstPlotFilter = True
                        penObj=pg.mkPen(color=str('#000000'))
                        ramdomColor='#000000'
                        self.nameFirstPlotFilter = filter
                        lineReference = pg.PlotItem()
                        self.layoutPlotFilter = pg.GraphicsLayout()
                        self.ui_signal_2.setCentralWidget(self.layoutPlotFilter)
                        self.layoutPlotFilter.addItem(lineReference,row=2,col=10,rowspan=1,colspan=1)
                        #lineReferenceO = pg.PlotDataItem([vecTime[0]],[dataFilter[0]],name=filter, pen=penObj)
                        lineReferenceO = pg.PlotDataItem([newTimeStamps[0]],[dataFilter[0]],name=filter, pen=penObj)
                        # lineReference.getAxis("left").setLabel(filter, color=ramdomColor)
                        
                        
                        viewBoxPlotP = lineReference.vb
                        firstPlotLien = managerPlot.getSingalPlotByName(self.nameFirstPlot)
                        referenceLienF = firstPlotLien.getLineReference()
                        firstLineVbRef = referenceLienF.getViewBox()
                        
                        viewBoxPlotP.setXLink(firstLineVbRef)
                        newAxis = lineReference.getAxis("left")
                        newAxis.setZValue(-10000)
                        newAxis.setLabel(filter, color=str(ramdomColor))



                        viewBoxPlotP.addItem(lineReferenceO)
                        viewBoxPlotP.sigResized.connect(self.updateViewsFilter)
                        #change the range for x and y axis
                        managerPlot.addElementListFilter(listSelectedSignals[indexP],
                        #PlotLine(lineReferenceO, vecTime[1:], dataFilter[1:], [vecTime[0]], [dataFilter[0]], filter, 0,
                        #       ramdomColor,False,viewBoxPlotP,lineReference.getAxis("left")))
                        PlotLine(lineReferenceO, newTimeStamps[1:], dataFilter[1:], [newTimeStamps[0]], [dataFilter[0]], filter, 0,
                                ramdomColor,False,viewBoxPlotP,newAxis,first_plot=False))


                        #create viewBox reference for the feature energy, it will be used for all the filters
                        viewBoxFeatureEnergyFilter = pg.ViewBox()
                        self.layoutPlotFilter.scene().addItem(viewBoxFeatureEnergyFilter)
                        managerPlot.addViewBoxEnergyFeature(viewBoxFeatureEnergyFilter)
                    else:

                        managerPlot.addElementListFilter(listSelectedSignals[indexP],
                        PlotLine(None, newTimeStamps[1:], dataFilter[1:], [newTimeStamps[0]], [dataFilter[0]], filter, 0,
                                ramdomColor,False,None))


                #create viewBox reference for the features  of each filter
                viewBoxFilter = pg.ViewBox()
                self.layoutPlotFilter.scene().addItem(viewBoxFilter)
                managerPlot.addViewBoxFeaturesFilter(listSelectedSignals[indexP],filter,viewBoxFilter)
        #show tree filters on UI
        self.fillTreeWidget(listDictFilterPerSignal,signalType)
        self.horizontalSlider.setEnabled(True)
        self.updateViews()
        self.setTimerDataUpdate()

    def updateViews(self):

        """ Sur cette methode il n'y a pas rien a modifier. Celle-ci nous permet de regler 
        les differents echelles des valeurs des signaux sur le premier plot afin de qu'on puisse
        voir l'affichage des differentes echelles.
        Methode lance au moment d'initialiser les objets qui seront utilises pour l'affichage
        des signaux.
        """
        managerPlot = PlotManager.getInstance()
        firstPlotLien = managerPlot.getSingalPlotByName(self.nameFirstPlot)
        ## view has resized; update auxiliary views to match
        for line in managerPlot.listLinesPlot():
            if line.getNameSignal() != self.nameFirstPlot:
                viewBoxReference = line.getViewBox()
                viewBoxReference.setGeometry(firstPlotLien.getViewBox().sceneBoundingRect())

    def updateViewsFilter(self):

        """
        Sur cette methode il n'y a pas rien a modifier. Celle-ci nous permet de regler 
        les differents echelles des valeurs des filtres et features sur le deuxieme plot afin de qu'on puisse
        voir l'affichage des differentes echelles.
        Methode lance au moment d'initialiser les objets qui seront utilises pour l'affichage
        des filtres et features.
        """

        managerPlot = PlotManager.getInstance()
        firstPlotLien = managerPlot.getLinePlotFilter(self.nameFirstPlot,self.nameFirstPlotFilter) #peut-être
        currentSignalWithFilters = managerPlot.getFiltersCurrentSignals()
        ## view has resized; update auxiliary views to match
        for signal in currentSignalWithFilters:
            listFiltersObj = managerPlot.getListFiltersBySignalName(signal)
            for filterObject in listFiltersObj:
                if signal== self.nameFirstPlot:
                    if filterObject.getNameSignal()!= self.nameFirstPlotFilter :
                        if filterObject.getIsPlotted():
                            viewBoxReference = filterObject.getViewBox()
                            viewBoxReference.setGeometry(firstPlotLien.getViewBox().sceneBoundingRect())
                        for feature in managerPlot.getListAllFeatures():
                            if feature.getIsPlotted():
                                viewBoxFeature = feature.getViewBox()
                                viewBoxFeature.setGeometry(firstPlotLien.getViewBox().sceneBoundingRect())


                else:
                    viewBoxReference = filterObject.getViewBox()
                    viewBoxReference.setGeometry(firstPlotLien.getViewBox().sceneBoundingRect())
                    for feature in managerPlot.getListAllFeatures():
                            if feature.getIsPlotted():
                                viewBoxFeature = feature.getViewBox()
                                viewBoxFeature.setGeometry(firstPlotLien.getViewBox().sceneBoundingRect())



    def updateListVariables(self,rbtEvent):

        """
        Methode qui nous permet recuperer les noms des singals pour un id et nombre de session donne. 
        La methode est declenche a chaque fois qu'on click sur un radio botton
        """
        caoMeasures = CAO_MEASURES()
        id = self.edt_ln_id.text()
        sessionId = self.edt_ln_ss.text()
        if self.timer is not None:
            self.timer.stop()
            self.timerStopped = True
            self.btn_replay_plot.setEnabled(True)
            self.btn_pause_plot.setEnabled(False)

        if self.lst_vars_widget.count() == 0:
            if rbtEvent.isChecked():
                if rbtEvent.text() == "ECG":
                    signalsDb = caoMeasures.retrieveSignalDB(id,sessionId,rbtEvent.text())
                    self.lst_vars_widget.addItems(caoMeasures.getVariables(signalsDb))
                if rbtEvent.text() == "EDA":
                    signalsDb = caoMeasures.retrieveSignalDB(id,sessionId,rbtEvent.text())
                    self.lst_vars_widget.addItems(caoMeasures.getVariables(signalsDb))

                if rbtEvent.text() == "EMG":
                    signalsDb = caoMeasures.retrieveSignalDB(id,sessionId,rbtEvent.text())
                    self.lst_vars_widget.addItems(caoMeasures.getVariables(signalsDb))

                if rbtEvent.text() == "PPG":
                    signalsDb = caoMeasures.retrieveSignalDB(id,sessionId,rbtEvent.text())
                    self.lst_vars_widget.addItems(caoMeasures.getVariables(signalsDb))

        else:
            self.lst_vars_widget.clear()
            if rbtEvent.isChecked():
                if rbtEvent.text() == "ECG":
                    signalsDb = caoMeasures.retrieveSignalDB(id,sessionId,rbtEvent.text())
                    self.lst_vars_widget.addItems(caoMeasures.getVariables(signalsDb))
                if rbtEvent.text() == "EDA":
                    signalsDb = caoMeasures.retrieveSignalDB(id,sessionId,rbtEvent.text())
                    self.lst_vars_widget.addItems(caoMeasures.getVariables(signalsDb))
                if rbtEvent.text() == "EMG":
                    signalsDb = caoMeasures.retrieveSignalDB(id,sessionId,rbtEvent.text())
                    self.lst_vars_widget.addItems(caoMeasures.getVariables(signalsDb))
                if rbtEvent.text() == "PPG":
                    signalsDb = caoMeasures.retrieveSignalDB(id,sessionId,rbtEvent.text())
                    self.lst_vars_widget.addItems(caoMeasures.getVariables(signalsDb))
    
    def selectColorSignal(self,idx):

        """
        Methode simple qui nous permet de lancer une fenetre secondaire sur laquelle on sera capable 
        de choisir la couleur du signal a afficher.
        """
        if idx != -1:
            color = QColorDialog.getColor()
            #variable name and select color in HEX
            self.addColorToVarSignal(self.lst_vars_widget.item(idx).text(),color.name())


    def selectedSignal(self,item):
        managerPlot = PlotManager.getInstance()
        if item.checkState():
            line = managerPlot.getSingalPlotByName(item.text())
            if not line.is_plotted:
                referencePlotLine = line.getLineReference()
                if referencePlotLine is None:
                    penObj = pg.mkPen(color=str(line.getColor()), width=1)
                    lineReference = pg.PlotDataItem([line.getAllDataX()[managerPlot.getCommonIndexPlotSignal()]],
                                                          [line.getAllDataY()[managerPlot.getCommonIndexPlotSignal()]],
                                                          name=line.getNameSignal(), pen=penObj)
                    lineViewBox = line.getViewBox()
                    lineViewBox.addItem(lineReference)
                    managerPlot.addReferenceNewPlot(item.text(), lineReference)
                    managerPlot.changePlotStateSignal(item.text(), True)
                
        else:
            line = managerPlot.getSingalPlotByName(item.text())
            if line.getLineReference() is not None:
                referencePlotLine = line.getLineReference()
                lineViewBox = line.getViewBox()
                lineViewBox.removeItem(referencePlotLine)
                managerPlot.addReferenceNewPlot(item.text(), None)
                managerPlot.changePlotStateSignal(item.text(), False)


    def selectedFilter(self,item):
        managerPlot = PlotManager.getInstance()
        if item.checkState(0):
            self.indexColumnsFilters=10
            while(self.layoutPlotFilter.getItem(row=2,col=self.indexColumnsFilters-1)!=None and self.indexColumnsFilters>0) : self.decreaseIndexColFilters()
            if(self.indexColumnsFilters>0) : 
            #is a feature
                if item.childCount() == 0:
                    filterNode = item.parent()
                    signalNode = filterNode.parent()
                    signalName = signalNode.text(0)
                    filterName = filterNode.text(0)
                    featureName = item.text(0)
                    plotObjFeature = managerPlot.getFeaturePlotObj(signalName,filterName,featureName)

                    if plotObjFeature.getLineReference() == None:
                        
                        #get scene (viewBox) from filter 
                        #filterLine = managerPlot.getLinePlotFilter(signalName,filterName)
                        #sceneFilter = filterLine.getViewBox()
                        viewBoxFilter = managerPlot.getViewBoxRefFeaturesFilter(signalName,filterName)
                        #create line reference 
                        penObj = pg.mkPen(color=plotObjFeature.getColor())
                        lineReference=pg.PlotDataItem([plotObjFeature.getAllDataX()[managerPlot.getCommonIndexFilterPlot()]],
                                                    [plotObjFeature.getAllDataY()[managerPlot.getCommonIndexFilterPlot()]],
                                                    name=featureName, pen=penObj)
                        

                        
                        #test
                        #newPlotView = pg.ViewBox()
                        firstPlotLien = managerPlot.getSingalPlotByName(self.nameFirstPlot)
                        referenceLienF = firstPlotLien.getLineReference()
                        firstLineVbRef = referenceLienF.getViewBox()
                        newAxis = pg.AxisItem('left')
                        self.layoutPlotFilter.addItem(newAxis, row=2,col=self.indexColumnsFilters-1,rowspan=1, colspan=1)
                        #self.layoutPlotFilter.scene().addItem(newPlotView)
                        viewBoxFeaturesFilter = None
                        if 'energy' in str(item.text(0)):
                            viewBoxFeaturesFilter = managerPlot.getViewBoxEnergyFeature()
                        else:
                            viewBoxFeaturesFilter = managerPlot.getViewBoxRefFeaturesFilter(signalName,filterName)
                        newAxis.linkToView(viewBoxFeaturesFilter)
                        viewBoxFeaturesFilter.setXLink(firstLineVbRef)
                        newAxis.setZValue(-10000)
                        #newAxis.setStyle(showValues=False)
                        #newAxis.showLabel(False)
                        newAxis.setLabel(str(item.text(0)), color=plotObjFeature.getColor())
                        
                        #newPlotView.addItem(lineReference)
                        managerPlot.addNewViewBoxPlotFeature(signalName,filterName,featureName,viewBoxFeaturesFilter)
                        self.decreaseIndexColFilters()

                        plotObjFeature.setAxis(newAxis)
                        #fin test
                        

                        viewBoxFilter.addItem(lineReference)
                        managerPlot.addReferenceNewPlotFeature(signalName,filterName,featureName,lineReference)
                        managerPlot.changePlotStateFeature(signalName,filterName,featureName,True)
                        print(featureName,plotObjFeature.getAllDataY()[managerPlot.getCommonIndexFilterPlot()])
                    else:
                        viewBoxFeature=plotObjFeature.getViewBox()
                        viewBoxFeature.addItem(plotObjFeature.getLineReference())
                        #add axis 
                        self.layoutPlotFilter.addItem(plotObjFeature.getAxis(), row=2,col=self.indexColumnsFilters-1,rowspan=1, colspan=1)
                        self.decreaseIndexColFilters()
                        #end add axis 
                        managerPlot.changePlotStateFeature(signalName,filterName,featureName,True)

                else:
                    #is a filter
                    father = item.parent()
                    line = managerPlot.getLinePlotFilter(father.text(0), item.text(0))
                    
                    if line.first_plot:
                        line.first_plot=False
                        line.colorPlot=QColorDialog.getColor().name()
                    
                    

                    if not line.getIsPlotted():
                        referencePlotLine = line.getLineReference()
                        if referencePlotLine is None:
                            #create viewBox for the filter
                            
                            penObj = pg.mkPen(color=str(line.getColor()), width=1)
                            #test
                            newPlotView = pg.ViewBox()
                            # firstPlotLien = managerPlot.getLinePlotFilter(self.nameFirstPlot,self.nameFirstPlotFilter)
                            firstPlotLien = managerPlot.getSingalPlotByName(self.nameFirstPlot)
                            referenceLienF = firstPlotLien.getLineReference()
                            firstLineVbRef = firstPlotLien.getViewBox()
                            newAxis = pg.AxisItem('left')
                            self.layoutPlotFilter.addItem(newAxis, row=2,col=self.indexColumnsFilters-1,rowspan=1, colspan=1)
                            self.layoutPlotFilter.scene().addItem(newPlotView)
                            newAxis.linkToView(newPlotView)
                            newPlotView.setXLink(firstLineVbRef)
                            newAxis.setZValue(-10000)
                            newAxis.setLabel(father.text(0)+item.text(0), color=str(line.getColor()))
                            line.setAxis(newAxis)
                            if line.getNameSignal() == "PPG_HRV" :
                                lineReference=pg.PlotDataItem([line.getAllDataX()[managerPlot.getCommonIndexPlotSignal()]],
                                                            [line.getAllDataY()[managerPlot.getCommonIndexPlotSignal()]],
                                                            name=line.getNameSignal(),pen=None,symbol="x",symbolSize=20)
                                                            
                            else : 
                                  lineReference=pg.PlotDataItem([line.getAllDataX()[managerPlot.getCommonIndexPlotSignal()]],
                                                        [line.getAllDataY()[managerPlot.getCommonIndexPlotSignal()]],
                                                        name=line.getNameSignal(), pen=penObj)
                            managerPlot.addNewViewBoxPlotFilter(father.text(0), item.text(0), newPlotView)
                            newPlotView.addItem(lineReference)

                            
                    
                            managerPlot.addReferenceNewPlotFilter(father.text(0), item.text(0), lineReference)
                            managerPlot.changePlotState(father.text(0), item.text(0), True)
                            
                        else:
                            #readd reference filter plot 
                            viewBoxFeature=line.getViewBox()
                            viewBoxFeature.addItem(line.getLineReference())
                            #end readd reference filter plot
                            
                            managerPlot.changePlotState(father.text(0), item.text(0), True)
                            #add axis 
                            self.layoutPlotFilter.addItem(line.getAxis(), row=2,col=self.indexColumnsFilters-1,rowspan=1, colspan=1)
                            firstPlotLien = managerPlot.getSingalPlotByName(self.nameFirstPlot)
                            firstLineVbRef = firstPlotLien.getViewBox()
                            #readd reference filter plot 
                            #end readd reference filter plot
                            viewBoxFeature.setXLink(firstLineVbRef)
                            #end add axis 
                            
                            # if self.nameFirstPlotFilter == item.text(0) and self.nameFirstPlot == father.text(0) and (not self.matchedPlots):
                            # #get match index principal plot 
                            # self.matchedPlots=True
                            # matchedIndex =managerPlot.trouverIndiceValeurLaPlusProche(line.getAllDataX(),
                            #     line.getAllDataX()[managerPlot.getCommonIndexPlotSignal()])
                            # managerPlot.setCommonIndexFilterPlot(matchedIndex)
                            # #end get match index principal plot 

        else:
            #unchecked element

            #is a feature
            if item.childCount() == 0:
                filterNode = item.parent()
                signalNode = filterNode.parent()
                signalName = signalNode.text(0)
                filterName = filterNode.text(0)
                featureName = item.text(0)
                plotObjFeature = managerPlot.getFeaturePlotObj(signalName,filterName,featureName)
                referencePlotLine = plotObjFeature.getLineReference()
                lineViewBox = plotObjFeature.getViewBox()
                lineViewBox.removeItem(referencePlotLine)
                #erase axis 
                axisReference = plotObjFeature.getAxis()
                self.layoutPlotFilter.removeItem(axisReference)
                #end erase axis
                
                #managerPlot.addReferenceNewPlotFeature(signalName,filterName,featureName,None)
                managerPlot.changePlotStateFeature(signalName,filterName,featureName,False)
               
            else:
                #is a filter
                father = item.parent()
                line = managerPlot.getLinePlotFilter(father.text(0), item.text(0))
                referencePlotLine = line.getLineReference()
                lineViewBox = line.getViewBox()
                lineViewBox.removeItem(referencePlotLine)

                #erase axis 
                axisReference = line.getAxis()
                self.layoutPlotFilter.removeItem(axisReference)
                #end erase axis

                managerPlot.changePlotState(father.text(0), item.text(0), False)

               


    def addColorToVarSignal(self,varSignal,color):
        self.sigVarColor[varSignal] = color

    def cleanDictColorVarSignal(self):
        self.sigVarColor.clear()

    def getColorVarSignalByKey(self,key):
        return self.sigVarColor[key]

    def getColorVarSignal(self):
        return self.sigVarColor

    def setTimerDataUpdate(self):

        """
        Cette methode est chargee de gerer la vitesse avec laquelle 
        seront affiches les points sur le plot du signal principal.
        Pour modifier le temps vous devrez changer la valeur dans la ligne 
        self.timer.setInterval(50) , la valeur 50 est en miliseconds.

        """
        self.timer= QtCore.QTimer()
        self.timer.setInterval(abs(self.horizontalSlider.value()))
        self.timer.timeout.connect(self.updateDataPlot)
        self.timer.timeout.connect(self.updateDataPlotFilter)
        
        self.timer.start()

    def pausePrincipalPlot(self):
        self.timer.stop()
        
        self.btn_replay_plot.setEnabled(True)
        self.btn_pause_plot.setEnabled(False)


    def replayPrincipalPlot(self):
        self.timer.start()
        self.btn_replay_plot.setEnabled(False)
        self.btn_pause_plot.setEnabled(True)

    def updateTimer(self):
        self.timer.setInterval(abs(self.horizontalSlider.value()))

        

    def updateDataPlot(self):
        managaerPlot = PlotManager.getInstance()
        for line in managaerPlot.listLinesPlot():
            if managaerPlot.getCommonIndexPlotSignal() < len(line.getAllDataX()) - 1:
                if line.getIsPlotted():
                    
                    if len(line.getCurrentDataPlottedX()) <= self.numPoints:
                        line.setCurrentDataPlottedX(line.getAllDataX()[managaerPlot.getCommonIndexPlotSignal()])
                        line.setCurrentDataPlottedY(line.getAllDataY()[managaerPlot.getCommonIndexPlotSignal()])
                        managaerPlot.setCommonIndexPlotSignal(managaerPlot.getCommonIndexPlotSignal() + 1)
                    else:
                        newX = line.getCurrentDataPlottedX()[1:self.numPoints]
                        newY = line.getCurrentDataPlottedY()[1:self.numPoints]
                        newX.append(line.getAllDataX()[managaerPlot.getCommonIndexPlotSignal()])
                        newY.append(line.getAllDataY()[managaerPlot.getCommonIndexPlotSignal()])
                        managaerPlot.setCommonIndexPlotSignal(managaerPlot.getCommonIndexPlotSignal() + 1)
                        line.setWholeDataX(newX)
                        line.setWholeDataY(newY)

                    line.getLineReference().setData(line.getCurrentDataPlottedX(), line.getCurrentDataPlottedY())
                    self.updateViews()

    def updateDataPlotFilter(self):
        managaerPlot = PlotManager.getInstance()
        key_list = list(managaerPlot.listLinesFilter().keys())
        for key in key_list:
            for line in managaerPlot.listLinesFilter()[key]:
                if line.getIsPlotted():
                    if managaerPlot.getCommonIndexPlotSignal() < len(line.getAllDataX()) - 1:
                        if len(line.getCurrentDataPlottedX()) <= self.numPoints:
                            if line.getNameSignal() == "PPG_HRV" :
                                if line.getAllDataY()[managaerPlot.getCommonIndexPlotSignal()]!=0:
                                    line.setCurrentDataPlottedY(line.getAllDataY()[managaerPlot.getCommonIndexPlotSignal()])
                                    line.setCurrentDataPlottedX(line.getAllDataX()[managaerPlot.getCommonIndexPlotSignal()])
                            else : 
                                line.setCurrentDataPlottedX(line.getAllDataX()[managaerPlot.getCommonIndexPlotSignal()])
                                line.setCurrentDataPlottedY(line.getAllDataY()[managaerPlot.getCommonIndexPlotSignal()])
                        else:
                            newX = line.getCurrentDataPlottedX()[1:self.numPoints]
                            newY = line.getCurrentDataPlottedY()[1:self.numPoints]
                            newX.append(line.getAllDataX()[managaerPlot.getCommonIndexPlotSignal()])
                            newY.append(line.getAllDataY()[managaerPlot.getCommonIndexPlotSignal()])
                            line.setWholeDataX(newX)
                            line.setWholeDataY(newY)
                        line.getLineReference().setData(line.getCurrentDataPlottedX(),line.getCurrentDataPlottedY())
        
        #plot features filter
        listAllFeatures = managaerPlot.getListAllFeatures()
        for plotObjFeature in listAllFeatures:
            
            if plotObjFeature.getIsPlotted():
                if managaerPlot.getCommonIndexPlotSignal() < len(plotObjFeature.getAllDataX()) - 1:
                    if len(plotObjFeature.getCurrentDataPlottedX()) <= self.numPoints:
                        plotObjFeature.setCurrentDataPlottedX(plotObjFeature.getAllDataX()[managaerPlot.getCommonIndexPlotSignal()-1])
                        plotObjFeature.setCurrentDataPlottedY(plotObjFeature.getAllDataY()[managaerPlot.getCommonIndexPlotSignal()-1])
                        #managaerPlot.setCommonIndexFilterPlot(managaerPlot.getCommonIndexFilterPlot() + 1)
                    else:
                        newX = plotObjFeature.getCurrentDataPlottedX()[1:self.numPoints]
                        newY = plotObjFeature.getCurrentDataPlottedY()[1:self.numPoints]
                        newX.append(plotObjFeature.getAllDataX()[managaerPlot.getCommonIndexPlotSignal()-1])
                        newY.append(plotObjFeature.getAllDataY()[managaerPlot.getCommonIndexPlotSignal()-1])
                        #managaerPlot.setCommonIndexFilterPlot(managaerPlot.getCommonIndexFilterPlot() + 1)
                        plotObjFeature.setWholeDataX(newX)
                        plotObjFeature.setWholeDataY(newY)

                    plotObjFeature.getLineReference().setData(plotObjFeature.getCurrentDataPlottedX(),plotObjFeature.getCurrentDataPlottedY())
        

                    

    def showFilterList(self,columnsList,signalType):

        """
        Ici , selon le type de signal que nous traitons on aura comment sortie la liste des noms 
        de filtres pour chaque type de signal. 
        Faudra mofidifier les valeurs des  listes ecgOptions et emgOptions
        """
        filterList = []
        if signalType == "ECG":
            ecgOptions = ['EDA_Raw', 'EDA_Clean', 'EDA_Tonic', 'EDA_Phasic']
            filterList = [signal for signal in columnsList if signal in ecgOptions]
        elif signalType == "EMG":
            emgOptions = ['EDA_Raw', 'EDA_Clean', 'EDA_Tonic', 'EDA_Phasic']
            filterList = [signal for signal in columnsList if signal in emgOptions]

        elif signalType == "EDA":
            edaOptions = ['EDA_Raw', 'EDA_Clean', 'EDA_Tonic', 'EDA_Phasic']
            filterList = [signal for signal in columnsList if signal in edaOptions]
        
        elif signalType == "PPG":
            ppgOptions = ['PPG_Raw','PPG_Clean','PPG_Rate','PPG_Peaks','PPG_HRV']
            filterList = [signal for signal in columnsList if signal in ppgOptions]


        return filterList

    def fillTreeWidget(self,listDictFilterPerSignal,typeSignal = ""):

        """
        Affichage de l'arborescence sur laquelle on trouve les filtres des signals
        et leurs features.
        """
        self.treeWidgetFilters.setColumnCount(1)
        root = QTreeWidgetItem([str("Filtres par signal")])
        self.treeWidgetFilters.addTopLevelItem(root)

        def addBranchsToRoot(root,listDictFilterPerSignal):
            for signalAndFilters in listDictFilterPerSignal:
                signalName = signalAndFilters["signal_name"]
                newBranch = QTreeWidgetItem([str(signalName)])
                root.addChild(newBranch)
                for signalFilterName in signalAndFilters["listFilters"]:

                    sheetBranch = QTreeWidgetItem([str(signalFilterName)])
                    sheetBranch.setFlags(sheetBranch.flags() | QtCore.Qt.ItemIsUserCheckable)
                    sheetBranch.setCheckState(0,QtCore.Qt.Unchecked)
                    newBranch.addChild(sheetBranch)
                    addFeaturesToFiltre(sheetBranch,self.listFeaturesTree(self.listFeaturesFilter(typeSignal),str(signalFilterName)))

        def addFeaturesToFiltre (branch, listFeaturesFiltre):
            for featureSignal in listFeaturesFiltre:
                sheetBranch = QTreeWidgetItem([str(featureSignal)])
                sheetBranch.setFlags(sheetBranch.flags() | QtCore.Qt.ItemIsUserCheckable)
                sheetBranch.setCheckState(0, QtCore.Qt.Unchecked)
                branch.addChild(sheetBranch)

        addBranchsToRoot(root,listDictFilterPerSignal)


    def listFeaturesTree(self,listFeatures,filter):
        typeFilter = filter.split("_")[1]
        typeFilter = typeFilter.lower()
        featuresFilter = []
        if(typeFilter=="hrv"):
            listFeatures=['LF','HF','LF/HF','RMSSD','PNN50','SDNN']
        for feauture in  listFeatures:
            featuresFilter.append(feauture+"_"+typeFilter)

        return featuresFilter


    def listFeaturesFilter(self,typeSignal):
        
        """
        Selon la valeur qu'on passe en parametre dans l'argument typeSignal on aura comment valeur 
        de retour la liste des prefixes des features pour chaque signal.
        La liste de retournee est utilisee pour concatener au nom de la feature le nom du filtre. 
        Exemple: 
        Pour typeSignal = 'EDA'
        Eventuellemnt on aura RMSE_raw, energy_raw,..., std_raw 
        """
        if typeSignal=="EDA":
            return ['RMSE','energy','min','mean','median','max','var','std']

        elif typeSignal == "EMG":
            return []
        elif typeSignal == "ECG":
            return []
        elif typeSignal == "PPG":
            return ['RMSE','energy','min','mean','median','max','var','std']




