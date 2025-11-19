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

def createCurve():
    WAITTIME = 0.1

    supply:BaseSupply   = BaseSupply.getDevice()
    dmm:BaseDMM         = BaseDMM.getDevice()
    scope:BaseScope     = BaseScope.getDevice()
    Vd= list()
    Id = list()

    VSuppled: BaseSupplyChannel = supply.chan(1)
    VledMeas = scope.vertical.chan(1)

    VSuppled.setV(0)
    VSuppled.enable(True)


    for x in np.arange (0, 1.5, 0.05):
        VSuppled.setV(x)
        time.sleep(WAITTIME)
        ledCurr = dmm.get_current()
        ledVolt = VledMeas.getMean() 
        #bewaar deze meetwaarden
        Vd.append(ledVolt)
        Id.append(ledCurr)

    VSuppled.enable(False)
    plt.plot(Vd, Id)
    plt.show()