import numpy as np
class PlotManager():
    __instance = None

    @staticmethod
    def getInstance():
        """ Static access method. """
        if PlotManager.__instance is None:
            PlotManager()
        return PlotManager.__instance

    def __init__(self):
        if PlotManager.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            PlotManager.__instance = self
            self.arrayLinesPlot = []
            self.arrayLinesFilter = {}
            #[[nameSignal, nameFilter , {feature1:[],....,featuren:[]}]]
            self.arrayFeaturesFilter = []
            self.dictViewBoxFeatures = {}
            self.viewBoxEnergyFeatureFilters = None
            self.commonIndexFilterPlot = 10
            self.commonIndexPlotSignal = 1

    def trouverIndiceValeurLaPlusProche(self,array, value):
        """
        Cette methode retourne l'indice de la liste de la valeur 
        la plus proche de l'argument value.
        """
        array = np.asarray(array)
        idx = (np.abs(array - value)).argmin()
        return idx
            
    def addViewBoxEnergyFeature(self,viewBoxRef):
        self.viewBoxEnergyFeatureFilters=viewBoxRef
    def getViewBoxEnergyFeature(self):
        return self.viewBoxEnergyFeatureFilters
    def addViewBoxFeaturesFilter(self,signalName,filterName,viewBoxReference):
        self.dictViewBoxFeatures[(signalName,filterName)] = viewBoxReference
    
    def getViewBoxRefFeaturesFilter(self,signalName,filterName):
        return self.dictViewBoxFeatures[(signalName,filterName)]

    def clearPlotManager(self):
        self.arrayLinesPlot = []
        self.arrayLinesFilter = {}
        self.commonIndexFilterPlot = 10
        self.commonIndexPlotSignal = 1

    def addElement(self,line):
        self.arrayLinesPlot.append(line)

    def listLinesPlot(self):
        return self.arrayLinesPlot
    
    def addListFeaturesFilter(self,signalName, filter,listObjFeatures):
        #all the features for one filter are added at the very begining
        self.arrayFeaturesFilter.append([signalName, filter,listObjFeatures])
    
    def getFeaturePlotObj(self,signalName, filter,featureName):
        #feature[0] signalName
        #feature[1] filterName
        #feature[2] listFeaturesFilter
        for feature in self.arrayFeaturesFilter:
            if signalName == feature[0] and filter == feature[1]:
                for featureObj in feature[2]:
                    if featureName == featureObj.getNameSignal():
                        return featureObj

    def addElementListFilter(self,key,element,features=[]):
        if not bool(self.arrayLinesFilter):

            self.arrayLinesFilter[key] = [element]

        else:
            if key in self.arrayLinesFilter:
                copyValue = self.arrayLinesFilter[key]
                copyValue.append(element)
                self.arrayLinesFilter[key] = copyValue
            else:
                self.arrayLinesFilter[key] = [element]

    def getListFiltersBySignalName(self,signalName):
        for key in self.arrayLinesFilter.keys():
            if signalName == signalName:
                return self.arrayLinesFilter[key]

    def getLinePlotFilter(self,signal,filterName):
        filterPlots = self.arrayLinesFilter[signal]
        for filterPlot in filterPlots:
            if filterPlot.getNameSignal() == filterName:
                return filterPlot
    
    def getFiltersCurrentSignals(self):
        return list(self.arrayLinesFilter.keys())

    def listLinesFilter(self):
        return self.arrayLinesFilter

    def getPlotFilterByName(self,nameFilter):
        for filter in self.listLinesFilter():
            if filter.getNameSignal() == nameFilter:
                return filter

    def addReferenceNewPlotFilter(self,signal,nameFilter,reference):
        filterPlots = self.arrayLinesFilter[signal]
        for filter in filterPlots:
            if filter.getNameSignal() == nameFilter:
                filter.setLineReference(reference)

    def addReferenceNewPlotFeature(self,signalName,nameFilter,nameFeature,reference):
        #feature[0] signalName
        #feature[1] filterName
        #feature[2] listFeaturesFilter
        for feature in self.arrayFeaturesFilter:
            if signalName == feature[0] and nameFilter == feature[1]:
                for featureObj in feature[2]:
                    if nameFeature == featureObj.getNameSignal():
                        featureObj.setLineReference(reference)

    def addNewViewBoxPlotFilter(self,signal,nameFilter,referenceViewBox):
        filterPlots = self.arrayLinesFilter[signal]
        for filter in filterPlots:
            if filter.getNameSignal() == nameFilter:
                filter.setViewBoxReference(referenceViewBox)

    def addNewViewBoxPlotFeature(self,signalName,nameFilter,nameFeature,referenceViewBox):
        #feature[0] signalName
        #feature[1] filterName
        #feature[2] listFeaturesFilter
        for feature in self.arrayFeaturesFilter:
            if signalName == feature[0] and nameFilter == feature[1]:
                for featureObj in feature[2]:
                    if nameFeature == featureObj.getNameSignal():
                        featureObj.setViewBoxReference(referenceViewBox)


    def addReferenceNewPlot(self,signal,reference):
        for line in self.arrayLinesPlot:
            if line.getNameSignal() == signal:
                line.setLineReference(reference)

    def changePlotStateFeature(self,signalName,nameFilter,nameFeature,value):
        #feature[0] signalName
        #feature[1] filterName
        #feature[2] listFeaturesFilter
        for feature in self.arrayFeaturesFilter:
            if signalName == feature[0] and nameFilter == feature[1]:
                for featureObj in feature[2]:
                    if nameFeature == featureObj.getNameSignal():
                        featureObj.setIsPlotted(value)

    def changePlotState(self,signal,nameFilter,value):
        filterPlots = self.arrayLinesFilter[signal]
        for filter in filterPlots:
            if filter.getNameSignal() == nameFilter:
                filter.setIsPlotted(value)

    def changePlotStateSignal(self,signal,value):
        for line in self.arrayLinesPlot:
            if line.getNameSignal() == signal:
                line.setIsPlotted(value)

    def setCommonIndexFilterPlot(self,value):
        self.commonIndexFilterPlot = value

    def getCommonIndexFilterPlot(self):
        return self.commonIndexFilterPlot

    def setCommonIndexPlotSignal(self,value):
        self.commonIndexPlotSignal = value

    def getCommonIndexPlotSignal(self):
        return self.commonIndexPlotSignal

    def getSingalPlotByName(self,signalName):
        for line in self.arrayLinesPlot:
            if line.getNameSignal() == signalName:
                return line
    
    def getListAllFeatures(self):
        listFeatures = []
        for listFeaturesFilter in self.arrayFeaturesFilter:
            for featurePlotObj in listFeaturesFilter[2]:
                listFeatures.append(featurePlotObj)
        
        return listFeatures

