import pyvisa
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import configparser
import os
import socket
import logging
import lmfit
from lmfit.model import ModelResult
import math
import matplotlib.pyplot as plt
from scipy.fft import fft

from devices.BaseConfig import LabcontrolConfig, BaseScopeConfig

logger = logging.getLogger(__name__)

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
    def __init__(self, mySCPIParamsDict):
        self.paramsDict:dict = mySCPIParamsDict
        self.paramDictIndex = None
        self.paramList = None
        self.nrOfListsAV = None

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
        
        
class BaseScope(object):
    """BaseScope: base class for oscilloscope implementation.
        Implementations for oscilloscopes have to inherit from this class:
        1. This base class takes care for subclass auto registration, according to pep487, See:  
        https://peps.python.org/pep-0487/
        2. Implementing subclasses HAVE TO implement the getDevice method of this class, which has subsequent signature:
        @classmethod def getScopeClass.
        3. Be sure BaseScope's constructor has access to the inheriting subclasses during instantion. If not, the
        subclass will not be registated and the correct supply object won't be instantiated. 
        4. Instantion must be done by calling the getDevice method. This method implements a factory kind of scheme. 
    """
    scopeList = []        
    
    def __init_subclass__(cls, **kwargs):
        """Method for auto registration of BaseScope subclasses according to PEP487.
        DO NOT ALTER THIS METHOD NOR TRY TO OVERRIDE IT.
        """
        super().__init_subclass__(**kwargs)
        cls.scopeList.append(cls)
         
    @classmethod
    def getScopeClass(cls, rm, urls, host=None, scopeConfigs: list = None):
        """Method for getting the right type of scope, so it can be created by the runtime.
        This Basescope implementation does nothing other the return the BaseScope type. The inheriting
        subclass should implement the needed logic"""
        pass
    
    @classmethod
    def getDevice(cls,host=None):
        """Method for handling the creation of the correct Scope object, by implementing a factory process. 
        Firstly, this method calls getScopeClass() for getting the right BaseScope derived type. If succesfull, this 
        method, secondly, returns this (class)type together with the needed parameters, to enable
        the Python runtime to create and initialise the object correctly.
        DON'T TRY TO CALL THE CONSTRUCTOR OF THIS CLASS DIRECTLY"""
        rm = pyvisa.ResourceManager()
        urls = rm.list_resources()
        myconfigs = LabcontrolConfig().find(cls) # myconfig is a list of config 

        for scope in cls.scopeList:
            scopetype, dev, theConfig = scope.getScopeClass(rm, urls, host, myconfigs)
            if scopetype != None:
                cls = scopetype
                return cls(dev, theConfig)
        logger.warning("Geen oscilloscoop gevonden!")    
        return None # if getDevice can't find an instrument, return None.

    @classmethod
    def SocketConnect(cls, rm:pyvisa.ResourceManager = None, scopeConfig: BaseScopeConfig = None,
                timeOut = 10000, readTerm = '\n', writeTerm = '\n')->pyvisa.resources.MessageBasedResource:
        myConfig: BaseScopeConfig = scopeConfig
        if rm == None:
            return None
        
        if scopeConfig == None:
            return None
        else:
            host = myConfig.IPAddress #property
            mydev: pyvisa.resources.MessageBasedResource = None
            if host == None:
                return None
            try:
                #logger.info(f"Trying to resolve host {host}")
                ip_addr = socket.gethostbyname(host)
                mydev = rm.open_resource("TCPIP::"+str(ip_addr)+"::INSTR")
            except (socket.gaierror, pyvisa.VisaIOError) as error:
                #logger.error(f"Couldn't resolve host {host}")
                return None
            
            mydev = rm.open_resource("TCPIP::"+str(ip_addr)+"::INSTR")
            mydev.timeout = timeOut  # ms
            mydev.read_termination = readTerm
            mydev.write_termination = writeTerm
            return mydev
        #No return needed here. Every path within function returns None or resource.

    
    def __init__(self, visaInstr:pyvisa.resources.MessageBasedResource=None, scopeConfig: BaseScopeConfig = None):
        """This method takes care of the intialisation of a BaseScope object. This implementation leaves most
        datamembers uninitialised. A subclass should therefore override this function and initialise the datamembers. 
        Remark: don't forget to call super().__init()__ if needed!"""
        self.brand = None
        self.model = None
        self.serial = None
        self.firmware = None
        self.visaInstr : pyvisa.resources.MessageBasedResource = visaInstr
        self.horizontal : BaseHorizontal = None
        self.vertical : BaseVertical = None
        self.trigger : BaseTriggerUnit = None
        self.display : BaseDisplay = None
        self.acquisition : BaseAcquisition = None
        self.utility = None
        self.host = None
        self.scpiCommand = None # this member is a ref to a dict() containing all commands known to a device.
        
        self.nrOfHoriDivs = None# maximum number of divs horizontally
        self.nrOfVertDivs = None # maximum number of divs vertically 
        self.visibleHoriDivs = None# number of visible divs on screen
        self.visibleVertDivs = None # number of visible divs on screen
        

        #self.nrOfHoriDivs = scopeConfig.horizontalGrid # maximum number of divs horizontally
        #self.nrOfVertDivs = scopeConfig.verticalGrid # maximum number of divs vertically 
        #self.visibleHoriDivs = scopeConfig.visibleHorizontalGrid # number of visible divs on screen
        #self.visibleVertDivs = scopeConfig.visibleVerticalGrid # number of visible divs on screen
        self.mode = "SW"  #default setting for the data processing, when doing measurements with this scope.
        self._scopeConfig = scopeConfig

    
    #@property 
    def visaInstr(self) -> pyvisa.resources.MessageBasedResource: 
        """Method for getting the reference to this objects VISA resource. 
        The reference to a visaInstrument object will be set by init only. 
        Please don't alter this method or override it when deriving this class.
        """
        return self.visaInstr
    
    def setSCPICommand(self, SCPICommandDict: dict = None, PARAMDict: dict = None):
        self.scpiCommand = SCPICommand(SCPICommandDict, PARAMDict)
    
    def acquire(self):
        pass
    
    def acquire(self, state, mode=None, nrOfAvg=None, stopAfter=None):
        pass

    def setProcMode(self, mode):
        """Sets the processing or measurement mode of this channel to "SW" or "HW". When set to "SW", every subsequent measurement
        request made by this scope or it sibling object will be done in software. 
        When set "HW", the request will be done by the oscilloscope (the hardware). If the actual connected scope doesn't not offer 
        the measurement function requested, the operation will be done in software, to maintain functional consistency for every scopes.
        """
        if mode == "SW" or mode == "HW":
            self.mode = mode    
            self.vertical.setProcMode(self.mode)
    
