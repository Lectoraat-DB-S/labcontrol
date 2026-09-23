"""
.. currentmodule:: devices.BaseLabDeviceUtils

========================================
BaseLabDeviceUtils (:mod:`devices.BaseLabDeviceUtils`)
========================================

Provides a convienent functions and classes for Labcontrol.

PhaseFittingProcess Class
=========================
.. autosummary::
    :toctree: generated/

    PhaseFittingProcess

Functions
=========

.. autosummary::
    :toctree: generated/

PhaseFittingProcessProxy Class
==============================
.. autosummary::
    :toctree: generated/

    PhaseFittingProcessProxy

Functions
=========

.. autosummary::
    :toctree: generated/



"""
import traceback
import logging
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
import sys
import math
import pandas as pd
from dataclasses import make_dataclass
import lmfit
from lmfit.model import ModelResult
import subprocess
import json
import os
from multiprocessing import Process, Queue
import multiprocessing

from devices.BaseScope.BaseChannel import WaveForm

logger = logging.getLogger(__name__)

class FitProcessQueueData:
    def __init__(self, amp, freq, phase, offset, xdata, ydata):
        self.amp = amp
        self.freq = freq
        self.phase = phase
        self.offset = offset
        self.xdata = xdata
        self.ydata = ydata
        

class FittingProcess(Process):
    """
    A custom Process class for fitting a parameterized sine function on given data.
    
    A FittingProcess object provides a convenient way of utilizing Python's parallellism capabilities from the multiprocessing package. FittingProcess inherits processing stuff from multiprocessing.Process and combines it with lmfit functionalty for doing fitting of a parameters of an arbitrary function on given input data. The default fit function of FittingProcess is a sine function. and a customized  :func:`run` method, this class offers an easy to use, reusable process object for doing sinewave parameters fitting on sampled data.
    
    Creation:
    
    A FittingProcess object can only be created by using FittingProcess default constructor. The newly created object can be started by used multiprocessing default start() method, which starts the execution FittingProcess implemented :func:`run` method.
    
    Usage:
    A started FittingProcess object communicates through an input and an output queue. To perform a fit, one have to put a FitProcessQueueData object into the input queue of the running FittingProcess, which will start fitting by using lmfit. When fitting completes, FittingProcess puts a lmfit bestvalues dict into the output queue, after which FittingProcess is ready to accept a new fitjob. FittingProcess will break from its run method when it gets a "STOP" string out the input queue.
    
    Advise: use FittingProcessProxy for interfacing with a FittingProcess object.
    """
    
    def __init__(self, name:str = None, inQueue=None, outQueue=None, method = "basinhopping", debugPrint = True):
        """
        FittingProcess initializer.

        Creates a multiprocessing.Process object. 
        
        Creation:
        ---------
        >>> inputQ = multiprocessing.Queue()
        >>> outputQ = multiprocessing.Queue()
        >>> procs = []
        >>> p1 = FittingProcess(args=(inputQ, outputQueue))
        >>> procs.append(p1)
        >>> p1.start()

        Parameters
        ----------
        inQueue : a multiprocessing.Queue(), required
            the input queue object for sending new param and new datastart.
        outQueue : a multiprocessing.Queue(), required
            the output queue object to put the best values of fit in.
        method  : string, optional
            Method to be used by lmfit.fit(). Default value = "basinhopping".
        debugPrint : boolean, optional, default value = True 
            boolean flag for debug printing out. Defaults to True.
        """
        super(FittingProcess, self).__init__()
        self._name = name
        self._inQueue:Queue = inQueue
        self._outQueue:Queue = outQueue
        self.model = lmfit.Model(self.sine_function)
        self.method = method
        self.debug = debugPrint

    def debugPrint(self, msg):
        if self.debug:
            print(f"process with pid={self.pid} says: {msg}")

    @property
    def inQueue(self):
        return self._inQueue
    
    @inQueue.setter
    def inQueue(self, newInQueue):
        self._inQueue = newInQueue
        
    @property
    def outQueue(self):
        return self._outQueue
    
    @outQueue.setter
    def outQueue(self, newOutQueue):
        self._outQueue = newOutQueue
    
    def sine_function(self, x: float, amp: float, freq: float, phase: float, offset: float):
        """
        Sine function to be used for fitting on sinusoidal data acquired.
        
         Parameters
        -----------
        x : float, required
            Multiple time instances to calculate the function value for. Must be a np.array.
        amp : float, required
            the amplitude.
        freq : float, required 
            the frequency.
        phase : float, required 
            the phase shift.
        offset : float, required
            the (DC) offset.
        return : function value according to the formula: = amp * np.sin((2*np.pi*freq * x) + phase) + offset
        inQueue : a multiprocessing.Queue(), required
            the input queue object for sending new param and new datastart.
        outQueue : a multiprocessing.Queue(), required
            the output queue object to put the best values of fit in.
        method  : string, optional
            Method to be used by lmfit.fit(). Default value = "basinhopping".
        debugPrint : boolean, optional, default value = True 
            boolean flag for debug printing out. Defaults to True.    
        """
        return amp * np.sin((2*np.pi*freq * x) + phase) + offset
    
    def run(self):
        outDict: dict = {}
        logger.info(f"FittingProcess {self.name}, {self.pid} starts running")
        self.debugPrint("run method of PhaseFitting has been started")
        for func  in iter( self.inQueue.get, 'STOP'):
            #API: for doing a new fit, messages must be added to inQueue, both of them are dict():
            # 1. Firstly, the new params needed for lmfit, have to be send by inQueue  this process.
            # 2. Secondly, the new samples will be retrieved from inQueue, so fitting can start. 
            # Presume queue.get() to be blocking if nothing is in queue.
            try:
                outDict.clear()
                self.debugPrint("got some data from the queue")
                mydat:FitProcessQueueData = func[0]    # get the fitdata from inQueue
                #Give lmfit new params
                myNewParam = self.model.make_params(amp={'value': mydat.amp, 'min': 0.95*mydat.amp, 'max': 1.05*mydat.amp, 'vary': True},
                                freq={'value': mydat.freq, 'min': 0.9*mydat.freq, 'max': 1.1*mydat.freq, 'vary': True},
                                phase={'value': mydat.phase, 'min': -np.pi, 'max': np.pi, 'vary': True},
                                offset={'value': mydat.offset, 'min': -0.1, 'max': +0.1, 'vary': True})
                #get x,y samples out of the newSamplesDict
                newXDat = mydat.xdata
                newYDat = mydat.ydata
                self.debugPrint("Start fitting")
                myResult = self.model.fit(data=newYDat, params=myNewParam, x=newXDat, 
                                        method=self.method)
                #TODO: nu worden alleen de best values in de queue gezet. Mogelijk beter om hele resultaat object van lmfit.model.fit in de queue te zetten, ook al is (veel?) meer bytes dat over moet. Het voordeel is een interface dat meer (lmfit) standaard standaar is, waar enorm veel info uit te halen is. 
                mySummary = myResult.summary()
                myBestVals:dict = mySummary['best_values']
                print(f"Value of fitted amplitude {myBestVals['amp']}, fitter {self.name}, pid ={self.pid}")
                outDict.update(myBestVals)
                
                #finally put the bestvalues from the fit in outQueue.
                self.debugPrint("putting bestvals into queue")
                self.outQueue.put(outDict)
            except Exception as e:
                # Print the exception message
                self.debugPrint(f"An error occurred: {e}")
        
                # Print the full traceback for debugging
                print("Full traceback:")
                traceback.print_exc()
                logger.error(f"FittingProcess ({self.name}, pid = {self.pid}) run into ERROR ={e}. Sending ERROR now.")
                self.outQueue.put("ERROR")
                break    
            logger.info(f"FittingProcess ({self.name}, pid = {self.pid}) finished work. Ready for new input!")
            self.debugPrint("Finished work, ready for accepting new fitjob")
        self.debugPrint("Loop ended. I will be killed soon. Bye Bye!")

