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

from devices.BaseScope.BaseChannel import WaveForm

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