###################################### BASECHANNEL #########################################################
class BaseChannel(object):
    """BaseChannel: a baseclass for the abstraction of a channel of an oscilloscope.
    All channel implementation have to inherit from this baseclass.
    1. This base class takes care for subclass auto registration, according to pep487, See:  
    https://peps.python.org/pep-0487/
    2. Implementing subclasses HAVE TO fully implement the getChannelClass method of this class.
    3. Be sure this BaseChannel implementation has access to all inheriting subclasses during creation. If not, 
    the subclass won't be registered and creating the needed channel object(s) will fail."""

    channelList = []

    def __init_subclass__(cls, **kwargs):
        """Method for auto registration of BaseChannel subclasses according to PEP487.
        DO NOT ALTER THIS METHOD NOR TRY TO OVERRIDE IT.
        """
        super().__init_subclass__(**kwargs)
        cls.channelList.append(cls)
    
    @classmethod
    def getChannelClass(cls, dev):
        """getChannelClass: factory method for scope channel objects. 
        Remark: this baseclass implementation is empty, must be implemented by the subclass. """
        pass


    def __init__(self, chan_no: int, visaInstr:pyvisa.resources.MessageBasedResource):
        """Method voor initialising this Channel object.
        Remark: if the subclass relies the intialisation done below, don't forget to call super().__init()__ !"""
        self.visaInstr = visaInstr
        self.chanNr = chan_no
        self.name = None
        self.WF = BaseWaveForm()            # the waveform ojbect of this channel
        self.WFP = BaseWaveFormPreample(visaInstr) # the waveformpreamble object for this channel
        self.mode = "SW" # measurements, pkpk for instance, will be performed in software. Set to "HW" when using scope functions 

    def query(self, cmdString):
        return self.visaInstr.query(cmdString)
    
    def write(self, cmdString: str):
        return self.visaInstr.write(cmdString) #returns number of bytes written.

    def writeRaw(self, cmdString:str):
        bytesToWrite = cmdString.encode()
        return self.visaInstr.write_raw(bytesToWrite) #returns the number of bytes written.

    def readRaw(self, nrOfBytes): # nrOfBytes defaults to None, meaning the resource wide set value is set.
        return self.visaInstr.read_raw(size=nrOfBytes)

    
    def setImpedance(self, newImp):
        pass

    def getWaveformPreamble(self):
        """Gets the description of the current waveform (i.e. preamble) of this channel. This BaseChannel implementation 
        is empty. An inheriting subclass will have to implement this method by sending the proper SCPI commands."""
        pass 

    def setCoupling(self, coupling):
        pass

    def getCoupling(self):
        pass
    
    def setVisible(self, state:bool):
        pass

    def isVisible(self):
        pass

    def setProcMode(self, mode = "SW"):
        if mode == "SW" or mode == "HW":
            self.mode = mode
    
    def probe(self, factor):
        pass

    #def probe(self):
    #    pass

    def setProcMode(self, mode):
        """Sets the processing or measurement mode of this channel to "SW" or "HW". When set to "SW", every subsequent measurement request
        will be done in software. When set "HW", the request will be done by the oscilloscope (the hardware). If the scope 
        connect doesn't not offer the measurement requested, the operation will be done in software on the host computer"""
        if mode == "SW" or mode == "HW":
            self.mode = mode    
        
    def capture(self)->'BaseWaveForm':
        """Gets the waveform from the oscilloscope, by initiating a new aqquisition. This BaseChannel implementation 
        is empty. An inheriting subclass will have to implement this method by sending the proper SCPI commands 
        in order to: a. set this channel object as the source for the capture b. get waveform descriptors, c. get the 
        raw data and e. take care for converting the raw data to meaningfull physical quantities and handel the storage 
        it."""
        pass

    def setVdiv(self, value):
        """Sets the vertical sensitivity (i.e. Vdiv) of this channel. This BaseChannel implementation 
        is empty. An inheriting subclass will have to implement this method.
        """
        pass

    def getVdiv(self):
        """Gets the current vertical sensitivity (i.e. Vdiv) of this channel. This BaseChannel implementation 
        is empty. An inheriting subclass will have to implement this method.
        """
        pass

    def position(self):
        """Gets the (vertical) position of this channel with respect to the center graticule. Unit of position is divisions (divs)."""
        pass

    def position(self, pos):
        """"Sets the (vertical) position of this channel with respect to center. Parameter pos is the deviation from center in divisions (divs). 
        A positive value means above center, negative means below center. """
        pass


    def getXzero(self):
        """Gets the vertical offset of this channel on display. This BaseChannel implementation 
        is empty. An inheriting subclass will have to implement this method.
        """
        pass


    def getAvailableMeasurements(self):
        """Gets the available measurements of this oscilloscope. 'Measurements' are build-in, predefined data processing
        functions. Functionality depends on capabilities of a scope. This BaseChannel implementation 
        is empty. An inheriting subclass will have to implement this method.
        """
        pass
    
    def getMean(self):
        """Calculates the mean of the samples of this channels last waveform. 
        This BaseChannel implementation is empty. An inheriting subclass will have to implement this method. 
        Preferable by using the scopes build-in (direct) measurement functionality, but, if not present for the 
        scope instance used, by a software implementation of the derived class.
        """
        pass

    def getMax(self):
        """Calculates or finds the maximum value in this channels last waveform. 
        This BaseChannel implementation is empty. An inheriting subclass will have to implement this method. 
        Preferable by using the scopes build-in (direct) measurement functionality, but, if not present for the 
        scope instance used, by a software implementation of the derived class.
        """
        pass

    def getMin(self):
        """Calculates or finds the minimal value in this channels last waveform. 
        This BaseChannel implementation is empty. An inheriting subclass will have to implement this method. 
        Preferable by using the scopes build-in (direct) measurement functionality, but, if not present for the 
        scope instance used, by a software implementation of the derived class.
        """
        pass

    def getPkPk(self):
        """Calculates or finds the peak-to-peak maximum value in this channels last waveform. 
        This BaseChannel implementation is empty. An inheriting subclass will have to implement this method. 
        Preferable by using the scopes build-in (direct) measurement functionality, but, if not present for the 
        scope instance used, by a software implementation of the derived class.
        """
        if self.mode == "SW":
            maxVal = max(self.WF.scaledYdata)
            minVal = min(self.WF.scaledYdata)
            return maxVal-minVal

    def getPhaseTo(self, input):
        """Calculates the phase difference of this channels last waveform with respect to the input parameter. The
        phase should be calculated by: self.phase - input.phase. 
        This BaseChannel implementation is empty. An inheriting subclass will have to implement this method. 
        Preferable by using the scopes build-in (direct) measurement functionality of the physical scope, but, 
        if not present, by a software implementation of the derived class.
        """
        pass

    def getPhaseTo(self, input:'BaseChannel', freqEstimate=1000):
        if self.mode == 'SW':
            phShift = self.calcPhaseShiftTo(input, freq=freqEstimate)
            return phShift
        else:
            return None
        

    def getFrequency(self):
        """Calculates the frequency of this channels last waveform. 
        This BaseChannel implementation is empty. An inheriting subclass will have to implement this method. 
        Preferable by using the scopes build-in (direct) measurement functionality of the physical scope, but, 
        if not present, by a software implementation of the derived class.
        """
        pass
    
    def getPeriod(self):
        """Measures the time needed for a full periode of this channels last waveform. 
        This BaseChannel implementation is empty. An inheriting subclass will have to implement this method. 
        Preferable by using the scopes build-in (direct) measurement functionality of the physical scope, but, 
        if not present, by a software implementation of the derived class.
        """
        pass

    def configPlot(self, plot: plt):
        """Method for configuring Matplotlib plots, based on the channels preamble data capture. This method
        implements the following base functionality:
        1. Setting x and y axes ranges.
        2. Setting x and y axes units
        3. Setting linear, logplot or loglogplot.
        4. Setting a base title for the plot.
        5. ....?.....
        Pre-condition: 1. waveform captured on this channel (at least once). 2. Matlibplot plot instance created   
        Input parameter : plot. A valid Matplotlib plot handle to be configured.
        Return: a configured plot handle. Plot data has to be supplied and show() to be called."""
        pass
        
    def getConfigPlot(self):
        """Method for getting a configured Matplotlib plot, based on the channels preamble data capture. This method
        implements the following base functionality:
        1. Creating a Matplotlib.pyplot instance
        2. Setting x and y axes ranges.
        3. Setting x and y axes units
        4. Setting linear, logplot or loglogplot.
        5. Setting a base title for the plot.
        6. ....?.....
        Pre-condition: 1. waveform captured on this channel (at least once).    
        Input parameter : None.
        Return: a created and configured plot handle, invisible with no data in it."""
        pass

    def getPlot(self):
        """Method for getting a completely configured plot. This method has the same functionality as getConfigPlot, but 
        this method actually plots the data, based on the current WaveForm of this channel.
        Precondition: waveform available
        Input parameter: None
        return: handle to matplotlib object."""
        pass 

    def clearMeas(self):
        pass

    def addMeas(self, measType):
        pass

    def getAvMeasVals(self):
        pass

    def set2_80(self, val):
        pass

    def findAllZC(self):
        if self.mode == 'SW':
            trace = self.WF
            ysamp = np.array(trace.scaledYdata)
            
            # to find the first zero crossing, one need the offset
            
            offset = np.mean(ysamp)
            positive = ysamp > offset
            idx = np.where(np.bitwise_xor(positive[1:], positive[:-1]))[0]
            return idx
        else:
            return None
        
    def calcPhaseShiftTo(self, input: 'BaseChannel', freq): #input is een channeltype of een MATH type.
        # calcPhaseShiftTo(self, input: 'BaseChannel', targetFreq)
        # 1. get idx of zcd of this channel
        mytdata = np.array(self.WF.scaledXdata)
        inptdata = np.array(input.WF.scaledXdata)
        myIdx = self.findAllZC()
        inputIdx = input.findAllZC()
        myZCtdata = mytdata[myIdx]
        inpZCtdata = inptdata[inputIdx]
        
        bool_mask = myZCtdata >= inpZCtdata[0]
        myZCtdata = myZCtdata[bool_mask][0]
        diff =  myZCtdata-inpZCtdata[0]

        return diff*freq*360.0
        
        # 2. get idx of zcd of the input channel
        # 3. As we want to know the phase to the input, the idx value of the input channel must be smaller 
        # than the idx of the zero crossing of this channel.


    def findFirstZC(self):
        pass

    ########## MATH FUNCTIONALITY (HARDWARE IMPLEMENTATION OF FYSICAL SCOPE) ######################

    def setMath(self, funct2Set):
        pass

    def setSQRT(self):
        pass

    def setIntg(self):
        pass
    
    def setDiff(self):
        pass
        
    def setFFT(self):
        pass

    def toggleFFT(self):
        pass

    def setFFTVpos(self, newPos):
        pass

    def setFFTWin(self, newWindow:str):
       pass

    def setFFTZoom(self, newZoom):
        pass

    def setFFTscale(self, newScale):
        pass

                