class FittingProcessProxy:
    
    """
    A complementary stub for PhaseFittingProcess class. At this moment it resembles class SineFitter as much as possible, for easy integration into PhaseEstimator.
    """
    
    def __init__(self, name:str = None, inQueue=None, outQueue=None, amp=1, freq=1000, phase=0, offset=0, debug=True ):
        self._name = name
        self._inQueue:Queue = inQueue    #This is the input queue of the process
        self._outQueue:Queue = outQueue  #This is the output queue of the process
        #all sine functions parameters
        self._amp = amp
        self._freq = freq
        self._phase = phase
        self._offset = offset
        #result member for storing lmfit result object (future use)
        self._result = None
        #Oscilloscsope related data
        self._WF: WaveForm = None
        self._xdat = None
        self._ydat = None
        #lmfit estimation section
        self._yfit = None # the fitted sine 
        self._fitSummary = None
        self._bestValues = None
        self._bestAmp = 0
        self._bestFreq = 0
        self._bestPhase = 0
        self._bestOffset = 0
        #a flag selecting verbose output.
        self._debugPrint = debug
        
    def sine_function(self, x: float, amp: float, freq: float, phase: float, offset: float):
        """
        Sine function to be used for fitting on sinusoidal data acquired.
        
         Parameters
        -----------
        x : float, required
            Multiple time instances to calculate the function value for. Must be a np.array.
        amp : float, required
            the amplitude.
        freq : float, required 
            the frequency.
        phase : float, required 
            the phase shift.
        offset : float, required
            the (DC) offset.
        return : function value according to the formula: = amp * np.sin((2*np.pi*freq * x) + phase) + offset
        inQueue : a multiprocessing.Queue(), required
            the input queue object for sending new param and new datastart.
        outQueue : a multiprocessing.Queue(), required
            the output queue object to put the best values of fit in.
        method  : string, optional
            Method to be used by lmfit.fit(). Default value = "basinhopping".
        debugPrint : boolean, optional, default value = True 
            boolean flag for debug printing out. Defaults to True.    
        """
        return amp * np.sin((2*np.pi*freq * x) + phase) + offset
    
    @property
    def inQueue(self):
        return self._inQueue
    
    @inQueue.setter
    def inQueue(self, newInQueue):
        if self._debugPrint:
            print("Proxy is setting inQueue")
        self._inQueue = newInQueue
        
    @property
    def outQueue(self):
        return self._outQueue
    
    @outQueue.setter
    def outQueue(self, newOutQueue):
        if self._debugPrint:
            print("Proxy is setting outQueue")
        self._outQueue = newOutQueue
        
    @property
    def model(self):
        return self._model
    
    @property
    def fitSummary(self):
        return self._fitSummary
    
    @fitSummary.setter
    def fitSummary(self, newSummary):
        if newSummary == None:
            return
        else:
            self._fitSummary = newSummary
            self._bestValues = newSummary['best_values']

    @property
    def bestValues(self):
        return self._bestValues
    
    @bestValues.setter
    def bestValues(self, newBestVals):
        if newBestVals == None:
            return
        else:
            self._bestValues = newBestVals
    
    # Best properties
    @property
    def bestAmp(self):
        if self._bestValues == None:
            return None
        self._bestAmp = self._bestValues["amp"] 
        print(f"Proxy {self._name}, bestamp = {self._bestAmp}")
        return self._bestAmp
    
    @property
    def bestFreq(self):
        if self._bestValues == None:
            return None
        self._bestFreq = self._bestValues["freq"] 
        return self._bestValues["freq"]
    
    @property
    def bestPhase(self):
        if self._bestValues == None:
            return None
        self._bestPhase = self._bestValues["phase"]
        return self._bestValues["phase"]
    
    @property
    def bestOffset(self):
        if self._bestValues == None:
            return None
        self._bestOffset = self._bestValues["offset"]
        return self._bestValues["offset"]
    
    @property
    def WF(self):
        return self._WF
    
    @WF.setter
    def WF(self, newWF):
        self._WF = newWF

    @property
    def amp(self):
        return self._amp

    @amp.setter
    def amp(self, newVal):
        """Property for setting the amp parameter of the SineModel. This method also call the makeParam function of this class,
        in order to set the proper lmfit params for doing the fit."""
        self._amp = newVal
        #self.makeParam()
    
    @property
    def phase(self):
        return self._phase

    @phase.setter
    def phase(self, newVal):
        self._phase = newVal
        


    @property
    def offset(self):
        return self._offset 

    @offset.setter
    def offset(self, newVal):
        self._offset = newVal
        
    @property
    def freq(self):
        return self._freq

    @freq.setter
    def freq(self, newVal):
        self._freq = newVal
        
    @property
    def phaseDeg(self):
        return (self._phase*180.0)/math.pi
    
    @property     
    def xdat(self):
        self._xdat = self._WF.scaledXdata
        return self._xdat

    @property     
    def ydat(self):
        self._ydat = self._WF.scaledYdata
        return self._ydat    

    @property     
    def yfit(self):
        myamp = self._bestValues["amp"]
        myfreq = self._bestValues["freq"]
        myphase = self._bestValues["phase"]
        myoffset = self._bestValues["offset"]
        self._yfit = self.sine_function(x=self._xdat,amp=myamp, freq=myfreq, phase=myphase, offset=myoffset)
    
        return self._yfit

    def setData(self, xdata, ydata):
        self._xdat = xdata
        self._ydat = ydata

    def setAPrioriData(self, amp=0, freq=0, phase=0, offset = 0):
        """
        This method sets the first parameters quesses of sine function to be fitparameters.
        This method has to be called first in order to create the correct messages, which will be sent to the process when calling startFitting.
        """
        if self._debugPrint:
            print("Proxy sets a priori data")
        self._amp = amp
        self._freq = freq
        self._phase = phase
        self._offset = offset       

    def startFitting(self):
        """
        Method for combining the 'params' and 'data' dicts into one "message "dict, which will be added to  the inQueue of the associate process of this proxy class. The associate process will get the message dict from its  input queue (inQueue), after it will start the fitting process.        
        """
        fitData = FitProcessQueueData(self.amp, self.freq, self.phase, self.offset, self.xdat, self.ydat)
        if self._debugPrint:
            print("PhaseFittingProcessProxy: Sending FitProcessQueueData to process")
        self._inQueue.put([fitData])

    def makeParam(self):
        print("Not implemented. Use createParamsDict and send it to process by calling startFitting.")

    def endProcess(self):
        if self._debugPrint:
            print("Proxy puts STOP message for process in Queue.")
        self._inQueue.put("STOP")
    
    def getBestValues(self):
        if self._debugPrint:
            print("Proxy getting data from queue")
        bestValDict = self._outQueue.get()
        self._bestValues = bestValDict
        if self._debugPrint:
            print("got bestvaluels from queue, return now.")
        return bestValDict
