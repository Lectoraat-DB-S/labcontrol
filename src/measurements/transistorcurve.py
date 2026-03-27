import pyvisa
import time
import numpy as np
import matplotlib.pyplot as plt
from devices.siglent.spd.PowerSupply import SiglentPowerSupply
from devices.siglent.sdm.DigitalMultiMeter import SiglentDMM
from devices.siglent.sds.SDS1000.SDS1k import SiglentScope
from devices.BaseSupply import BaseSupply, BaseSupplyChannel
from devices.BaseScope.BaseScope import Scope
from devices.BaseDMM import BaseDMM
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
    for x in np.arange (0.0, 4, 0.75):
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

def measHFECurve(RB=0, RC=0):
    Vcmeas = list()     #list holding measured Vc voltage by the scope
    coll_curr = list()  #list for holding the DMM measured collector current
    Vbmeas = list()     #list holding scope measured Vb
    Vccmeas = list()    #list holding Vcc read values of supply
    Vbbmeas = list()    #list holding Vbb read values of supply
    supply:BaseSupply = BaseSupply.getDevice()
    dmm:BaseDMM = BaseDMM.getDevice()
    scope:Scope = Scope.getDevice()
    #set supply
    
    
    supply.chan(1).setV(15)
    supply.chan(2).setV(0)
    supply.chan(1).setI(1)
    supply.chan(2).setI(0.5)
   
    
    baseControl:BaseSupplyChannel = supply.chan(2)
    collControl:BaseSupplyChannel = supply.chan(1)
    
    baseControl.enable(True)
    collControl.enable(True)
    time.sleep(1)
    
   
    basechan =  scope.vertical.chan(1)
    basechan.setVisible(True)
    collchan = scope.vertical.chan(2)
    collchan.setVisible(True)
    basechan.setVdiv(0.5)
    collchan.setVdiv(5)
    
    
    for x in np.arange (0, 0.4, 0.02):
        baseControl.setV(x)
        time.sleep(0.5)
        val = dmm.get_current() 
        coll_curr.append(val)
        basevolval = basechan.getMean()
        Vbmeas.append(basevolval)
        colvolval = collchan.getMean()
        Vcmeas.append(colvolval)
        Vbbmeas.append(baseControl.measV())
        Vccmeas.append(collControl.measV())
        
    for x in np.arange (0.4, 0.7, 0.01):
        baseControl.setV(x)
        time.sleep(0.5)
        val = dmm.get_current() 
        coll_curr.append(val)
        basevolval = basechan.getMean()
        Vbmeas.append(basevolval)
        colvolval = collchan.getMean()
        Vcmeas.append(colvolval)
        Vbbmeas.append(baseControl.measV())
        Vccmeas.append(collControl.measV())
    
    
    collControl.enable(False)  
    baseControl.enable(False)  
    ccurrent = np.array(coll_curr)
    basevolt = np.array(Vbmeas)
    collvolt = np.array(Vcmeas)
    df = pd.DataFrame((basevolt,ccurrent,collvolt))
    df.to_csv('myarray.csv', index=False, header=False)
    plt.plot(basevolt, ccurrent)
    if RB !=0 and RC != 0:
        calcIB=list() #list holding calculated values of IB
        calcIc=list() #list holding calculated values of IC
    
   