############ BaseHorizontal ###########
class BaseHorizontal(object):
    """BaseHorizontal: baseclass implementation of a scope horizontal functionality.
    Implementation of real supplies have to inherit from this class:
    1. This base class takes care for subclass auto registration, according to pep487, See:  
    https://peps.python.org/pep-0487/
    2. Implementing subclasses HAVE TO implement the getHorizontalClass method of this class
    3. Give BaseHorizontal's constructor access to all inheriting subclasses during its instantion. If not, 
    registration of the subclass will fail, which prevents creation of needed Horizontal type kind of object."""
    
    HorizontalList = list()

    def __init_subclass__(cls, **kwargs):
        """Method for auto registration of BaseHorizontal subclasses according to PEP487.
        DO NOT ALTER THIS METHOD NOR TRY TO OVERRIDE IT.
        """
        super().__init_subclass__(**kwargs)
        cls.HorizontalList.append(cls)
    
    @classmethod
    def getHorizontalClass(cls, dev):
        """getHorizontalClass: a factory method for getting the right horziontal type of an oscilloscope. 
        Remark: this baseclass implementation is empty, all logic must be implemented by the subclass. """
        pass
        
          
    def __init__(self, dev:pyvisa.resources.MessageBasedResource= None):
        """This method takes care of the intialisation of a BaseHorizontal object. Subclasses must override this 
        method ,by initialising the datamembers needed. Remark: if the subclass relies on the intialisation done 
        below, don't forget to call super().__init()__ !"""
        self.visaInstr = dev             # default value = None, see param
        self.TB = 0.0                  # current value of timebase, unit sec/div
        self.SR = 0                    # samplerate
        self.POS = 0                   # Horizontal position in screen (of the waveforms)
        self.ZOOM = 0                  # Horizontal magnifying.

    def setRoll(self, flag:bool):
        """Method for setting horizontal roll (true/false). This method should be overridden by the 
        inherting subclass, as this BaseHorizontal implementation is empty."""
        pass       
    
    def getTimeDiv(self):
        """Method for getting available timebase setting. This method should be overridden by the 
        inherting subclass, as this BaseHorizontal implementation is empty."""    
        pass

    def setTimeDiv(self, value):
        """Method for setting a timebase vaule. This method should be overridden by the 
        inherting subclass, as this BaseHorizontal implementation is empty."""    
        pass

    def setDelay(self, val):
        """Sets the main timebase delay. This delay is the time between the trigger event and the 
        delay reference point on the screen. The range of the value is 5000div timebase, 5div timebase]. 
        This method should be overridden by the inherting subclass, as this BaseHorizontal implementation is empty."""
        pass

    def getDelay(self):
        """Method for getting the current set delay of the timebase. This method should be overridden by the 
        inherting subclass, as this BaseHorizontal implementation is empty."""
        pass

    def setRefPos(self, value:int):
        """Method for setting the reference, or zero point, in case of a timebasedelay. This method should be overridden by the 
        inherting subclass, as this BaseHorizontal implementation is empty."""
        pass

    def getRefPos(self):
        """Method for getting the reference, or zero point, in case of a timebasedelay. This method should be overridden by the 
        inherting subclass, as this BaseHorizontal implementation is empty."""
        pass        

    def setWindowZoom(self, state:bool):
        """Method for setting the state of the timebase zoom funcion. This method should be overridden by the 
        inherting subclass, as this BaseHorizontal implementation is empty. """
        pass

    def getWindowZoom(self, state:bool):
        """Gets the current state of the zoomed timebase window: on or off."""
        pass

    def setWindowDelay(self, val):
        """Sets the horizontal position in the zoomed view of the main sweep."""
        pass

    def getWindowDelay(self):
        """Gets the amount of delay set in the Timebase delay window."""
        pass

    def setWindowScale(self, val):
        """Method for setting the zoomed window horizontal scale (sec/div)"""
        pass

    def getWindowScale(self, val):
        """Gets the amount of time/division set for the zoomed timebase."""
        pass
            
