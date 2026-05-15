
import pyvisa
import logging
#import measurements.weerstandsmetingDMM as measurement
#import measurements.transistorcurve as curfje

import curvefitting.RLCnetwork as curfit
import curvefitting.secondorderstep as secstep

import matplotlib.pyplot as plt
import numpy as np

def addAWGN(target_snr_db = 20, x_in=0):
    x_watts =  x_in ** 2
    # Calculate signal power and convert to dB 
    sig_avg_watts = np.mean(x_watts)
    sig_avg_db = 10 * np.log10(sig_avg_watts)
    # Calculate noise according to [2] then convert to watts
    noise_avg_db = sig_avg_db - target_snr_db
    noise_avg_watts = 10 ** (noise_avg_db / 10)
    # Generate an sample of white noise
    mean_noise = 0
    noise_volts = np.random.normal(mean_noise, np.sqrt(noise_avg_watts), len(x_watts))
    # Noise up the original signal
    y_volts = x_in + noise_volts
    return y_volts


if __name__ == "__main__":
    x = "hello"

#if condition returns True, then nothing happens:
    assert x == "hello"

#if condition returns False, AssertionError is raised:
    assert x == "goodbye"
    #curfit.doTheMath()
    N = 7e3
    n= np.arange(0,N-1)
    fs = 1e6
    Ts = 1/fs
    A = 1
    f = 2e3
    y = np.sin(2*np.pi*n*f/fs)
    ywn= addAWGN(x_in=y)
    plt.figure(1)
    plt.plot(n,ywn)
    plt.show()
    #secstep.doSecOrderStep()