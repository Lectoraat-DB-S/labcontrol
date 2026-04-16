import numpy as np
import matplotlib.pyplot as plt
import math

def truncIt(a:np.array):
    a[a<0]=0
    return a

def underdamped_system(K,w0,damping,t:np.array, offset):
    wd=w0*np.sqrt(1-pow(damping,2))
    alpha=w0*damping
    phi=np.arccos(damping)
    t=t-offset
    y_out = K*(1-((np.sqrt(pow(alpha,2)+pow(wd,2))/wd)*np.exp(-alpha*(t))*np.sin(wd*(t)+phi)))
    y_out[t<0]=0
    return y_out

def mainPruts():
    start = 0
    stop=40
    aantal=100
    t=np.linspace(start,stop, num=aantal)
    z=truncIt(t)
    y=underdamped_system(1,1,0.5,t,20)
    #t=t-10
    plt.plot(t)
    plt.figure(2)
    plt.plot(y)
    plt.show()