###################################### BASECWAVEFORMPREAMBLE ###################################################
class BaseWaveFormPreample(object):
    """BaseWaveFormPreambel: a base class for holding a channels waveform Preambel data.
    Implementation of real scopes have to subclass their waveform implementations from this class. Reason for
    doing so:
    1. This base class takes care for subclass auto registration, according to pep487, See:  
    https://peps.python.org/pep-0487/
    2. Implementing subclasses HAVE TO implement the getDevice method of this class, which has subsequent signature:
    @classmethod 
    def getWaveFormPreableObject(cls, dev):
    3. Be sure BasewaveForm's constructor has access to the inheriting subclass during instantion. If not, the
    subclass will not be registated and the correct supply object won't be instantiated. 
    """
    WaveFormPreambleList = list()

    @classmethod
    def getWaveFormPreableClass(cls, dev:pyvisa.resources.MessageBasedResource=None):
        pass

    def __init_subclass__(cls, **kwargs):
        """Method for auto registration of BaseWaveFormPreamble subclasses according to PEP487.
        DO NOT ALTER THIS METHOD NOR TRY TO OVERRIDE IT.
        """
        super().__init_subclass__(**kwargs)
        cls.WaveFormPreambleList.append(cls)
    

    def __init__(self, dev:pyvisa.resources.MessageBasedResource=None):
        self.visaInstr = dev
        """The preamble here is originally the TekWaveFormPreamble init. This method inits all datamembers to the value None.
        Following data members are set:
        self.nrOfBytePerTransfer   : Number of bytes per sample or in total => check!
        self.nrOfBitsPerTransfer   : Number of bits per sample or in total => check!
        self.encodingFormatStr     : Encoding sting used during transfer, see documentation
        self.binEncodingFormatStr  : Encoding used during transfer, binary, see documentation
        self.binFirstByteStr       : Location of first byte(? Checken!), see documentation
        self.nrOfSamples           : number of samples of acquired waveform
        self.vertMode              : Indicaties YT,XY, or FFT mode
        self.xincr                 : Time between two samples
        self.xzero                 : Location of X=0 on screen horizontally
        self.xUnitStr              : Horizontal axis unit
        self.ymult                 : Vertical gain, or VDIV
        self.yzero                 : Is a value, expressed in YUNits, used to convert waveform record
                                     values to YUNitLocation of Y=0 on screen vertically
        self.yoff                  : Vertical offset in digitizer levels
        self.yUnitStr              : Vertical axis unit
        self.couplingstr           : "AC", "DC" or "GND"
        self.timeDiv               : Amount of time of one horizontal division on screen. Also called 'Timebase' 
        self.acqModeStr            : The sampling system of an oscilloscope has greater range than the horizontal scale. Therefore a scope is capable to take multiple
                                            samples for an acquisition interval. Typical Acquisition modes are 'sample mode', 'peak mode', or 'average(ing)' 
        self.sourceChanStr         : A string indicating the channel of this waveformpreamble, e.g. 'C1' or 'CH1', depending on scope brand or type.
        self.vdiv                  : the amount of vertical displacement per division of the screen.
            
        
        """
        
        self.tdiv                   = None # same as timeDiv => checken!!!
     
        self.nrOfBytePerTransfer    = None #Number of bytes per sample or in total => check!
        self.nrOfBitsPerTransfer    = None #Number of bits per sample or in total => check!
        self.encodingFormatStr      = None #Encoding sting used during transfer, see documentation
        self.binEncodingFormatStr   = None #Encoding used during transfer, binary, see documentation
        self.binFirstByteStr        = None #Location of first byte(? Checken!), see documentation
        self.nrOfSamples            = None #number of samples of acquired waveform
        self.vertMode               = None #Y, XY, or FFT.
        self.xincr                  = None #Time between two samples
        self.xzero                  = None #Location of X=0 on screen horizontally
        self.xUnitStr               = None #Horizontal axis unit
        self.ymult                  = None #Vertical gain, or VDIV
        self.yzero                  = None #Is a value, expressed in YUNits, used to convert waveform record
                                              #  values to YUNitLocation of Y=0 on screen vertically
        self.yoff                   = None #Vertical offset in digitizer levels
        self.yUnitStr               = None #Vertical axis unit
        self.couplingstr            = None #"AC", "DC" or "GND"
        self.timeDiv                = None #Amount of time of one horizontal division on screen. Also called 'Timebase' 
        self.acqModeStr             = None #The sampling system of an oscilloscope has greater range than the horizontal scale. Therefore a scope is capable to take multiple
                                            #samples for an acquisition interval. Typical Acquisition modes are 'sample mode', 'peak mode', or 'average(ing)' 
        self.sourceChanStr          = None #A string indicating the channel of this waveformpreamble, e.g. 'C1' or 'CH1', depending on scope brand or type.
        self.vdiv                   = None #the amount of vertical displacement per division of the screen.
        self.probe                  = None #the probe (attenuation) factor, e.g. 0.1x , 1x or 1000x
        self.bwLimit                = None #Indicites the bw of the scope due to (additional) filtering
        self.recordType             = None #Indicates the semantical content of the waveform acquired. Viable options are: 'SingleSweep, Spectrum, Histogram'. It's not
                                            # a critical parameter, it just add some more info about the meaning of possible purpose of this data.(Siglent)
        self.processing             = None #Indicates pre or post signalprocessing, such as fir, interpolation etc. (Siglent) 


    def toString(self):
        #https://flexiple.com/python/print-object-attributes-python
        """
        vars() maakt een dict (of iets wat er op lijkt type(vars) is een of ander proxyding ) van alle datamembers en alle 
        functies van een object. Het is een van de built-in introspectie functies van Python. 
        De functies van het object beginnen met 2 underscores, dus moet je alle keys van de dict waar een twee underscores 
        achter elkaar in staan, eruit gooien. De waardes in de datamembers kun je opvragen met vars()[key]
        """
        resStr = ""
        dundrscr = "__"
        dictOfWFP = vars(self)
        for member in dictOfWFP:
            if dundrscr not in member:
                memVal = dictOfWFP[member]
                resStr += f"{member},\t{memVal}`n"
        return resStr
    
    def toString(self, otherWFP: 'BaseWaveFormPreample'):
        """Method to convert this WaveFormPreample and the otherWPF to a string representatie, which can be saved to disk or
        might be send by a stream."""
        #TODO: check which WFP is chan1 and check if both WFP has same elements.
        resStr = ""
        dundrscr = "__"
        dictOfWFP1 = vars(self)
        dictofWFP2 = vars(otherWFP)
        for member in dictOfWFP1:
            if dundrscr not in member:
                resStr += f"{member},\t{dictOfWFP1[member]},\t{member},\t{dictofWFP2[member]}.\n"
        return resStr
    
    def queryPreamble(self):
        """Method for getting the preamble of the scope and set the correct data members
        of a preamble. This baseclass has no implementation."""
        pass
        
