from devices.BaseScope import BaseChannel, BaseWaveForm, BaseWaveFormPreample
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
import sys
import math
import pandas as pd
from dataclasses import make_dataclass
from devices.BaseScope import BaseWaveForm
import lmfit
from lmfit.model import ModelResult
from devices.BaseFitter import FitSine, PhaseEstimator
import subprocess
import json
import os


###### network configure scripts ###### Needs administrator rights to work ######################-
CONFIG_FILE = "config.json"

def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout.strip())
    if result.stderr:
        print(result.stderr.strip())

def load_config():
    CONFIG_FILE_PATH = os.getcwd()+"\\src\\devices\\"+CONFIG_FILE
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

def wf2numpyArray(wf: BaseWaveForm):
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
        | col1 | col2 | col3 | col4 | col5 | col7 | col8 |    
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

def createDFfromWF(wf: BaseWaveForm, format = "scaledOnly"):
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

def addWF2DF(wfToAdd: BaseWaveForm, df: pd.DataFrame):
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


def findAllZC(input: BaseWaveForm):

    ysamp = np.array(input.scaledYdata)
    myZCArray = findAllZCinSampArray(ysamp)
    # to find zero crossings, one need the offset
    return myZCArray

def fitSineParam2Data(waveformSamples, freq_in, fitmethod="basinhopping"):
    """Function for fitting a sine model on actual data.
    Input parameters:
    
    returns: """
    
    pass


#def calcPhaseShiftBetweenSampArrays(signalIn: np.array, signalOut: np.array, 
def findInOutPhaseShift(signalIn: np.array, signalOut: np.array,
                        inTimeArray: np.array, outTimeArray: np.array, freq,
                        method = "zcd", fitmethod = "basinhopping", 
                        ampVal=1, phaseVal = 0, freqVal = 1000, offVal = 0): 
    
        # calcPhaseShiftTo(self, input: 'BaseChannel', targetFreq)
        # 1. get idx of zcd of this channel
    paramValDict ={"method":method, "fittingMethod":fitmethod}
    inParamDict = {"inputParameters":paramValDict}
    if method == "zcd":
        #TODO: 1. reuse basefunctionality, this just copy-paste code! 2. Add falling or rising edge indication
        # 3. check if differences fit with frequency
        #deze functie werkt: getest op 3-9-2025
        inputIdx= findAllZCinSampArray(signalIn)
        outputIdx = findAllZCinSampArray(signalOut)
        #aanpak? 1. inputIdx[0] 2. zoek de eerste outputIdx die groter is dan in punt 1.
        # 1. Op welke plek (dus index) in de array ging wfIn voor het eerst door nul (falling/rising)? antwoord: inputIdx[0]
        # 2. voor welke plekken in de ZC array van wfOut geldt dat deze na inputIdx[0] komen? 
        idxOfFirstZCDinput = inputIdx[0]
        idx_mask = outputIdx >= idxOfFirstZCDinput
        inZCtdata = inTimeArray[inputIdx]
        outZCtdata = outTimeArray[outputIdx]
        outZCDTimeInstance = outZCtdata[idx_mask][0]
        inZCDTimeInstance = inTimeArray[idxOfFirstZCDinput]
            
        #bool_mask = inZCtdata >= outZCtdata[0]
        #inZCtdata = inZCtdata[bool_mask][0]
        diff = inZCDTimeInstance- outZCDTimeInstance
        #diff =  outZCDTimeInstance-inTimeData[idxOfFirstZCDinput]
        #phasedifResDict = {"phasedif":diff*freq*360.0}
        #resultdict={"results": phasedifResDict}
        
        #return {inParamDict, resultdict}
        return diff*freq*360.0
    elif method == "fit":
        if fitmethod not in VALID_METHODS:
            return {None, None}
        estimator = PhaseEstimator(inputSignal=signalIn, 
                                    outputSignal=signalOut,
                                    timeData=inTimeArray,
                                    debugPrint=True)
        phShift = estimator.estimate()
        return phShift
    

