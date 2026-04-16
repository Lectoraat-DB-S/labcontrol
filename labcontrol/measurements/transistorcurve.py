import pyvisa
import time
import numpy as np
import matplotlib.pyplot as plt
from  matplotlib.axes import Axes
from devices.siglent.spd.PowerSupply import SiglentPowerSupply
from devices.siglent.sdm.DigitalMultiMeter import SiglentDMM
from devices.siglent.sds.SDS1000.SDS1k import SiglentScope
from devices.BaseSupply import BaseSupply, BaseSupplyChannel
from devices.BaseScope.BaseScope import Scope
from devices.BaseScope.BaseChannel import Channel
from devices.BaseDMM import BaseDMM
import pandas as pd


INPUTDEV = 1
OUTPUTDEV = 2

def calcCurrent(Rx, V1:list, V2:list)->list:
    """"Berekent een lijst van basisstroomwaarden op basis van lijst van VBE waarden
    en een lijst van VBB waarden en de waarde van de basisweerstand RB."""
    Iout = np.empty(len(V1))
    V1_array = np.array(V1)
    V2_array = np.array(V2)
    Iout = (V1_array - V2_array)/Rx
    Iout_list = list(Iout)
    return Iout_list

def createBJTCharPlots(VBE:list, Ib:list, Ic: list):
    #convert lists to np.array
    basevolt = np.array(VBE)
    IbCurrent = np.array(Ib)
    IcCurrent = np.array(Ic)
    hfeArray = np.empty(len(VBE))
    hfeArray = IcCurrent/IbCurrent

    fig, axs = plt.subplots(2, 2)
    ax11: Axes  = axs[0, 0]
    ax12: Axes  = axs[0, 1] 
    ax21: Axes  = axs[1, 0]
    ax22: Axes  = axs[1, 0]
    ax11.plot(basevolt, IbCurrent)
    ax11.set_title('Input characteristics')
    ax11.set_xlabel("Vbe (V)")
    ax11.set_ylabel("Ib (A)")
   
    ax12.plot(basevolt, IcCurrent)
    ax12.set_title('Transfer characteristics')
    ax12.set_xlabel("Vbe (V)")
    ax12.set_ylabel("Ic (A)")

    ax21.plot(IcCurrent, IbCurrent)
    ax21.set_title('Ic-Ib characteristics')
    ax21.set_xlabel("Ib (A)")
    ax21.set_ylabel("Ic (A)")
    
    ax22.plot(hfeArray)
    ax22.set_title('HFE characteristics')
    ax22.set_ylabel("HFE value")

    return fig, axs




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

def measHFECurve(VccMin = 0, VccMax = 15, VbbMin = 0, Vbbmax = 0.75, VbbFineLevel = 0.4, VbbFineStep = 0.01, VbbCoarseStep = 0.02,
                 RB=0, RC=0, save2csv: bool = 'False'):
    """Function for extracting the BJT NPN characteristics by measurements.
    Internal variabels:
        Vcmeas  : A list for keeping the collector voltage (Vc), measured by a scope.
        Vbmeas  : A list for keeping the base voltage (Vb), measured by a scope.
        collCurr: A list for keeping the collector current (Ic), measured by dmm.
        Vccmeas : A list for keeping readout values of the VCC supply.
        Vbbmeas : A list for keeping readout values of the VBB supply."""
    WAITTIME = 0.5      # Time in seconds to wait before taking measurement after setpoint change. Depends on circuit.
    Vcmeas = list()     #list holding measured Vc voltage by the scope
    Vbmeas = list()     #list holding scope measured Vb
    collCurr = list()  #list for holding the DMM measured collector current
    Vccmeas = list()    #list holding Vcc read values of supply
    Vbbmeas = list()    #list holding Vbb read values of supply
    supply:BaseSupply = BaseSupply.getDevice()
    dmm:BaseDMM = BaseDMM.getDevice()
    scope:Scope = Scope.getDevice()
    
    #get all control needed.   
    collControl:BaseSupplyChannel = supply.chan(1)
    baseControl:BaseSupplyChannel = supply.chan(2)
    basechan: Channel = scope.vertical.chan(1)
    collchan: Channel = scope.vertical.chan(2)
    #set all supply start values.
    collControl.setV(VccMax)
    baseControl.setV(VbbMin)
    collControl.setI(1)
    baseControl.setI(0.5)
   
    #Turn both supply channels on.
    baseControl.enable(True)
    collControl.enable(True)
    #Turn both scope traces on
    basechan.setVisible(True)
    collchan.setVisible(True)
    #set vertical scale for both channels.
    basechan.setVdiv(0.5)
    collchan.setVdiv(5)
    
    time.sleep(2*WAITTIME) #Give circuit some time to stabilize 
    
    VBBsetPoints = list()
    VBBsetPoints.append(np.arange (VbbMin, VbbFineLevel, VbbCoarseStep))
    VBBsetPoints.append(np.arange (VbbFineLevel, Vbbmax, VbbFineStep))

    for x in VBBsetPoints:
        baseControl.setV(x)
        time.sleep(WAITTIME) # if RB value is low, settling time of IB, IC and VBE is also low.
        val = dmm.get_current() 
        collCurr.append(val)
        basevolval = basechan.getMean()
        Vbmeas.append(basevolval)
        colvolval = collchan.getMean()
        Vcmeas.append(colvolval)
            
    #Measurements all done. Disable supply
    collControl.enable(False)  
    baseControl.enable(False)  
        
    if RB !=0 and RC != 0:
        myIb = calcCurrent(RB, V1=Vbbmeas, V2=Vbmeas)
        myIc = calcCurrent(RC, V1=Vccmeas, V2=Vcmeas)
        myHFE = np.empty(len(collCurr))
        myHFE = myIc/myIb
   
    #convert relevant lists to arrays for doing calucaltions and plotting
    ccurrent = np.array(collCurr)
    basevolt = np.array(Vbmeas)
    collvolt = np.array(Vcmeas)
    ibCalcCurrent = np.array(myIb)
    icCalcCurrent = np.array(myIc)
    
    #if save2csv == True => create dataframe for easy csv save
    if save2csv:
        df = pd.DataFrame((basevolt,ccurrent,collvolt, ibCalcCurrent, icCalcCurrent,np.array(Vbbmeas), np.array(Vccmeas)))
        df.columns = ["VBE (Scope)", "Ic (DMM)", "VCE (Scope)", f"Ib (calculated Rb={RB})", f"Ic (calculated Rc={RC})", "Readout VBB", "Readout VCC"]
        df.to_csv('hfeNPNBJT.csv', index=False, header=False)

    #interesting plots for a BJT is: 1. ib vs ic 2, Ic-Vbe, 3. Ib-Vbe, 4. Ic-Vce
    # interesting 'annotations' or 'features' are the tangents of Ic-Vbe and Ib-Vbe at a settable quiescent point.
    # Another suggestions: curvefitting of ib and ic vs VBE (exponential function)
    # Four quadrant plots of BJT characteristics exists, giving easy overview of the transistors properties. Should try to
    # create one.   
    fig, axs = createBJTCharPlots(Vbmeas, myIb, myIc)

    #TODO: When debugging, plots won't show-up. They will show during normal execution.
    # But calling plt.show() within main function does work. Plots appear normally, even with debug. 
    plt.show()