######################################## BASEWAVEFORM #########################################################
class BaseWaveForm(object):
    """BaseWaveForm: a base class for holding a channels waveform data.
    Implementation of real scopes have to subclass their waveform implementations from this class. Reason for
    doing so:
    1. This base class takes care for subclass auto registration, according to pep487, See:  
    https://peps.python.org/pep-0487/
    2. Implementing subclasses HAVE TO implement the getWaveFormClass method of this class.
    3. Be sure BasewaveForm's constructor has access to the inheriting subclass during instantion. If not, 
    registration of the subclass will fail and the correct supply object won't be instantiated. 
    """
    
    WaveFormList = list()

    def __init_subclass__(cls, **kwargs):
        """Method for auto registration of BaseWaveForm subclasses according to PEP487.
        DO NOT ALTER THIS METHOD NOR TRY TO OVERRIDE IT.
        """
        super().__init_subclass__(**kwargs)
        cls.WaveFormList.append(cls)

    @classmethod
    def getWaveFormClass(cls):
        pass
        
    def __init__(self):
        """Class for holding waveform data of a channel capture and the methods to transform raw sample data into soming fysical meaningful, such as voltage."""
        self.rawYdata       = None #data without any conversion or scaling taken from scope
        self.rawXdata       = None #just an integer array
        self.scaledYdata    = None #data converted to correct scale e.g units
        self.scaledXdata    = None #An integer array representing the fysical instants of the scaledYData.
        #Horizontal data settings of scope
        self.chanstr        = None
        self.couplingstr    = None
        self.timeDiv        = None # see TDS prog.guide table2-17: (horizontal)scale = (horizontal) secdev 
        self.vDiv           = None # probably the same as Ymult.
        self.xzero          = None # Horizontal Position value. Definition: xzero = 0 => horizontal center of screen.
        self.xUnitStr       = None # unit of X-as/xdata
        self.xincr          = None # multiplier for scaling time data, time between two sample points.
        self.nrOfSamples    = None # the number of points of trace.
        self.yzero          = None 
        self.ymult          = None # vertical step scaling factor. Needed to translate binary value of sample to real stuff.
        self.yoff           = None # vertical offset in V for calculating voltage
        self.yUnitStr       = None
    
    def setWaveForm(self, wfp: BaseWaveFormPreample):
        self.chanstr        = wfp.sourceChanStr
        self.couplingstr    = wfp.couplingstr
        self.timeDiv        = wfp.timeDiv
        self.vDiv           = wfp.vdiv
        self.xzero          = wfp.xzero
        self.xUnitStr       = wfp.xUnitStr
        self.xincr          = wfp.xincr
        self.nrOfSamples    = wfp.nrOfSamples
        self.yzero          = wfp.yzero
        self.yoff           = wfp.yoff
        self.ymult          = wfp.ymult
        self.yUnitStr       = wfp.yUnitStr
    
    def toString(self):
        #https://flexiple.com/python/print-object-attributes-python
        """
        vars() maakt een dict (of iets wat er op lijkt type(vars) is een of ander proxyding ) van alle datamembers en alle 
        functies van een object. Het is een van de built-in introspectie functies van Python. 
        De functies van het object beginnen met 2 underscores, dus moet je alle keys van de dict waar een twee underscores 
        achter elkaar in staan, eruit gooien. De waardes in de datamembers kun je opvragen met vars()[key]
        """
        resStr = ""
        dundrscr = "__"
        dictOfWFP = vars(self)
        for member in dictOfWFP:
            if dundrscr not in member:
                memVal = dictOfWFP[member]
                resStr += f"{member},\t{memVal}\n"
        return resStr
    
    def toDict(self):
        """ chan1Settings = {
        chan1Settings : {"xzero":0}
        }"""
        resStr = ""
        dundrscr = "__"
        dictOfWFP = vars(self)
        myWFSettingsDict = dict()
        for member in dictOfWFP:
            if dundrscr not in member:
                memVal = dictOfWFP[member]
                addDict = dict(member, memVal)
                myWFSettingsDict.update(addDict)
        return myWFSettingsDict
    
    def toDF(self):
        dundrscr = "__"
        dictOfWFP = vars(self)
        myWFSettingsDict = dict()
        for member in dictOfWFP:
            if dundrscr not in member:
                addDict = dict(member, dictOfWFP[member])
                myWFSettingsDict.update(addDict)
        df = pd.DataFrame(myWFSettingsDict)
        return df

    def preamble2DF(self, otherWFP: BaseWaveFormPreample):
        dundrscr = "__"
        dictOfWFP1 = vars(self)
        dictOfWFP2 = vars(otherWFP)
        valList = list()
        myWFSettingsDict = dict()
        for member in dictOfWFP1:
            valList.clear()
            if dundrscr not in member:
                valList.append(dictOfWFP1[member])
                valList.append(dictOfWFP2[member])
                addDict = dict(member, valList)
                myWFSettingsDict.update(addDict)
        df = pd.DataFrame(myWFSettingsDict)
        return df
    
    def toSeries(self, select = "raw"):
        """Converts the samples of this waveform to a Pandas Series object.
        A Series object is a one dimensional np.ndarray, which integrates very nicely within Pandas.
        Parameter select: "raw" (default) or "scaled". 
         raw = only sample sequence numbers and unconverted sample data
         scaled = converted sample data, according the content of the companion WFP. """
        # conversion below should be unnecessary
        xraw = np.array(self.rawXdata)
        yraw = np.array(self.rawYdata)
        scaledx = np.array(self.scaledXdata)
        scaledy = np.array(self.scaledYdata)
        ser = None
        if select == "raw":
            ser = pd.Series(data=self.rawYdata, index=self.rawXdata)
        else:
            ser = pd.Series(data=self.scaledYdata, index=self.scaledXdata)
        
        return ser
    
    def data2DF(self):
        columnNames = ["xraw", "yraw", "xscaled", "yscaled"]
        # conversion below should be unnecessary
        xraw = np.array(self.rawXdata)
        yraw = np.array(self.rawYdata)
        scaledx = np.array(self.scaledXdata)
        scaledy = np.array(self.scaledYdata)
        df = pd.DataFrame(xraw, yraw, scaledx, scaledy, columns=columnNames)
        return df
    
    def WF2DF(self):
        frames = [self.preamble2DF, self.data2DF]
        result = pd.concat(frames)
        return result
    
    def WF2file(self, fullFileName):
        df2Save:pd.DataFrame = self.WF2DF()
        df2Save.to_hdf(fullFileName)

    def toString(self, otherWFP: BaseWaveFormPreample):
        """Method to convert this WaveFormPreample and the otherWPF to a string representatie, which can be saved to disk or
        might be send by a stream."""
        #TODO: check which WFP is chan1 and check if both WFP has same elements.
        resStr = ""
        dundrscr = "__"
        dictOfWFP1 = vars(self)
        dictofWFP2 = vars(otherWFP)
        for member in dictOfWFP1:
            if dundrscr not in member:
                resStr += f"{member},\t{dictOfWFP1[member]},\t{member},\t{dictofWFP2[member]}.\n"
        return resStr
    
###################################### BASETRIGGERUNIT #########################################################
class BaseTriggerUnit(object):
    """New: creation of an object, or instance. 
    Only BaseTriggerUnit may call this new method for creating an object based on the correct type, as a kind
    of factory pattern. To get the right type __new__ will call getTriggerUnitClass methods from every subclass
    known to BaseTriggerUnit
    See also: https://mathspp.com/blog/customising-object-creation-with-__new__ 
    This coding scheme requires (automatic) registration of subclasses according pep487:
    see: https://peps.python.org/pep-0487/      
    """
    triggerUnitList = []

    @classmethod
    def getTriggerUnitClass(cls, vertical:'BaseVertical',visaInstr:pyvisa.resources.MessageBasedResource=None):
        """Method for getting the right Python type, or the proper subclass of BaseTriggerUnit, based on parameters
        passed. 
            """
        pass
    
    def __init_subclass__(cls, **kwargs):
        """Method for autoregistration of BaseTriggerUnit subclasses. Don't alter and don't override. Be sure this
        the"""
        super().__init_subclass__(**kwargs)
        cls.triggerUnitList.append(cls)
        
    def __init__(self, vertical:'BaseVertical'=None, visaInstr:pyvisa.resources.MessageBasedResource=None):
        """This method takes care of the intialisation of a BaseTriggerUnit object. Subclasses must override this 
        method, by initialising the datamembers needed. Remark: if the subclass relies on the intialisation done 
        below, don't forget to call the subcalss' super().__init()__ !"""
        self.vertical :pyvisa.resources.MessageBasedResource = vertical
        self.visaInstr = visaInstr
        self.source = None #the channel to trigger on.
        self.level =None
        
    def level(self):
        pass
        
    def level(self, level):
        pass 
    
    def setSource(self, chanNr):
        pass

    def getEdge(self):
        pass
    
    def setCoupling(self, coup:str):
        pass

    def setSlope(self, slope:str):
        pass
        
    def getFrequency(self):
        pass
        
    def getholdOff(self): #Trigger holdoff blz 215 TRIGger:MAIn:HOLDOff:VALue?
        pass

    def mode(self): #trigger mode blz 216 TRIGger:MAIn:MODe?
        pass

    def mode(self, modeVal):
        pass

    def getState(self): #tigger state zie blz 223 TRIGger:STATE?
        pass

class BaseDisplay(object):
    """BaseDisplay: a baseclass for the abstraction of a Display unit of an oscilloscope.
    All display implementations have to inherit from this baseclass.
    1. This base class takes care for subclass auto registration, according to pep487, See:  
    https://peps.python.org/pep-0487/
    2. Implementing subclasses HAVE TO fully implement the getChannelClass method of this class.
    3. Be sure this BaseChannel implementation has access to all inheriting subclasses during creation. If not, 
    the subclass won't be registered and creating the needed channel object(s) will fail."""

    displayList = []

    def __init_subclass__(cls, **kwargs):
        """Method for auto registration of BaseChannel subclasses according to PEP487.
        DO NOT ALTER THIS METHOD NOR TRY TO OVERRIDE IT.
        """
        super().__init_subclass__(**kwargs)
        cls.displayList.append(cls)
    
    @classmethod
    def getDisplayClass(cls, dev):
        """getChannelClass: factory method for scope channel objects. 
        Remark: this baseclass implementation is empty, must be implemented by the subclass. """
        pass

    def __init__(self, visaInstr:pyvisa.resources.MessageBasedResource):
        """Method voor initialising this Channel object.
        Remark: if the subclass relies the intialisation done below, don't forget to call super().__init()__ !"""
        self.visaInstr = visaInstr

    def format(self):
        pass

    def format(self, mode):
        pass

    def persist(self):
        pass
    
    def persist(self, persmode):
        pass

    
