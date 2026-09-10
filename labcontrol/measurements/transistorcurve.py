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


class BJTMEASMODEL(object):
    def __init__(self):
        self.BJTType= "NPN"
        self._scope = None
        self._dmm   = None
        self._supply= None
        self._Rb    = None
        self._Rc    = None
        self._Re    = None
        self.VCCmax = None 
        self.VCCmin = None
        self.VCCstep = None
        self._VCCList: list = None
        self.VBBmax = None 
        self.VBBmin = None
        self.VBBstep = None
        self._VBBList: list = None
        self.VbbFineLevel = None       #the VBB inputlevel value to do smaller step measurements.  
        self.VbbFineStepSize = None    #the stepsize for fine measurement. Above VbbFineLevel this stepsize will be used.
        self.VbbCoarseStep = None      #the stepsize for coarse measurements. Below VbbFineLevel this stepsize will be used.
        self._Vcmeas: list = None       #list holding measured Vc voltage by the scope
        self._Vbmeas: list = None       #list holding scope measured Vb
        self._Icmeas: list = None       #list for holding the DMM measured collector current
        self._Vccmeas: list = None    #list holding Vcc read values of supply
        self._Vbbmeas: list = None    #list holding Vbb read values of supply
        self._WaitTime  = None
        self._measSetup = None # the measurement setup variable defines the measurement circuit: 1. direct 2. Rb & Rc (CE) 3. Rb & Re (CC)

    @property
    def scope(self):
        return self._scope
    
    @scope.setter
    def scope(self, newScope: Scope):
        self._scope = newScope
    
    @property
    def dmm(self):
        return self._dmm
    
    
    @dmm.setter
    def dmm(self, newDmm: BaseDMM):
        self._scope = newDmm
    
    @property
    def supply(self):
        return self._supply

    @supply.setter
    def supply(self, newSupply: BaseSupply):
        self._scope = newSupply
        
    def measInputCharCC():
        """
        Measures the input characteristics with a Common Collector (CC) configuration. In such a setup, VE and VB will be measured. VC equals VCC. Advantage: scope will measure VE directly as it shares its ground with an inpnutsource such as a supply of a signalgenerator. The latter will be connected to GND as the scope. Using a signalgenerator as inputsource, will prevent easy measurement of VC. 
        """
        pass
    
    def doInputCharMeas(self):
        collControl:BaseSupplyChannel = self.supply.chan(1)
        baseControl:BaseSupplyChannel = self.supply.chan(2)
        basechan: Channel = self.scope.vertical.chan(1)
        collchan: Channel = self.scope.vertical.chan(2)
        #set all supply start values.
        collControl.setV(self.VccMax)
        baseControl.setV(self.VbbMin)
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
        
        time.sleep(2*self._WaitTime) #Give circuit some time to stabilize 
        
        VBBsetPoints = list()
        VBBsetPoints.append(np.arange (self.VbbMin, self.VbbFineLevel, self.VbbCoarseStep))
        VBBsetPoints.append(np.arange (self.VbbFineLevel, self.Vbbmax, self.VbbFineStep))

        for x in VBBsetPoints:
            baseControl.setV(x)
            time.sleep(self._WaitTime) # if RB value is low, settling time of IB, IC and VBE is also low.
            val =self. dmm.get_current() 
            self.collCurr.append(val)
            basevolval = basechan.getMean()
            self.Vbmeas.append(basevolval)
            colvolval = collchan.getMean()
            self.Vcmeas.append(colvolval)
                
        #Measurements all done. Disable supply
        collControl.enable(False)  
        baseControl.enable(False)     
        
    def setForIBTarget(self):
        pass 
        
    def doOutputCharMeas(self):
        collControl:BaseSupplyChannel = self.supply.chan(1)
        baseControl:BaseSupplyChannel = self.supply.chan(2)
        basechan: Channel = self.scope.vertical.chan(1)
        collchan: Channel = self.scope.vertical.chan(2)
        #set all supply start values.
        collControl.setV(self.VccMax)
        baseControl.setV(0)
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
        
        
        VCCsetPoints = list()
        VCCsetPoints.append(np.arange ( self.VCCmax, self.VCCmin, -self.VCCstep))
        
        IBsetPoints = list()
        # TODO: create the list
        
        time.sleep(2*self._WaitTime)
        
        for y in VCCsetPoints:
            collControl.setV(y)    
            time.sleep(2*self._WaitTime)
            for x in IBsetPoints:
                self.setForIBTarget(x)
                #Now measure all relevant quantities

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