class MPFitFactorizer(Process):
    """
    This multiprocessing.Process extension is a dedicated process for managing:
    
    1. The creation of queues for doing the necessary communication between all processes.
    2. The creation of all PhaseFitting workerprocesses 
    3. The creation of all PhaseFittingProxy objects for interfacing with all worker processes by putting items in and/or getting items off the queue.
    4. Because this class is a Process by extension, its run() method will live in side a process on a processor, which will, together with other methodes of this class must implements following functionality:
    
        a. Able to accept fitjobs from one client i.e. the labautomation script, without blocking.
        b. Do some booking which fitjobs are processed and which one aren't. E.g. use the frequency setted and if no result is added to it, then result for that fit is pending.
        c. Putting the accepted job as an item onto the processing queues.
        d. If a worker process has completed a fitjob, the results (bestvalues of the fit) must be taken from the result queue and added to the list of result.
        e. The client will signal this class when it likes to have the results of all jobs, which is the same as a kind of quit message.
        f. After receiving the collect for result message, this class waits until all jobs finished, collects all the results, puts them in a list and returns this list to the client. 
         
    """
    
    def run(self):
        """
        pseudo code:
        wacht op een resultaat in één van de resultQueues
        haal item uit betreffende Queue
        Plaats item op juiste plek in resultList
        Begin bovenaan, totdat "STOP"
        """
        pass
    pass        


