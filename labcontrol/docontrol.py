
import pyvisa
import logging
#import measurements.weerstandsmetingDMM as measurement
#import measurements.transistorcurve as curfje

import curvefitting.RLCnetwork as curfit
import curvefitting.secondorderstep as secstep

import matplotlib.pyplot as plt
import numpy as np



if __name__ == "__main__":
    #curfit.doTheMath()
    secstep.doSecOrderStep()