def measBJTInputChar(VccMin = 0, VccMax = 15, VbbMin = 0, Vbbmax = 0.75, VbbFineLevel = 0.4, VbbFineStep = 0.01, VbbCoarseStep = 0.02,
                 RB=0, RC=0, save2csv: bool = 'False'):
    """Function for extracting the BJT NPN characteristics by measurements.
    Internal variabels:
        Vcmeas  : A list for keeping the collector voltage (Vc), measured by a scope.
        Vbmeas  : A list for keeping the base voltage (Vb), measured by a scope.
        collCurr: A list for keeping the collector current (Ic), measured by dmm.
        Vccmeas : A list for keeping readout values of the VCC supply.
        Vbbmeas : A list for keeping readout values of the VBB supply.
    """
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
    ccurrent = np.array(collCurr)
    basevolt = np.array(Vbmeas)
    collvolt = np.array(Vcmeas)
        
    if RB !=0 and RC != 0:
        myIb = calcCurrent(RB, V1=Vbbmeas, V2=Vbmeas)
        myIc = calcCurrent(RC, V1=Vccmeas, V2=Vcmeas)
        ibCalcCurrent = np.array(myIb)
        icCalcCurrent = np.array(myIc)
        myHFE = np.empty(len(collCurr))
        myHFE = icCalcCurrent/ibCalcCurrent
   
        #convert relevant lists to arrays for doing calucaltions and plotting
        
        retval = (basevolt, collvolt, ccurrent, ibCalcCurrent, icCalcCurrent, myHFE )
        
        #if save2csv == True => create dataframe for easy csv save
        if save2csv:
            df = pd.DataFrame((basevolt,ccurrent,collvolt, ibCalcCurrent, icCalcCurrent,np.array(Vbbmeas), np.array(Vccmeas)))
            df.columns = ["VBE (Scope)", "Ic (DMM)", "VCE (Scope)", f"Ib (calculated Rb={RB})", f"Ic (calculated Rc={RC})", "Readout VBB", "Readout VCC"]
            df.to_csv('hfeNPNBJT.csv', index=False, header=False)   
    else: 
        retval = (basevolt, collvolt, ccurrent)



    return retval
    
def measureBJTOutputChar(IBsetpoints: list, VCERange = (0,30, 0.1), Pmax = 0.1, RB=0, RC=0):
    """Function for measuring the output characteristics of a BJT, based on measuring circuit: TBD.
    For every value in the list IBsetpoints, this script will 
    
    1. measures VC (with E=0 V), VB with a oscilloscope and Ic with a DMM/ampmeter. 
    2. Reads back the values of VCC and VBB
    3. Values of RB and RC for calculating Ib and IC based on VBB, VB, VCC and VC.
    For every VCE in the range VCEmin (default:0 V) to VCEMax(default: 30V) in  a predefined stepsize (0.1 V)
    
    Suggestion: start at VCE max en step down to VCE min.
    Remark: better measurement when base of BJT is connect to a current source or sink, instead of a voltage source.  
    
    
    """
    VCEmin = VCERange[0]
    VCEmax = VCERange[1]
    VCEstep = VCERange[2]
    
    for val in np.arange (VCEmin, VCEmax, VCEstep):
        pass
    
    pass