class BaseAcquisition(object):
    """BaseDisplay: a baseclass for the abstraction of a Display unit of an oscilloscope.
    All display implementations have to inherit from this baseclass.
    1. This base class takes care for subclass auto registration, according to pep487, See:  
    https://peps.python.org/pep-0487/
    2. Implementing subclasses HAVE TO fully implement the getChannelClass method of this class.
    3. Be sure this BaseChannel implementation has access to all inheriting subclasses during creation. If not, 
    the subclass won't be registered and creating the needed channel object(s) will fail."""

    acquisitionList = []

    def __init_subclass__(cls, **kwargs):
        """Method for auto registration of BaseChannel subclasses according to PEP487.
        DO NOT ALTER THIS METHOD NOR TRY TO OVERRIDE IT.
        """
        super().__init_subclass__(**kwargs)
        cls.acquisitionList.append(cls)
    
    @classmethod
    def getAcquisitionClass(cls, dev):
        """getChannelClass: factory method for scope channel objects. 
        Remark: this baseclass implementation is empty, must be implemented by the subclass. """
        pass

    def __init__(self, visaInstr:pyvisa.resources.MessageBasedResource):
        """Method voor initialising this Channel object.
        Remark: if the subclass relies the intialisation done below, don't forget to call super().__init()__ !"""
        self.visaInstr = visaInstr

    def mode(self):
        pass

    def mode(self, acqMode):
        pass

    def getNumOfAcquisition(self):
        pass

    def averaging(self):
        pass

    def averaging(self, nrOfAvg):
        pass

    def state(self):
        pass

    def state(self, runMode):
        pass

########## BASEFUNCTION ###########
class BaseFunction(object):
    ADD = {0: "+"}
    SUB = {1: "-"}
    MUL = {2: "*"}
    FFT:dict = {3: "FFT"}
    PHASEFIT = {4: "PHASE"}
    VALIDFUNCTONS:list = [ADD, SUB, MUL, FFT, PHASEFIT]
    def __init__(self, theFunction:dict = None):
        self.functionType = None
        if type(theFunction) != dict or len(theFunction) != 1:
            return
        
        index = [i for i in range(0, len(BaseFunction.VALIDFUNCTONS)) if (list(theFunction.values()))[0] in BaseFunction.VALIDFUNCTONS[i].values()]
        if len(index)>0:
            self.functionType = theFunction

    def setOperands(self, oper1 =  None, oper2 = None):
        pass
            


class BaseFFT(BaseFunction):
    def __init__(self, chan: BaseChannel = None):
        """Inits the BaseFFT.
        param: chan: the (visible) channel of whichthe FFT must be calculated"""
        super().__init__(BaseFunction.FFT)
        self.scopeChan: BaseChannel = chan
        self.freqAxis = None
        self._FFT  = None
        self._freqAxis = None

    @property
    def freqAxis(self):
        if self.scopeChan == None or self.scopeChan.WF == None:
            logger.log(logging.ERROR, "Trying to create FFT frequency array of NoneType, return now... ")
        myfx = np.arange(self.scopeChan.WF.nrOfSamples)
        self._freqAxis = myfx*(1.0/(self.scopeChan.WF.xincr*self.scopeChan.WF.nrOfSamples))
        return self._freqAxis

    @property
    def FFT(self):
        if self.scopeChan == None or self.scopeChan.WF == None:
            logger.log(logging.INFO, "Trying to take the FFT of NoneType, return now... ")
        self._FFT = fft(self.scopeChan.WF.scaledYdata)
        return self._FFT
    
    def setOperands(self, oper1 =  None, oper2 = None):
        if type(oper1) is BaseChannel :
            self.setChan(oper1)

    def setChan(self, newChan: BaseChannel):
        self.scopeChan = newChan
    
    def plot(self, captureFirst: bool = False, linear: bool = False):
        """Convenient function for showing a Matplotlib of this fft"""
        if self.scopeChan == None or self.scopeChan.WF == None:
            logger.log(logging.ERROR, "Trying to plot FFT without source channel set or data")
            return
        if captureFirst:
            self.scopeChan.capture()
        myfig = plt.figure()
        if linear:
            plt.plot(self.freqAxis, np.abs(self.FFT))
        else:
            plt.plot(np.log10(self.freqAxis), np.log10(np.abs(self.FFT)))
        plt.title(f"FFT of Channel {self.scopeChan.name}")
        axs = myfig.get_axes()
        axs[0].set_xlabel("frequency [Hz]")
        axs[0].set_ylabel("|X(f)|")
        axs[0].grid(True)

        return myfig
    

    

class BaseSineFitter(object):

    VALID_METHODS = ['least_squares', 'differential_evolution', 'brute',
                    'basinhopping', 'ampgo', 'nelder', 'lbfgsb', 'powell', 'cg',
                    'newton', 'cobyla', 'bfgs', 'tnc', 'trust-ncg', 'trust-exact',
                    'trust-krylov', 'trust-constr', 'dogleg', 'slsqp', 'emcee',
                    'shgo', 'dual_annealing']


    """A class for fitting a model of a sine,"""
    def __init__(self, amp=1, freq=1000, phase=0, offset=0):
        self._amp = amp
        self._freq = freq
        self._phase = phase
        self._offset = offset
        self._model = None
        self._params = None
        self._result = None
        self._method = "basinhopping"
        self._summary = None
        self._bestval = None
        self._WF: BaseWaveForm = None
        self._xdat = None
        self._ydat = None
        self._yfit = None
        #best estimation section
        self._bestAmp = 0
        self._bestFreq = 0
        self._bestPhase = 0
        self._bestOffset = 0

    # Best properties
    @property
    def bestAmp(self):
        if self._bestval == None:
            return None
        return self._bestval["amp"]
    
    @property
    def bestFreq(self):
        if self._bestval == None:
            return None
        return self._bestval["freq"]
    
    @property
    def bestPhase(self):
        if self._bestval == None:
            return None
        return self._bestval["phase"]
    
    @property
    def bestOffset(self):
        if self._bestval == None:
            return None
        return self._bestval["offset"]
    
    

    def sine_function(self, x, amp, freq, phase, offset):
        return amp * np.sin((2*np.pi*freq * x) + phase) + offset

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
        #self.makeParam()


    @property
    def offset(self):
        return self._offset 

    @offset.setter
    def offset(self, newVal):
        self._offset = newVal
        #self.makeParam()   

    @property
    def freq(self):
        return self._freq

    @freq.setter
    def freq(self, newVal):
        self._freq = newVal
        #self.makeParam()

    @property
    def phaseDeg(self):
        return (self.phase*180.0)/math.pi
    
    @property
    def params(self):
       return self._params
       
    @params.setter
    def params(self, fitParams):
        self._params = fitParams

    @property 
    def method(self):
        return self._method
    
    @method.setter
    def method(self, newMethod):
        if newMethod in BaseSineFitter.VALID_METHODS:
            self._method = newMethod

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
        return self._yfit
    

    @yfit.setter     
    def yfit(self, newFitData):
        self._yfit = newFitData
            

    def setData(self, xdata, ydata):
        self._xdat = xdata
        self._ydat = ydata

    def setAPrioriData(self, amp=0, freq=0, phase=0, offset = 0):
        self.amp = amp
        self.freq = freq
        self.phase = phase
        self.offset = offset
    

    def makeParam(self):
        #TODO: check whether 0.95*self will work. Goal: better control over variantion of parameters.
        self.params = self._model.make_params(amp={'value': self.amp, 'min': 0.95*self.amp, 'max': 1.05*self.amp, 'vary': True},
                            freq={'value': self._freq, 'min': 0.01*self._freq, 'max': 1.1*self._freq, 'vary': True},
                            phase={'value': self._phase, 'min': -np.pi, 'max': np.pi, 'vary': True},
                            offset={'value': self._offset, 'min': -0.1, 'max': +0.1, 'vary': True})
        #self.params.create_uvars()
    


    def makeFit(self):
        #self._model = lmfit.Model(self.sine_function, independent_vars=['x'], param_names=['amp', 'freq', 'phase', 'offset'])
        self._model = lmfit.Model(self.sine_function)
        #guess = self.guess_sine_params(self.xdat, self.ydat)
        #guess = self.guess_sine_params_irregular(self.xdat, self.ydat)
        self.makeParam()
        #self.params  = self._model.make_params(**guess)
        #self.params['freq'].set(vary=False)
        #self.params['amp'].set(vary=False)
        #self.params.create_uvars()
        self._result = self._model.fit(data=self.ydat, params=self.params, x=self.xdat, 
                                       method=self.method)
        #print(self._result.fit_report())
        #for name, par in self._result.params.items():
        #    print(name, par.value, par.stderr)
        self._summary = self._result.summary()
        self._bestval = self._summary['best_values']
        self.yfit = self.sine_function(self.xdat, self.bestAmp, self.bestFreq, self.bestPhase, 
                                       self.bestOffset)

    def printFittedParam(self):
        print(f"Value of fitted amp: {self.amp}")
        print(f"Value of fitted freq: {self.freq}")
        print(f"Value of fitted phase: {self.phase}")
        print(f"Value of fitted offset: {self.offset}")

    #TODO: statistische gegevens eruit halen: hoe goed is de fit
    #TODO: beter om het lmfit ingebouwde lmfit sinus model te pakken?
    #TODO: een plot functie om te zin of de fit gelukt is. En op basis daarvan een functie om melding te krijgen als 
    # fit onder en bepaalde grens komt.