class SCPIParam(object): 
    """Deze klasse is bedoeld om het beheer van multidim list iets logischer te maken.
    testparam1 = [["ONEMeg","1M", 1e6],["FIFTy",50]]
    testparam2 = [["ONEMeg","1M", 1e6]]
    testparam3 = ["ONEMeg","1M", 1e6]
    Drie 'lists'. len(testparam1) = 2, len(testparam2) = 2, len(testparam3) = 1
    testparam1 en testparam2 zijn twee geneste 'lists', elk elementen uit de hoofdlist is weer een list.
    Benaderen van eerste element van de eerste sublist uit testparam1 kan op de volgende manier:
    (testparam[0])[0], want het eerste element is wederom een list met 3 elementen. De haakjes zijn nodig, want
    de notatie testparam[0][0] hoort meer bij arrays en niet bij list wat Python als een soort van 'tuple' ziet.   
    
    """
    def __init__(self, mySCPIParamsDict=None):
        self.paramsDict:dict = mySCPIParamsDict
        self.paramDictIndex = None
        self.paramList = None
        self.nrOfListsAV = None
        
    def setDict(self, newSCPIParamsDict):
        self.paramsDict = newSCPIParamsDict

    def setIndex(self, myParamIndex:list):
        self.paramDictIndex = myParamIndex
        
    def dim(self, a):
        if not type(a) == list:
            return []
        return [len(a)] + self.dim(a[0]) 
    
    def getNrOfListsInList(self):
        """pre: self.paramList moet gezet zijn"""
        nrOflists = self.dim(self.paramList)
        if len(nrOflists) == 2:
            return nrOflists[0]
        
    def findParam(self, anElement):
        """Bedoeling: zoek de parameter op in een lijst. Hierbij geldt het volgende:
        1. als de param in de lijst met opties zit, dan is het eerste element in de lijst altijd de correcte SCPI schrijfwijze
        2. Soms is de lijst met opties een twee of meer dimensionaal geval, in dat geval is de index (ook zelf een lijst) de 
        referentie naar een lijst waarvan het eerste element de juiste notitatie is.
         """
        nrOfAvLists = self.getNrOfListsInList()
        for y in range(0, nrOfAvLists):
            myParamList = self.paramList[y]
            index = [i for i in range(0, len(myParamList)) if anElement == myParamList[i]]
            if len(index)==1:
                return y, index[0]
            else:
                return None, None
        
    def nrOfElements(self, a):
        nrOflists = self.dim(a)
        if type(nrOflists) == list:
            #als dit een list is, dan is de list multidimensionaal.
            #bijv 2, dan is de eerste is 2. 
            print(len(nrOflists))
            #stel len == 2, dan is nrOfList[0] het aantal rijen. en nrOfList[1] het aantal kolommen
            # stel [1,3] dan is a een list met daarin één list waar dan 3 elementen in zetten.
            nrElements = 0
            for k in range(0, nrOflists[0]):
                suba = a[k]
                if type(suba) == list:
                    nrElements=nrElements+len(a[k])
                else:
                    nrElements = nrElements +1
                            
            return nrElements
        else:
            return nrOflists

    def list2CommandParams(self, dictIndex:list = None)->list:
        """
        scpiList is the index to a SCPI command and the index to corresponding param options  
        For example, if one to set the impedance trigger unit when triggering on an edge, one will need the know the correct 
        SCPI notation of the param. In the edge trigger impedance case, there a two options: 50 of 1e6 Ohms or "FIFTty" and "ONEMeg"
        in correct SCPI notation. For a user to pass equivalent formats of expressing correct values, the PARAM sub-list for setting
        the impedance is given bij de two dim list:  [["ONEMeg","1M", 1e6],["FIFTy",50]]

        This function only returns this list, given the self.paramDictIndex member of the object has been set with a
        SCIPI command reference.  
        """
        if dictIndex == None:
            if self.paramDictIndex != None:
                dictIndex = self.paramDictIndex
            else:
                self.paramDictIndex = dictIndex
            
        if self.paramsDict == None:
            #TODO: is fout dus loggen.
            return None
        
        #scpiList should have a dimension of 1 (one row) and variaring size. If dimension is other than one, return None
        listShape = self.dim(dictIndex)
        if len(listShape) == 1: #als listShape lengte 1 heeft, dan zit er in de list niet nog een list
            listLength = len(dictIndex) #... en dan zijn dit het aantal elementen in de list.
            myParamList:list = None
            hulpvar:dict =self.paramsDict.get(dictIndex[0])
            for i in range(1, listLength-1):
                hulpvar = hulpvar.get(dictIndex[i])
            myParamList = hulpvar.get(dictIndex[(listLength-1)])
            return myParamList
        elif len(listShape) == 2:
            return None
        else:
            return None #TODO: this is an error, better to throw an exception or other way to inform the caller
        
     
        
    def checkParam(self, paramIn = None ): 
        """check if the inputparameter paramIn is in range or not.
        ParamIn: a single input parameter which need to be checked
        SCPIStruct = a list of strings, needed to find a list of valid options for parameters of a complementay scpi command.
        This method checks whether paramIn is a valid option of a scpi command referred to by SCPIStruct.
        If paramIn is a valid option, this method will return the index where paramIn has been found in the list given by 
        SCPIStruct. If paramIn was not te be found in that list, it will return None, stating the invalidity of parameter paramIn. 
        
        Het lastige hier is paramIn, wat verschillende soorten van parameters kan zijn:
        1. een optie zou moeten zijn uit een lijstvan pure string opties. De opties (PARAM) staan in eendimensionale lijst.
        2. idem, maar waar ook numerieke opties bij kunnen.
        3. Als 1. en/of  2. maar dan gaat het om tweedimensionale lijsten. Dat betekent ook direct dat de return ook een lijst 
        zou kunnen zijn, hoeft niet.
        4. een getal dat in een bepaald bereik moet vallen.
        5. één van bovenstaande opties, maar er zijn meerdere paramters (beter losse functie voor maken, checkParams())
        Een voorbeeld: lijst met opties ziet er als dit: [["ONEMeg","1M", 1e6],["FIFTy",50]] 
        """
        #checkTheParam = lambda paramIn, paramOptions: -1 if paramIn not in paramOptions else [i for i in len(paramOptions) if paramIn in paramOptions(i)]
        if self.paramsDict == None:
            #TODO: is fout dus loggen.
            return None
        
        paramList = None
        paramList = self.list2CommandParams(self.paramDictIndex) # zoek de juiste parameter optielijst op.
        if paramList==None:
            return None #TODO: error code of exceptie?
        
        nrOfParamListinList = len(self.dim(paramList))
        #if isinstance(paramIn, int):
        #    #TODO: code de lijst doorzoekt op aanwezigheid van het (integer) getal en de juiste SCPI notatie retourneert.
        #    pass
        #elif isinstance(paramIn, float):
            #TODO: voor float/double zelfde: doorzoeken op gehele getallen en wetenschappelijke notatie met x cijfers.
        #    pass
        #else:
        match nrOfParamListinList:
            case 0:
                return None
            case 1:
                #paramin is een string, maar dat hoeft niet voor myParam accepteer juiste SCPI notatie, maar ook hoofd en kleine letters.
                #kan onderstaande niet soort van automatisch genereerd worden op basis van lengte lijst?    
                nrOfParamOptions = len(paramList)
                myParamOptionsList = paramList
               
                for x in range(0, nrOfParamOptions):
                    myParamOption = myParamOptionsList[x]
                    if type(myParamOption)== type(paramIn) and  paramIn == myParamOption:
                        return myParamOptionsList[0]
                    if type(myParamOption) == str:
                        if type(myParamOption)== type(paramIn) and paramIn.lower() == (myParamOption).lower():
                            return myParamOptionsList[x]
                        #TODO: is onderstaande wel nodig?
                        if type(myParamOption)== type(paramIn) and paramIn.upper() == (myParamOption).upper():
                            return myParamOptionsList[x]
            case _:
                nrOfParamOptions = len(paramList)
                #blijkbaar zit er meer dan lists in deze list. Doorzoek nu elk van de sublijsten op een treffer.
                for k in range(0, nrOfParamOptions):
                    myParamOptionsList = paramList[k]
                    myNrOfOptions = len(paramList[k])
                    index = [i for i in range(0, myNrOfOptions) if type(myParamOptionsList[i])== type(paramIn) and paramIn == myParamOptionsList[i]]
                    if len(index)==1:
                        return myParamOptionsList[0]
                    for x in range(0, myNrOfOptions):
                        myParamOption = myParamOptionsList[x]
                        if type(myParamOption) == str:
                            if type(myParamOption)== type(paramIn) and paramIn.lower() == (myParamOption).lower():
                                return myParamOptionsList[0]
                            #TODO: is onderstaande wel nodig?
                            if type(myParamOption)== type(paramIn) and paramIn.upper() == (myParamOption).upper():
                                return myParamOptionsList[0]
                        
                return None        
        return None #kan eigenlijk niet, maar voor de zekerheid een return None op deze plek.