def calcPhaseShiftBetweenWFs(wfIn: BaseWaveForm, wfOut: BaseWaveForm, freq, 
                             method = "zcd", fitmethod = "basinhopping", ampVal=1, phaseVal = 0, freqVal = 1000, offVal = 0):    
    """Function for estimating the phase shift between signalOut and signalIn. This function determines the phase change of the output
    with respect to the input. In other words: the phase of the input will be regarded as reference i.e. no phase.
    The phase will be calculated by:
     1. finding the time instances of zero crossings of the input signal
     2. finding the time instances of zero crossings of the output signal
     3. Calculating the time difference between the first zerocrossing in the input and the first subsequent zero crossing of the
     output: timediff = zcd_out - zcd_in
     4. Calculating the estimatie of the phase difference by the formulae: timdiff * freq * 360. 
    
        Parameters 
            signalIn, signalOut: BaseWaveForm objects
            freq : an estimate of the current frequency, needed to calculate the shift, based on the delay between the signals.
            method : a string. Valid options are:
                "zcd" : This is default method. It is a zerocrossing detection algoritm written in software. Fast, simple and 
                        quite stupid, therefore subseptible for noise or signal disturbances. 
                        The algorithm determines the sample-indices of the first zerocrossing in both signal, if present. The indices 
                        will be translated to timeinstances, which will be converted to a phase shift between both signals.
                "fit" : All samples or a convienent slice of the smaples of both waveforms will be used to fit a parameterised 
                        sine_function(x, amp, omega, phase, offset):
                            return amp * np.sin(omega * x + phase) + offset
                        This function will be fitted to both Waveform acquisitions using a configuarable matching method wich will 
                        try to estimate the parameters amp, omega, phase and offset based on the input (sample)array x.
            fitmethod : a string parameter for setting the method used to do the fitting. The following options are avalaible:
                        'least_squares', 'differential_evolution', 'brute', 'basinhopping', 'ampgo', 'nelder', 'lbfgsb', 'powell', 
                        'cg', 'newton', 'cobyla', 'bfgs', 'tnc', 'trust-ncg', 'trust-exact', 'trust-krylov', 'trust-constr', 'dogleg',
                        'slsqp', 'emcee','shgo', 'dual_annealing'. Default selected method is 'basinhopping'           


            return: a float containing the phase difference. """
    #TODO: 1. reuse basefunctionality, this just copy-paste code! 2. Add falling or rising edge indication
    # 3. check if differences fit with frequency
    #deze functie werkt: getest op 3-9-2025
    inTimeData = np.array(wfIn.scaledXdata)
    outTimeData = np.array(wfOut.scaledXdata)
    signalIn = np.array(wfIn.scaledYdata)
    signalOut = np.array(wfOut.scaledYdata)
    phasedif = calcPhaseShiftBetweenSampArrays(signalIn,signalOut, inTimeData, outTimeData, freq, method, fitmethod)
    
    ### OLD CODE starts here ######
    #inputIdx = findAllZC(wfIn)
    #outputIdx = findAllZC(wfOut)
    #aanpak? 1. inputIdx[0] 2. zoek de eerste outputIdx die groter is dan in punt 1.
    # 1. Op welke plek (dus index) in de array ging wfIn voor het eerst door nul (falling/rising)? antwoord: inputIdx[0]
    # 2. voor welke plekken in de ZC array van wfOut geldt dat deze na inputIdx[0] komen? 
    #idxOfFirstZCDinput = inputIdx[0]
    #idx_mask = outputIdx >= idxOfFirstZCDinput
    #inZCtdata = inTimeData[inputIdx]
    #outZCtdata = outTimeData[outputIdx]
    #outZCDTimeInstance = outZCtdata[idx_mask][0]
    #inZCDTimeInstance = inTimeData[idxOfFirstZCDinput]
        
    #bool_mask = inZCtdata >= outZCtdata[0]
    #inZCtdata = inZCtdata[bool_mask][0]
    #diff = inZCDTimeInstance- outZCDTimeInstance
    #diff =  outZCDTimeInstance-inTimeData[idxOfFirstZCDinput]

    return phasedif

def calcPhaseShiftBetweenChan(chanIn: BaseChannel, chanOut: BaseChannel, freq): #input is een channeltype of een MATH type.
    
        # calcPhaseShiftTo(self, input: 'BaseChannel', targetFreq)
        # 1. get idx of zcd of this channel
    mywf1 = chanIn.WF
    mywf2 = chanOut.WF
    
    # 2. get idx of zcd of the input channel
    # 3. As we want to know the phase to the input, the idx value of the input channel must be smaller 
    # than the idx of the zero crossing of this channel.
    myPhaseShift = calcPhaseShiftBetweenWFs(mywf1,mywf2, freq)
    
    return myPhaseShift

