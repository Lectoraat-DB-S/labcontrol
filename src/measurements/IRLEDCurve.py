import pyvisa
import time
import numpy as np
import matplotlib.pyplot as plt
from devices.siglent.spd.PowerSupply import SiglentPowerSupply
from devices.siglent.sdm.DigitalMultiMeter import SiglentDMM
from devices.tektronix.scope import TekScopes
from devices.BaseScope import BaseScope, BaseChannel, BaseVertical,  BaseWaveForm
from devices.BaseSupply import BaseSupply, BaseSupplyChannel
from devices.BaseDMM import BaseDMM
import matplotlib.pyplot as plt

def plotDiodeCurve(xdat, ydat, filename):
    #plt.rcParams['text.usetex'] = True
    
    plt.plot(xdat, ydat, 'o-')
    fig = plt.gcf()
    ax = fig.get_axes()
    plt.title("IR LED $I_d$-$V_d$ karakteristiek")
    plt.xlabel(r'$V_d (V)$')
    plt.ylabel(r'$I_d (A)$')
    plt.grid(True)
    fname = filename + '1'+'.pdf'
    plt.savefig(fname,  dpi=150)
    plt.figure(2)
    plt.plot(xdat, ydat)
    fig = plt.gcf()
    ax = fig.get_axes()
    plt.title("IR LED $I_d$-$V_d$ karakteristiek")
    plt.xlabel(r'$V_d (V)$')
    plt.ylabel(r'$I_d (A)$')
    plt.grid(True)
    fname = filename + '2'+'.pdf'
    plt.savefig(fname,  dpi=150)

    plt.show()
    

def testDiodePlotCurve():
    y =0
    x=0
    Vd= list()
    Id = list()
    for x in np.arange (0, 1.3, 0.01):
        y = np.square(x)
        Vd.append(x)
        Id.append(y)
    
    plotDiodeCurve(Vd,Id, "testplot")

def createCurve():
    WAITTIME = 0.2

    supply:BaseSupply   = BaseSupply.getDevice()
    dmm:BaseDMM         = BaseDMM.getDevice()
    scope:BaseScope     = BaseScope.getDevice()
    Vd= list()
    Id = list()

    VSuppled: BaseSupplyChannel = supply.chan(1)
    VledMeas = scope.vertical.chan(1)

    VSuppled.setV(0)
    VSuppled.enable(True)


    for x in np.arange (0, 1.3, 0.01):
        VSuppled.setV(x)
        time.sleep(WAITTIME)
        ledCurr = dmm.get_current()
        ledVolt = VledMeas.getMean() 
        #bewaar deze meetwaarden
        Vd.append(ledVolt)
        Id.append(ledCurr)

    VSuppled.enable(False)
    plotDiodeCurve(Vd, Id, "irledkarak")
    