class SCPICommand(object):

    def __init__(self,  mySCPICommandDict: dict = None, myParamDict: dict = None):
        self.scpiDict:dict = mySCPICommandDict
        self.scpiDictIndex = None
        self.scpiFunc = None
        self.myParam = SCPIParam(myParamDict) # Toevoeging om te onderzoeken of het combineren van scpicomm en scpiparam voordeel heeft

    def setDict(self, newSCPICommandDict):
        self.scpiDict = newSCPICommandDict
    
    def setIndex(self, mySCPICommIndex:list):
        self.scpiDictIndex = mySCPICommIndex
        self.myParam.setIndex(mySCPICommIndex)
    
    def getLambdaFunc(self):
        """A nice function which returns a lambda function for creating the correct SCPI command"""
        if self.scpiDict == None or self.scpiDictIndex == None:
            #TODO: is fout dus loggen.
            return None
        listLength = len(self.scpiDictIndex)
        myfunc = None
        hulpvar:dict =self.scpiDict.get(self.scpiDictIndex[0])
        for i in range(1, listLength-1):
            hulpvar = hulpvar.get(self.scpiDictIndex[i])
            myfunc = hulpvar.get(self.scpiDictIndex[(listLength-1)])
        return myfunc

    def getSCPIStr(self, paramIn=None):
        """"
        Er zijn een aantal situaties bij het constructueren van het SCPI commanda
        1. Een vast (statisch) SCPI commando. Voorbeeld: SCPI["MEASURE"]["meassimplesrc?"](). Dan geldt dat 
        checkedParam == None en de paramIndex is ook nod
            
        2. Een instructie zoals SCPI["MEASURE"]["meassimplesrc"](newSrc), is niet statisch, omdat er een variabele in zit.
        Vaak heeft deze variable een zeer beperkt aantal opties, namelijk één uit de lijst van geldige parameters. In dit geval is
        de checkedParam == None, maar paramIndex bestaat, m.a.w. paramIndex != None
        3. Instructie met 2 variabelen bestaan ook. Waarschijnlijk is dit de situatie dat zowel checkedParam als paramIndex 
        een waarde hebben dus checkedParam != None en paramIndex != None. Maar hoe dit moet is TBD. nu return None."""
        if self.scpiDict == None or self.scpiDictIndex == None:
            #TODO: is fout dus loggen.
            raise TypeError(f"getSCPIStr: No dict or no dictIndex has been set! ")
        
        
        # voor constructie van SCPI commando is alleen een set van indexen nodig
        mylambdaFunc = self.getLambdaFunc()
        if mylambdaFunc is None:
            raise TypeError(f"No lambda function for index: {self.scpiDictIndex} ")
        if paramIn is None:
            return mylambdaFunc()
        else:
            checked = self.myParam.checkParam(paramIn)
            return mylambdaFunc(checked)
        