class BasePhaseEstimator(BaseFunction):
    
    def __init__(self, inputWF:BaseWaveForm=None, outputWF:BaseWaveForm=None, debugPrint=False):
        super().__init__(BaseFunction.PHASEFIT)
        self._inputFitter = BaseSineFitter()
        self._outputFitter = BaseSineFitter()
        
        self._inputWF = None
        self._input = None
        self._tAxis = None
        self._inputFitter.WF = None

        self._outWF = None
        self._output = None
        self._outputFitter.WF = None

        if inputWF != None:
            self._inputWF = inputWF
            self._input = inputWF.scaledYdata
            self._tAxis = inputWF.scaledXdata
            self._inputFitter.WF = inputWF

        if outputWF != None:
            self._outWF = outputWF
            self._output = outputWF.scaledYdata
            self._outputFitter.WF = outputWF
        
        
        
        self._debug = debugPrint
        self._phaseDiff = None


    @property
    def inputFitter(self):
        return self._inputFitter

    @property
    def outputFitter(self):
        return self._outputFitter

    @property
    def inputWF(self):
        return self._inputWF
    
    @inputWF.setter
    def inputWF(self, inWF: BaseWaveForm):
        if inWF.any() != None:
           self._inputWF = inWF
           self._input = self.inputWF.scaledYdata
           self.inputFitter.WF = inWF

    @property
    def input(self):
        return self._input
    
    @input.setter
    def input(self, signal):
        if signal.any() != None:
           self._input = signal

    @property
    def outputWF(self):
        return self._outWF
    
    @outputWF.setter
    def outputWF(self, outWF: BaseWaveForm):
        if outWF.any() != None:
           self._outWF = outWF
           self._output = self.outputWF.scaledYdata
           self.outputFitter.WF = outWF
    
    @property
    def output(self):
        return self._output
    
    @output.setter
    def output(self, signal):
        if signal.any() != None:
           self._output = signal 
           
    @property
    def tAxis(self):
        return self._tAxis
    
    @tAxis.setter
    def tAxis(self, timeData):
        if timeData != None:
           self._tAxis = timeData 


    @property
    def phaseDiffRAD(self):
        """Returns the phase difference between output en input in rad."""
        #return (self._phaseDiff*180.0)/math.pi
        self._phaseDiff = self._outputFitter.bestPhase - self._inputFitter.bestPhase

        return self._phaseDiff
    
    @property
    def phaseDiffDEG(self):
        self._phaseDiff = self._outputFitter.bestPhase - self._inputFitter.bestPhase

        return (self._phaseDiff*180.0)/math.pi

    def setWFs(self, inWF: BaseWaveForm = None, outWF: BaseWaveForm = None):
        if inWF == None or outWF == None:
            logger.log(logging.WARNING, "Trying to set (one of) estimator WF with a None type")
            return
        self.inputWF = inWF
        self.outputWF = outWF

    def setAPriori(self, ampIn=0, ampOut=0, freq=0, phase=0, offset=0):
        #set input param for lmfit with some known values
        self._inputFitter.setAPrioriData(ampIn,freq,phase,offset)
        self._outputFitter.setAPrioriData(ampOut,freq,phase,offset)

    #def estimate(self, wfIn: BaseWaveForm, wfOut: BaseWaveForm):
    def estimate(self):
        """Estimates the phase difference between input and output, assuming fitparams for both signals have been set."""
        #self._inputFitter.makeParam()
        #self._outputFitter.makeParam()
        #self.inputFitter.setData(xdata=wfIn.scaledXdata, ydata=wfIn.scaledYdata)

        #self.outputFitter.setData(xdata=wfOut.scaledXdata, ydata=wfOut.scaledYdata)
        self._inputFitter.makeFit()
        self._outputFitter.makeFit()
        #self.ph0aseDiff = self._outputFitter.bestPhase - self._inputFitter.bestPhase
        #TODO: check chi squared value or other indication of fit.
        if self._debug:
            # y = A sin (2 pi f t + phi),  waar is een zerocrossing?
            # als sin (x)=0 dus als x =0 mod pi. dus als 2 pi f t = -phi
            # dus als t = -phi/(2 pi f)
            #self.bestAmp, self.bestFreq, self.bestPhase, 
            self.plot()                        
            self.printResults()
            
        return  self._outputFitter.bestPhase - self._inputFitter.bestPhase
    
    def printResults(self):
        print(f"Resultaten fitting")
        print(f"Input: amplitude = {self.inputFitter.bestAmp}\n frequentie = {self.inputFitter.bestFreq}.\n fase = {self.inputFitter.bestPhase}\n" + 
              f"offset = {self.inputFitter.bestOffset}")
        print(f"Output: amplitude = {self.outputFitter.bestAmp}\n frequentie = {self.outputFitter.bestFreq}.\n fase = {self.outputFitter.bestPhase}\n" + 
              f"offset = {self.outputFitter.bestOffset}")
    
    def plotResults(self, title=None):
        if title == None:
            mytitle = "Phase Estimation Result"
        else:
            mytitle = title
        fig, axs = plt.subplots(2)
        fig.suptitle(mytitle)
        axs[0].plot(self._inputFitter.xdat, self._inputFitter.ydat, self._inputFitter.xdat, self._outputFitter.ydat)
        axs[1].plot(self._inputFitter.xdat, self._inputFitter.ydat, self._inputFitter.xdat, self._outputFitter.ydat,
                    self._inputFitter.xdat, self._inputFitter.yfit, self._inputFitter.xdat, self._outputFitter.yfit)
        axs[0].set_title("input data")
        axs[1].set_title("fitted sinefunctions on data")
        #TODO: create new subplot with only fitted function and a grahpical indication of the phaseDiff found.
        return fig, axs

    def plot(self):
        plt.ion()
        #tzc_in = -1* self.inputFitter.bestPhase/(2*math.pi*self.inputFitter.bestFreq)
        #tzc_out = -1* self.outputFitter.bestPhase/(2*math.pi*self.outputFitter.bestFreq)
        x = -1* math.asin (self.inputFitter.bestOffset/self.inputFitter.bestAmp) 
        print(f"x waarde = {x}")
        tzc_in = (x- self.inputFitter.bestPhase)/(2*math.pi*self.inputFitter.bestFreq)
        x = -1* math.asin (self.outputFitter.bestOffset/self.outputFitter.bestAmp) 
        tzc_out = (x- self.outputFitter.bestPhase)/(2*math.pi*self.outputFitter.bestFreq)
        print(f"x waarde = {x}")
        print(f"zero crossing in:{tzc_in}")
        print(f"zero crossing out:{tzc_out}")
        #nfit = self.inputFitter.yfit
        infit = self.inputFitter.yfit
        index = np.where(infit >= 0)
        ## outfit = self.outputFitter.yfit
       # tzc_in = outfit[outfit==0]
        myindex = index[0][0]-1
        #tzc_in = self.inputFitter.xdat[myindex]
        #TODO: onderstaande nog niet correct.
        #plt.figure(1)
        fig = plt.figure(1)
        ax = plt.gca()
        # first plot original input data
        ax.plot(self._inputFitter.xdat, self._inputFitter.ydat, self._inputFitter.xdat, self._outputFitter.ydat,
                    self._inputFitter.xdat, self._inputFitter.yfit, self._inputFitter.xdat, self._outputFitter.yfit)
        
        #markers voor zero crossing
        ax.plot([ tzc_in], 0,'o') #marker for zero cross of input signal
        ax.plot([ tzc_out], [0],'o')
        #ax.plot([0, tzc_out],'o') #marker for zero cross of output signal
        line1y =[0, self.inputFitter.bestAmp*1.2]   
        line1x =[tzc_in, tzc_in]
        line2y =[0, self.inputFitter.bestAmp*1.2]
        line2x =[tzc_out, tzc_out]
        if tzc_out > tzc_in:
            line3x =[tzc_in*0.8, tzc_out*1.2]
        else:
            line3x =[tzc_out*0.8, tzc_in*1.2]
        line3y = [self.inputFitter.bestAmp*1.1, self.inputFitter.bestAmp*1.1]
        ax.plot(line1x,line1y,linestyle=':', color='k') # vertical line from first  zc  
        ax.plot(line2x,line2y,linestyle=':', color='k') # vertical line from second  zc
        ax.plot(line3x,line3y,linestyle=':', color='k') # horizontal line, connecting line1 and line 2
        ax.text(line3x[1], line3y[1] , f'Phase_diff {self.phaseDiffDEG} degrees (estimate)', style='italic',
        bbox={'facecolor': 'red', 'alpha': 0.5, 'pad': 10})
        
        plt.title(f"Sampled & parameterized in- & output waveforms", fontsize=14, fontweight='bold')
        ax.set_xlim(min(self.inputFitter.xdat), max(self.inputFitter.xdat))
        #ax.set_ylim(-1, 1)
        fig.suptitle('With estimated phase', fontsize=11)
        #ax.title.set_text(f"Sampled & parameterized waveforms")
        ax.legend(["sampled input", "sa mple output","fitted input","fitted output"], loc="lower right")
        input(f'Press [Enter] to proceed to the next plot.')
        plt.clf()


