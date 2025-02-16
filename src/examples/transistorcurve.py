import time
import numpy as np
import matplotlib.pyplot as plt
from devices.siglent.spd.PowerSupply import SiglentPowerSupply
from devices.siglent.sdm.DigitalMultiMeter import SiglentDMM
from devices.siglent.sds.Scopes import SiglentScope
import pandas as pd

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
    supply = SiglentPowerSupply()
    dmm    = SiglentDMM()
    scope  = SiglentScope()
    #set supply
    
    supply.CH1.set_voltage(5)
    supply.CH2.set_voltage(0)
    supply.CH1.set_current(1)
    supply.CH2.set_current(0.5)
   
    
    baseControl = supply.CH2
    collControl = supply.CH1
    
    baseControl.set_output(True)
    collControl.set_output(True)
    time.sleep(0.5)
    
        
    coll_vol = list()
    coll_curr = list()
    base_vol = list()
    
    for x in np.arange (0, 3, 0.1):
        baseControl.set_voltage(x)
        time.sleep(0.5)
        val = dmm.get_current() 
        time.sleep(0.5)
        coll_curr.append(val)
        basevolval = scope.CH1.getMean()
        time.sleep(0.5)
        base_vol.append(basevolval)
        colvolval = scope.CH1.getMean()
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