###### network configure scripts ###### Needs administrator rights to work ######################-
CONFIG_FILE = "config.json"

def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout.strip())
    if result.stderr:
        print(result.stderr.strip())

def load_config():
    CONFIG_FILE_PATH = os.getcwd()+"\\devices\\"+CONFIG_FILE
    with open(CONFIG_FILE_PATH, "r") as f:
        return json.load(f)

def set_static(adapter, ip, mask, gateway, dns):
    print(f"[*] Statisch IP instellen voor {adapter} -> {ip}")
    run_cmd(f'netsh interface ip set address name="{adapter}" static {ip} {mask} {gateway}')
    if dns:
        run_cmd(f'netsh interface ip set dns name="{adapter}" static {dns}')

def set_dhcp(adapter):
    print(f"[*] DHCP instellen voor {adapter}")
    run_cmd(f'netsh interface ip set address name="{adapter}" source=dhcp')
    run_cmd(f'netsh interface ip set dns name="{adapter}" source=dhcp')

def setEthernet():
    print(os.getcwd())
    config = load_config()
    adapter = config.get("adapter", "Ethernet")
    profiles = config["profiles"]

    print("Beschikbare profielen:")
    for i, name in enumerate(profiles.keys(), 1):
        print(f"{i}. {name}")

    choice = input("Kies profielnummer: ")
    try:
        choice = int(choice) - 1
        profile_name = list(profiles.keys())[choice]
    except:
        print("Ongeldige keuze")
        return

    profile = profiles[profile_name]

    if profile["mode"] == "dhcp":
        set_dhcp(adapter)
    elif profile["mode"] == "static":
        set_static(adapter, profile["ip"], profile["mask"], profile.get("gateway", ""), profile.get("dns", ""))
    else:
        print("Onbekende modus in config.")

