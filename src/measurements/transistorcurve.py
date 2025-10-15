import pyvisa
import time
import numpy as np
import matplotlib.pyplot as plt
from devices.siglent.spd.PowerSupply import SiglentPowerSupply
from devices.siglent.sdm.DigitalMultiMeter import SiglentDMM
from devices.siglent.sds.SDS1000.Scopes import SiglentScope
from devices.BaseScope import BaseScope
from devices.BaseSupply import BaseSupply, BaseSupplyChannel
import pandas as pd

WAITTIME = 0.1
INPUTDEV = 1
OUTPUTDEV = 2

def makeCurveWithOnlySupply():
    supp = SiglentPowerSupply()
    baseControl = supp.CH2
    collControl = supp.CH1
    collControl.set_voltage(25)
    time.sleep(0.01)
    baseControl.set_voltage(0)
    time.sleep(0.01)
    collControl.set_current(500e-3)
    baseControl.set_current(10e-3)
    input("druk toets")
    collControl.set_output(True)    
    input("druk toets")
    baseControl.set_output(True)
    time.sleep(0.01)
    base_curr = list()
    coll_curr = list()
    base_vol = list()
    for x in np.arange (0.0, 3, 0.5):
        baseControl.set_voltage(x)
        time.sleep(0.2)
        curr1 = collControl.measure_current()
        time.sleep(0.2)
        coll_curr.append(curr1)
        curr2 = baseControl.measure_current()
        time.sleep(0.2)
        base_curr.append(curr2)
        base_vol.append(baseControl.measure_voltage())
        time.sleep(0.2)
    #maak plot
    collControl.set_output(False)    
    time.sleep(0.1)
    baseControl.set_output(False)
    time.sleep(0.1)
    plt.plot(base_vol,coll_curr)
    plt.show()

def createTransCurve():
    supply = BaseSupply()
    dmm    = SiglentDMM()
    scope  = BaseScope()
    #set supply
    
    supply.chan(1).set_voltage(15)
    supply.chan(2).set_voltage(0)
    supply.chan(1).set_current(1)
    supply.chan(1).set_current(0.5)
   
    
    baseControl = supply.chan(2)
    collControl = supply.chan(1)
    
    baseControl.enable(True)
    collControl.enable(True)
    time.sleep(0.5)
    
        
    coll_vol = list()
    coll_curr = list()
    base_vol = list()
    basechan =  scope.vertical.chan(1)
    collchan = scope.vertical.chan(2)
    
    for x in np.arange (0, 3, 0.1):
        baseControl.set_voltage(x)
        time.sleep(0.5)
        val = dmm.get_current() 
        time.sleep(0.5)
        coll_curr.append(val)
        basevolval = basechan.getMean()
        time.sleep(0.5)
        base_vol.append(basevolval)
        colvolval = collchan.getMean()
        coll_vol.append(colvolval)
        
    
    collControl.set_output(False)  
    baseControl.set_output(False)  
    ccurrent = np.array(coll_curr)
    basevolt = np.array(base_vol)
    collvolt = np.array(coll_vol)
    df = pd.DataFrame((basevolt,ccurrent,collvolt))
    df.to_csv('myarray.csv', index=False, header=False)
    plt.plot(basevolt, ccurrent)
    plt.show()
        

class Measurement(object):
    
    def __init__(self) -> None:
        self.source = None
        self.meas   = None
    
    def setSourceDevice(self, labdevice, config):
        self.source = labdevice
    
    def setMeasDevice (self, labdevice, config):
        self.meas = labdevice
        
    def doSweepMeas(self):
        pass
    
    def doSingleMeas(self, val):
        pass

def setStimulus(var1, var2):
    pass

def getResponse(var):
    pass

def performVoltageSweep(inputvalues:list, INPUTDEV, OUTPUTDEV):
    outputlist = list()
    for item in inputvalues:
        setStimulus(item, INPUTDEV)
        time.sleep(WAITTIME)
        outputlist.append(getResponse(OUTPUTDEV))
    return outputlist

def doIt():
    rm = pyvisa.ResourceManager()
    print(rm.list_resources())
    
    supp = SiglentPowerSupply()
    baseControl = supp.CH2
    collControl = supp.CH1
    collControl.set_voltage(25)
    time.sleep(0.01)
    baseControl.set_voltage(0)
    time.sleep(0.01)
    collControl.set_current(500e-3)
    baseControl.set_current(10e-3)
    input("druk toets")
    collControl.set_output(True)    
    input("druk toets")
    baseControl.set_output(True)
    time.sleep(0.01)
    base_curr = list()
    coll_curr = list()
    base_vol = list()
    for x in np.arange (0.6, 0.70, 0.01):
        baseControl.set_voltage(x)
        time.sleep(0.2)
        curr1 = collControl.measure_current()
        time.sleep(0.2)
        coll_curr.append(curr1)
        curr2 = baseControl.measure_current()
        time.sleep(0.2)
        base_curr.append(curr2)
        base_vol.append(baseControl.measure_voltage())
        time.sleep(0.2)
    #maak plot
    collControl.set_output(False)    
    time.sleep(0.1)
    baseControl.set_output(False)
    time.sleep(0.1)
    plt.plot(base_vol,coll_curr)
    plt.show()
    