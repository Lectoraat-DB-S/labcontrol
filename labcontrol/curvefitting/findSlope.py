#https://stackoverflow.com/questions/13691775/python-pinpointing-the-linear-part-of-a-slope
from matplotlib import pyplot as plt

import numpy as np

def SlopeFind():
    # create theoretical data
    x_a = np.linspace(-8,0, 60)
    y_a = np.sin(x_a)
    x_b = np.linspace(0,4,30)[1:]
    y_b = x_b[:]
    x_c = np.linspace(4,6,15)[1:]
    y_c = np.sin((x_c - 4)/4*np.pi)/np.pi*4. + 4
    x_d = np.linspace(6,14,120)[1:]
    y_d = np.zeros(len(x_d)) + 4 + (4/np.pi)

    x = np.concatenate((x_a, x_b, x_c, x_d))
    y = np.concatenate((y_a, y_b, y_c, y_d))


    # make noisy data from theoretical data
    y_n = y + np.random.normal(0, 0.27, len(x))

    # create convolution kernel for calculating
    # the smoothed second order derivative
    smooth_width = 59
    x1 = np.linspace(-3,3,smooth_width)
    norm = np.sum(np.exp(-x1**2)) * (x1[1]-x1[0]) # ad hoc normalization
    y1 = (4*x1**2 - 2) * np.exp(-x1**2) / smooth_width *8#norm*(x1[1]-x1[0])



    # calculate second order deriv.
    y_conv = np.convolve(y_n, y1, mode="same")

    # plot data
    plt.plot(x,y_conv, label = "second deriv")
    plt.plot(x, y_n,"o", label = "noisy data")
    plt.plot(x, y, label="theory")
    plt.plot(x, x, "0.3", label = "linear data")
    plt.hlines([0],-10, 20)
    plt.axvspan(0,4, color="y", alpha=0.2)
    plt.axvspan(6,14, color="y", alpha=0.2)
    plt.axhspan(-1,1, color="b", alpha=0.2)
    plt.vlines([0, 4, 6],-10, 10)
    plt.xlim(-2.5,12)
    plt.ylim(-2.5,6)
    plt.legend(loc=0)
    plt.show()