################ End network configuration scripts #####################



def sine_function(x, amp=1, freq=1000, phase=0, offset=0):
    return amp * np.sin(2*math.pi*freq * x + phase) + offset    

def sine_functionw(x, amp, omega, phase, offset):
    return amp * np.sin(omega * x + phase) + offset

def wf2numpyArray(wf: WaveForm):
    """Utility function to get both set of scaled samples out of a WaveForm.
    returns a tuple: xArray, yArray
    Where xArray = scaled time instances of waveform
    and     yArray = scaled samples from the acquisition."""
    #TODO: move to BaseWaveForm class.
    xArray = np.array(wf.scaledXdata)
    yArray = np.array(wf.scaledYdata)
    return xArray, yArray

def wf2df():
    """
    Function to create a DataFrame out of a WaveForm object i.e. the raw x and y data and their scaled version.
    
    content of DF/file:
    1. Scope or global (horizontal) settings
    2. vertical settings
    3. Data : 4 column raw scaled chan 1 than 4 colom raw scaled chan 2.
    col1 , col2 , col3 , col4 , col5 , col7 , col8     
    date:   dd-mm-yy
    global settings
    ========
    xUnitStr,<TAB>xxxxx
    xincr,<TAB>zzzzz      
    nrOfSamples,<TAB>yyyyy   
    timeDiv,<TAB>xxxxx
    chan 1 settings,<TAB><TAB>chan 2 settings
    chanstr,<TAB>xxxx,chanstr,<TAB>xxxx.
    couplingstr,<TAB>xxxx,<TAB>couplingstr,<TAB>xxxx.
    vDiv,<TAB>xxxx,<TAB>vDiv,<TAB>xxxx.
    xzero,<TAB>xxxx,<TAB>xzero,<TAB>xxxx.
    yzero,<TAB>xxxx,<TAB>yzero,<TAB>xxxx.
    ymult,<TAB>xxxx,<TAB>ymult,<TAB>xxxx.
    yoff,<TAB>xxxx,<TAB>yoff,<TAB>xxxx.
    yUnitStr,<TAB>xxxx,<TAB>yUnitStr,<TAB>xxxx.
    
    <TAB><TAB>data chan 1<TAB><TAB>data chan 2.
    indexNr<TAB>rawX<TAB>rawY<TAB>scaledX<TAB>scaledY<TAB>rawX<TAB>rawY<TAB>scaledX<TAB>scaledY.
    0,<TAB>wwww,<TAB>xxxx,<TAB>yyyy,<TAB>zzzz,<TAB>wwww,<TAB>xxxx,<TAB>yyyy,<TAB>zzzz.
    1,<TAB>wwww,<TAB>xxxx,<TAB>yyyy,<TAB>zzzz,<TAB>wwww,<TAB>xxxx,<TAB>yyyy,<TAB>zzzz.
    ...     ..      ..      ..      ...     ...     ...       ...
    """
    pass

