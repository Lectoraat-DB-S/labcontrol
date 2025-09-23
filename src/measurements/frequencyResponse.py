import time
import numpy as np
from devices.BaseGenerator import BaseGenerator, BaseGenChannel
from devices.BaseScope import BaseScope, BaseChannel, BaseVertical,  BaseWaveForm
import matplotlib.pyplot as plt
import pandas as pd
import devices.BaseLabDeviceUtils as utils



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
    phaseDiffList = list()
    maxAmpIN = list()
    maxAmpOUT = list()
    measFreqs = list()
    chan1CaptureList = list()
    chan2CaptureList = list()
    startFreq = 50
    stopFreq = 0.5e6
    stepFreq = 10000
    nrOfFreqPerDec = 5
    ### oscilloscoop settings maken ####
    # zet display op YT
    scope.display.format("YT")
    scope.display.persist(0) #persistence off
    # zet display persistence op minimaal
    # zet acquisitie mode op averaging en zet middeling op tenminste 4
    scope.acquisition.mode(acqMode=3) # SET TO AVERAGING
    scope.acquisition.averaging(16)
    # zet de tijdbasis van de scope goed
    # zet de triggersource goed: triggeren op kanaal 1, signaal van de generator.
    # zet, per kanaal de vdiv goed
    # zet , per kanaal de (vertical) coupling goed (ws AC, dan geen offset.)
    # zet de scope triggering coupling goed
    WAITTIME = 100e-3 #tijd om waarden te laten stabiliseren voor doen van meting.
    # step 0: set generator at first freq point + enable
    genChan1.setfreq(startFreq)
    genChan1.setAmp(4)
    scope.acquire("RUN")
    scopeChan1.setVisible(True)
    scopeChan2.setVisible(True)
    scopeChan1.probe(1)
    scopeChan2.probe(1)
    scopeChan1.setVdiv(0.5)
    scopeChan2.setVdiv(0.5)
    scopeChan1.position(0)
    scopeChan2.position(0)
    #scopeChan1.addMeas("FREQuency")
    time.sleep(WAITTIME)
    genChan1.enableOutput(True)
    #scope.acquire(state="STOP", mode="SAMPLE", stopAfter="SEQUENCE")
    myFreqs = gen.createFreqArray(startFreq, stopFreq, nrOfFreqPerDec, 'DEC')
    # step 1: acquire all the data
    #for freq in np.arange (startFreq, stopFreq, stepFreq):
    for freq in myFreqs:
        print(f"huidige frequentie: {freq}")
        measFreqs.append(freq)
        #stel de scoop in op juiste tijdbase en vdiv
        #zorg voor elk kanaal, tenminste 2 hele perioden sinussignaal in beeld
        start = time.time()
        genChan1.setfreq(freq)
        end = time.time()
        #print(f"generator freqzetten kost: {end-start}")
        #set the time base of the scope for two periods atleast.
        divtime = (1/(2*freq))
        scope.horizontal.setTimeDiv(divtime)
        #effe wachten om te stabiliseren
        #time.sleep(WAITTIME)
        #measFreqs.append(scopeChan1.getFrequency())
        #print(scopeChan1.query("MEASUrement?"))
        #print(scopeChan1.query("MEASUrement:IMMed?"))
        #start = time.time()
        signalIn:BaseWaveForm=scopeChan1.capture()
        signalOut:BaseWaveForm=scopeChan2.capture()
        #phasediff= scopeChan2.getPhaseBetween(scopeChan1,freq)
        #end = time.time()
        #print(f"2 maal een capture kost: {end-start}")
        chan1CaptureList.append(signalIn)
        chan2CaptureList.append(signalOut)
        #phaseDiff.append(scopeChan1.getPhaseTo(scopeChan2))
        val1 = scopeChan1.getPkPk()
        val2 = scopeChan2.getPkPk()
        maxAmpIN.append(val1/2)
        maxAmpOUT.append(val2/2)
        phShift = utils.calcPhaseShiftBetweenWFs(signalIn, signalOut, freq, method = "fit", fitmethod="basinhopping",
                                                 ampVal=maxAmpIN, freqVal=freq)
        #dit is nog niet handig: bij fitting kan ik maar 1x een set startwaarden invullen.  
        phaseDiffList.append(phShift)
        scopeChan1.set2_80(val1)
        scopeChan2.set2_80(val2)
        print(f"pkpk waarden. kan1: {val1}, kan2:{val2}")

    voltin = np.array(maxAmpIN, dtype=np.float64)
    voltout = np.array(maxAmpOUT)
    phaseShift = np.array(phaseDiffList)
    f = np.array(measFreqs)
    
    #csv_data =np.stack((voltin, voltout), axis=1)
    #voltin.tofile('xval.csv', sep = ',')
    #voltout.tofile('yval.csv', sep = ',')
    
    
    plt.figure(1)
    plt.plot(f, voltin, f, voltout)
    plt.figure(2)
    plt.loglog(f, voltin, f, voltout)
    plt.figure(3)
    plt.plot(f, phaseShift)
    plt.figure(4)
    plt.semilogx(f, phaseShift)
    plt.show()

    #voor het plotten van een bodeplot.
    #https://aleksandarhaber.com/how-to-create-bode-plots-of-transfer-functions-in-python-using-scipy-control-engineering-tutorial/
        
    
    # step 2: process the data
    #magResp = calcMagnitudeResponse(maxAmpOUT, maxAmpIN)
    #phaseResp = calcPhaseResonse(signalIn, signalOut)
    #fc_min3dB = calcMin3dBFromMagResp(magResp)
    # stap 3: plot the data