########## BASEMATH ###########
class BaseMath(object):
    """A class for holding software defined scopefunctions"""
    def __init__(self):
        self.functions:list = [] # list for holding the function
        self.functions.append(BaseFFT())
        self.functions.append(BasePhaseEstimator())

    def add(self, aFunction: BaseFunction):
        self.functions.append(aFunction)
    
    def remove(self, aFunction: BaseFunction):
        """Removes a function from the BaseVertical list. Called by BaseVertical."""
        pass

    #def get(self, aFunction: BaseFunction):
    #    pass

    def get(self, functionStr: str = None, oper1 = None, oper2 = None):
        # self.functions is a list, which element is a dict. So from every item of the list functions, one wants to have the value of the
        # functionType member of the BaseFunction element in the list
        # So the line of code is: (self.function[i]).values(), because every dict element of list has only one value elemet
        if functionStr == None:
            return
        myFunction:BaseFunction = None
        index = [i for i in range(0, len(self.functions)) if functionStr in self.functions[i].functionType.values()]
        if index != None and len(index)==1:
            myFunction =  self.functions[index[0]]

        if myFunction is None:
            return None
        if oper1 is None:
            return myFunction
        elif oper2 is None:
            myFunction.setOperands(oper1)
        else:
            myFunction.setOperands(oper1, oper2)
        return myFunction
            
            
            
    #def get(self):
    #    return self.functions

    def clear(self):
        "Clears all added functions"
        self.functions.clear()
    
    def visible(self, aFunction: BaseFunction=None, status: bool=True):
        """Defines whether or not the function will be Visible"""
        pass


########## BASEVERTICAL ###########
    
class BaseVertical(object):
    """BaseVertical is a baseclass implementation of the vertical functionality of a scope.
    A Vertical of a real oscilloscope have to inherit from this class
    1. This base class takes care for subclass auto registration, according to pep487, See:  
    https://peps.python.org/pep-0487/
    2. Implementing subclasses HAVE TO implement the getVerticalClass method of this class
    3. Be sure BaseSupply's constructor has access to the inheriting subclass during instantion. If not, the
    subclass will not be registated and the correct supply object won't be instantiated. 
    """
    VerticalList = list()
   
    @classmethod
    def getVerticalClass(cls, dev):
        """getVerticalClass: factory method for getting the right vertical type of an oscilloscope. 
        Remark: this baseclass implementation is empty, must be implemented by the subclass. """
        pass 

    
    def __init_subclass__(cls, **kwargs):
        """Method for auto registration of BaseVertical subclasses according to PEP487.
        DO NOT ALTER THIS METHOD NOR TRY TO OVERRIDE IT.
        """
        super().__init_subclass__(**kwargs)
        cls.VerticalList.append(cls)

  
    def __init__(self, nrOfChan: int = 0, dev:pyvisa.resources.MessageBasedResource = None):
        """This method takes care of the intialisation of a BaseVertical object. Subclass must override this 
        method ,by initialising the datamembers needed. Remark: if the subclass relies on the intialisation done 
        below, don't forget to call super().__init()__ !"""
        self.channels = []          
        self.nrOfChan = nrOfChan       # A virtual Baseclass: so no channels available.
        self.visaInstr = dev             # default value = None, see param
        self.mode = "SW"
        self.math:BaseMath = BaseMath()         

    def addMath(self, newFunction: BaseFunction):
        self.math.add(newFunction)
    
    def getMath(self):
        pass

    def getMath(self, functionStr:str):
        pass

    #def chan(self, chanNr:int):          
    #def chan(self, chanNr)->BaseChannel: 
    #    """Get the channel object based on the number. This method should be overridden by the 
    #    inherting subclass, as this BaseVertical implementation is empty."""
    #    return None
    
    def chan(self, chanNr)->BaseChannel: 
        """Gets a channel, based on its index: 1, 2 etc."""
        try: 
            for  i, val in enumerate(self.channels):
                if (chanNr) in val.keys():
                    return val[chanNr]
        except ValueError:
            print("Requested channel not available")
            return None     
    

    def setProcMode(self, mode):
        """Sets the processing or measurement mode of this channel to "SW" or "HW". When set to "SW", every subsequent measurement request
        will be done in software. When set "HW", the request will be done by the oscilloscope (the hardware). If the scope 
        connect doesn't not offer the measurement requested, the operation will be done in software on the host computer"""
        if mode == "SW" or mode == "HW":
            self.mode = mode
            for  i in range(self.nrOfChan):
                chan:BaseChannel  = self.chan(i+1)
                chan.setProcMode(mode)