def meas2DF():
    "function to convert a measurement, i.e. a series of acquisitions, to a pandas DataFrame so it can be"
    "written to disk."
    pass

def createDFfromWF(wf: WaveForm, format = "scaledOnly"):
    if format == "scaledOnly":
        xArray, yArray = wf2numpyArray(wf)
        xColHeader = 'time '+ wf.chanstr
        yColHeader = 'output '+ wf.chanstr
        df = pd.DataFrame(xArray, yArray, columns=[xColHeader, yColHeader])
        return df
    elif format == "all":
        pass
        #colNames = wwf2header(wf) #create colHeaders
        #for col in colNames:
        #

def addWF2DF(wfToAdd: WaveForm, df: pd.DataFrame):
    nrOfRows, nrOfCols = df.shape
    myx, myy = wf2numpyArray(wfToAdd)
    if len(nrOfRows) != len(myy):
        return #TODO: add logging or a message
    xHeader = 'time '+ wfToAdd.chanstr
    yHeader = 'output '+ wfToAdd.chanstr
    df.insert(nrOfCols-1, myx, xHeader)
    df.insert(nrOfCols, myy, yHeader)
    

def writeArray2File(theArray, theFileName):
    myListWithCommas= list(theArray)
    #according to fora like stackoverflow, first convert array or list to str, than remove comma
    myListNoCommas = str(myListWithCommas).split(',')
    return list(myListNoCommas)

def addArray2DF(df:pd.DataFrame, theArray, header):
    nrOfRows, nrOfCols = df.shape

    df.insert(nrOfCols-1, theArray, header)

def findAllZCinSampArray(inputSamp: np.array):
                
    # to find zero crossings, one need the offset
        
    offset = np.mean(inputSamp)
    positive = inputSamp > offset
    idx = np.where(np.bitwise_xor(positive[1:], positive[:-1]))[0]
    return idx


def findAllZC(input: WaveForm):

    ysamp = np.array(input.scaledYdata)
    myZCArray = findAllZCinSampArray(ysamp)
    
    return myZCArray



def createBodePlot(wr, logMagnitude, phase):
    #gejat van: https://aleksandarhaber.com/how-to-create-bode-plots-of-transfer-functions-in-python-using-scipy-control-engineering-tutorial/

    # define the subplot matrix and define the size
    fig, ax = plt.subplots(2,1,figsize=(15,8))
    ax[0].semilogx(wr,logMagnitude,color='blue',linestyle='-',linewidth=3)
    #ax[0].set_xlabel("frequency [rad/s]",fontsize=14)
    ax[0].set_ylabel("Magnitude [dB]",fontsize=14)
    ax[0].tick_params(axis='both',labelsize=14)
    ax[0].grid()
    ax[1].semilogx(wr,phase, color='black', linestyle= '-',linewidth=3)
    ax[1].set_xlabel("frequency [rad/s]",fontsize=14)
    ax[1].set_ylabel("Phase [deg]",fontsize=14)
    ax[1].tick_params(axis='both',labelsize=14)
    ax[1].grid()
    fig.savefig('complete.png',dpi=600)
    fig.show()

def testBodePlot():
    tf1=signal.TransferFunction([1,0.1],[1,0.01])
        # start freq exponent

    sFE=-4  # 10^-4
    # end freq exponent
    eFE=1 # 10^1
    N=100

    w=np.logspace(sFE,eFE,num=N,base=10)
    wr, logMagnitude, phase =signal.bode(tf1,w)
    createBodePlot(wr,logMagnitude,phase)


#def sine_decay(x, amplitude, frequency, decay, offset, phase=0):
def sine_decay(x, amplitude, frequency, offset, phase=0):
    #return offset + amplitude * np.sin(x*frequency + phase) * np.exp(-x/decay)
    return offset + amplitude * np.sin(x*frequency + phase)