def calcPhaseShiftBetweenWFLists(WFList1: list, WFList2: list, freq=1000)->list:
    """"Calculates for each element of both lists, the phaseshift between WFList1 and WFList 2, according phase 2 - phase 2.
    Precondition: WFList1 and WFList2 are both lists of WaveForms."""   
    if len(WFList1) != len(WFList2):
        return None

    phaseList = list()
    index = 0
    for waveform1 in WFList1:
        waveform2 = WFList2.index(index)
        phaseEstimate = calcPhaseShiftBetweenWFs(waveform1, waveform2, freq)
        phaseList.append(phaseEstimate)

    return phaseList

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


def testlmfit():
    
    x = np.linspace(0, 0.005, 201)
    np.random.seed(2)

    #ydat = sine_function(x, 2, 10000, 4.10, 0) + np.random.normal(size=len(x), scale=1)
    ydat = sine_function(x, 2, 1000, math.pi/4, 0) + np.random.normal(size=len(x), scale=0.25)

    model = lmfit.Model(sine_function)
    params = model.make_params(amp={'value': 1.9, 'min': 0, 'max': 2},
                            omega={'value': 0.4, 'min': 0, 'max': 1.0},
                            phase={'value': math.pi/3, 'min': 0.001, 'max': 89.99},
                            offset={'value': 0, 'min': -10, 'max': 10})

    #params = model.make_params(amplitude={'value': 10, 'min': 0, 'max': 1000},
    #                        frequency={'value': 2.0, 'min': 0, 'max': 6.0},
    #                        decay={'value': 2.0, 'min': 0.001, 'max': 12},
    #                        offset=1.0)

    # fit with leastsq
    result0 = model.fit(data=ydat, params=params, x=x, method='leastsq')
    print("# Fit using leastsq:")
    print(result0.fit_report())
    tmp = result0.summary()
    print(tmp)
    method2 = 'basinhopping'
    if len(sys.argv) > 1 and sys.argv[1] in VALID_METHODS:
        method2 = sys.argv[1]


    # fit with other method
    result = model.fit(ydat, params, x=x, method=method2)
    print(f"\n#####################\n# Fit using {method2}:")
    print(result.fit_report())

    # plot comparison
    plt.plot(x, ydat, 'o', label='data')
    plt.plot(x, result0.best_fit, '+', label='leastsq')
    plt.plot(x, result.best_fit, '-', label=method2)
    plt.legend()
    plt.show()


#def sine_decay(x, amplitude, frequency, decay, offset, phase=0):
def sine_decay(x, amplitude, frequency, offset, phase=0):
    #return offset + amplitude * np.sin(x*frequency + phase) * np.exp(-x/decay)
    return offset + amplitude * np.sin(x*frequency + phase)

def testlmfitDecaySine():
    
    x = np.linspace(0, 15.5, 201)
    np.random.seed(2)

    ydat = sine_decay(x, 12.5, 2.0, 1.25,math.pi/3) + np.random.normal(size=len(x), scale=0.40)

    model = lmfit.Model(sine_decay)
    """
    params = model.make_params(amplitude={'value': 10, 'min': 0, 'max': 1000},
                            frequency={'value': 0.1, 'min': 0, 'max': 6.0},
                            decay={'value': 2.0, 'min': 0.001, 'max': 12},
                            offset=0,
                            phase=2)

    """
    
    params = model.make_params(amplitude={'value': 10, 'min': 5, 'max': 100},
                            frequency={'value': 0.9, 'min': 0.5, 'max': 6.0},
                            offset={'value': 0.1, 'min': 0, 'max': 6.0},
                            phase={'value': 2, 'min': 0.5, 'max': 6.0})

    # fit with leastsq
    result0 = model.fit(ydat, params, x=x, method='leastsq')
    print("# Fit using leastsq:")
    print(result0.fit_report())
    tmp = result0.summary()
    schattings = tmp['params']
    print(tmp)

    #method2 = 'basinhopping'
    #method2 = 'brute'
    method2 = 'differential_evolution'
    if len(sys.argv) > 1 and sys.argv[1] in VALID_METHODS:
        method2 = sys.argv[1]


    # fit with other method
    result = model.fit(ydat, params, x=x, method=method2)
    print(f"\n#####################\n# Fit using {method2}:")
    print(result.fit_report())

    # plot comparison
    plt.plot(x, ydat, 'o', label='data')
    plt.plot(x, result0.best_fit, '+', label='leastsq')
    plt.plot(x, result.best_fit, '-', label=method2)
    plt.legend()
    plt.show()