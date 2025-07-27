import time
import numpy as np
from devices.BaseGenerator import BaseGenerator, BaseGenChannel
from devices.BaseScope import BaseScope, BaseChannel, BaseVertical



def measPhaseDiff(a, b) -> list:
    return None

def measMaxAmplitude(a, b) -> list:
    return None

def calcPhaseResonse(phaseDiff):
    return None

def calcMagnitudeResponse(outPut, inPut = None) -> list:
    return None

def calcMin3dBFromMagResp(magResp) -> list:
    return None

def doACSweep():
    scope: BaseScope = BaseScope.getDevice()
    scopeVert: BaseVertical = scope.vertical
    gen: BaseGenerator = BaseGenerator.getDevice()
    genChan1: BaseGenChannel = gen.chan(1)
    scopeChan1: BaseChannel = scopeVert.chan(1)
    scopeChan2: BaseChannel = scopeVert.chan(2)
    signalIn = None     #was list(), maar dat lijkt me erg veel ruimte te kosten.
    signalOut =  None   #idem
    phaseDiff = list()
    maxAmpIN = list()
    maxAmpOUT = list()
    measFreqs = list()
    chan1CaptureList = list()
    chan2CaptureList = list()
    startFreq = 500
    stopFreq = 1e6
    stepFreq = 10000
    # zet de tijdbasis van de scope goed
    # zet de triggersource goed: triggeren op kanaal 1, signaal van de generator.
    # zet, per kanaal de vdiv goed
    # zet , per kanaal de (vertical) coupling goed (ws AC, dan geen offset.)
    # zet de scope triggering coupling goed
    WAITTIME = 100e-3 #tijd om waarden te laten stabiliseren voor doen van meting.
    # step 0: set generator at first freq point + enable
    genChan1.setfreq(startFreq)
    genChan1.setAmp(2)
    scope.acquire("RUN")
    scopeChan1.setVdiv(2)
    #scopeChan1.addMeas("FREQuency")
    time.sleep(WAITTIME)
    
    scopeChan2.setVdiv(0.1)
    genChan1.enableOutput(True)
    #scope.acquire(state="STOP", mode="SAMPLE", stopAfter="SEQUENCE")
    
    # step 1: acquire all the data
    for freq in np.arange (startFreq, stopFreq, stepFreq):
        #stel de scoop in op juiste tijdbase en vdiv
        #zorg voor elk kanaal, tenminste 2 hele perioden sinussignaal in beeld
        start = time.time()
        genChan1.setfreq(freq)
        end = time.time()
        #print(f"generator freqzetten kost: {end-start}")
        #set the time base of the scope for two periods atleast.
        divtime = (1/(10*freq))
        scope.horizontal.setTimeDiv(divtime)
        #effe wachten om te stabiliseren
        #time.sleep(WAITTIME)
        #measFreqs.append(scopeChan1.getFrequency())
        #print(scopeChan1.query("MEASUrement?"))
        #print(scopeChan1.query("MEASUrement:IMMed?"))
        #start = time.time()
        signalIn=scopeChan1.capture()
        signalOut=scopeChan2.capture()
        #end = time.time()
        #print(f"2 maal een capture kost: {end-start}")
        chan1CaptureList.append(signalIn)
        chan2CaptureList.append(signalOut)
        #phaseDiff.append(scopeChan1.getPhaseTo(scopeChan2))
        #maxAmpIN.append(scopeChan1.getPkPk())
        #maxAmpOUT.append(scopeChan2.getPkPk())
        print(f"huidige frequentie: {freq}")
    
    # step 2: process the data
    #magResp = calcMagnitudeResponse(maxAmpOUT, maxAmpIN)
    #phaseResp = calcPhaseResonse(signalIn, signalOut)
    #fc_min3dB = calcMin3dBFromMagResp(magResp)
    # stap 3: plot the data
