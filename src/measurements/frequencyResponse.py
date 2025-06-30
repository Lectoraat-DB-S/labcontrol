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

def calcMagnitudeResponse(maxAmps) -> list:
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
    stepFreq = 100
    # zet de tijdbasis van de scope goed
    # zet de triggersource goed: triggeren op kanaal 1, signaal van de generator.
    # zet, per kanaal de vdiv goed
    # zet , per kanaal de (vertical) coupling goed (ws AC, dan geen offset.)
    # zet de scope triggering coupling goed
    WAITTIME = 10e-3 #tijd om waarden te laten stabiliseren voor doen van meting.
    # step 0: set generator at first freq point + enable
    genChan1.setfreq(startFreq)
    genChan1.enableOutput(True)
    # step 1: acquire all the data
    for freq in np.arange (startFreq, stopFreq, stepFreq):
        #stel de scoop in op juiste tijdbase en vdiv
        #zorg voor elk kanaal, tenminste 2 hele perioden sinussignaal in beeld
        genChan1.setfreq(freq)
        #set the time base of the scope for two periods atleast.
        divtime = (1/(2*freq))
        scope.horizontal.setTimeDiv(divtime)
        #effe wachten om te stabiliseren
        time.sleep(WAITTIME)
        measFreqs.append(scopeChan1.getFrequency())
        signalIn=scopeChan1.capture()
        signalOut=scopeChan2.capture()
        chan1CaptureList.append(signalIn)
        chan2CaptureList.append(signalOut)
        phaseDiff.append(scopeChan1.getPhaseTo(scopeChan2))
        maxAmpIN.append(scopeChan1.getPkPk())
        maxAmpOUT.append(scopeChan2.getPkPk())
    
    # step 2: process the data
    magResp = calcMagnitudeResponse(maxAmps)
    phaseResp = calcPhaseResonse(signalIn, signalOut)
    fc_min3dB = calcMin3dBFromMagResp(magResp)
    # stap 3: plot the data