class PlotLine():

    def __init__(self, plotLine, dataX, dataY,currentX,currentY, signal,value,color, isPlotted = True,viewBox=None,axisPlot=None,first_plot=True):
        self.lineReference = plotLine
        self.allDataX = dataX
        self.allDataY = dataY
        self.currentDataPlottedX = currentX
        self.currentDataPlottedY = currentY
        self.signalName = signal
        self.currentValueIndex = value
        self.colorPlot = color
        self.is_plotted = isPlotted
        self.viewBox = viewBox
        self.axis=axisPlot
        self.first_plot= first_plot

    def getAxis(self):
        return self.axis
        
    def setAxis(self,axis):
        self.axis = axis

    def getViewBox(self):
        return self.viewBox
    def getIsPlotted(self):
        return self.is_plotted

    def setIsPlotted(self,value):
        self.is_plotted = value

    def setLineReference(self,reference):
        self.lineReference=reference
    def setViewBoxReference(self,reference):
        self.viewBox = reference
    def getColor(self):
        return self.colorPlot

    def getNameSignal(self):
        return self.signalName

    def getLineReference(self):
        return self.lineReference
    def getAllDataX(self):
        return self.allDataX

    def getAllDataY(self):
        return self.allDataY

    def getCurrentValueIndex(self):
        return self.currentValueIndex

    def setCurrentValueIndex(self,newValue):
        self.currentValueIndex = newValue

    def setCurrentDataPlottedX(self,element):
        self.currentDataPlottedX.append(element)

    def getCurrentDataPlottedX(self):
        return self.currentDataPlottedX

    def setCurrentDataPlottedY(self,element):
        self.currentDataPlottedY.append(element)

    def getCurrentDataPlottedY(self):
        return self.currentDataPlottedY

    def setWholeDataY(self,listY):
        self.currentDataPlottedY = listY

    def setWholeDataX(self,listX):
        self.currentDataPlottedX = listX
