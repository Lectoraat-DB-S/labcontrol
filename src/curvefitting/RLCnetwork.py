import math
import numpy as np
import matplotlib.pyplot as plt
from lmfit import Parameters,minimize, fit_report
#see https://coertvonk.com/physics/rlc-filters/rlc-resonator/rlc-resonator-14404
#see https://lpsa.swarthmore.edu/Transient/TransInputs/TransStep.html#second

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


def transfer(R,L,C,s):
    w0=1/math.sqrt(L*C)
    damping = R/2*math.sqrt(C/L)
    K=R/L
    H=K*(pow(w0,2)/(pow(s,2)+2*damping*w0*s+pow(w0,2)))
    return H
    

def calcDiscriminant(damping):
    return (pow(damping,2)-1)   

def underdamped_system_ungated(K,w0,damping,t:np.array, offset =0.4):
    wd=w0*math.sqrt(1-pow(damping,2))
    alpha=w0*damping
    phi=math.acos(damping)
    
    t=t-offset
    y_out = K*(1-((np.sqrt(pow(alpha,2)+pow(wd,2))/wd)*np.exp(-alpha*t)*np.sin(wd*t+phi)))
    return y_out

def  underdamped_system (K,w0,damping,t:np.array, offset):
    y = underdamped_system_ungated(K,w0,damping,t, offset)
    y[t < 0.0] = 0.0
    return y

# Define the fitting function
def secOrderModelFunction(params,t,y):
    K = params['K']
    w0 = params['w0']
    damping = params['damping']
    t0 = params['t0'] 
    wd=w0*np.sqrt(1-pow(damping,2))
    alpha=w0*damping
    phi=math.acos(damping)
    y_fit =  K*(1-((np.sqrt(pow(alpha,2)+pow(wd,2))/wd)*np.exp(-alpha*(t-t0))*np.sin(wd*(t-t0)+phi)))
    return y_fit-y

def doTheMath():
    R=1
    C=1
    L=1

    w_n=1/math.sqrt(L*C)
    damping = R/2*math.sqrt(C/L)
    K=R/L
    f_n=w_n/(2*math.pi)
    offset = 0.5
    fs=10.0 #sample rate in Hz
    ns=200 #number of samples
    t = np.linspace(0,ns/fs,ns)
    print(calcDiscriminant(damping))
    print(w_n)
    print(f_n)
    y=underdamped_system(K,w_n,damping,t, offset)
    #add some deadtime at start.
    z = np.zeros(shape=(20,), dtype=float)
    y_dt=np.concatenate((z,y))

    lengte = len(y_dt)
    t_dt = np.linspace(0,lengte/fs,lengte)
    plt.figure(1)
    plt.plot(t_dt,y_dt)
    #insert some noise
    y_noise = addAWGN(45,y_dt)
    plt.figure(2)
    plt.plot(t_dt,y_noise)
    plt.show()

    plt.figure(3)
    plt.plot(t, y)

    params = Parameters()
    params.add('K', min= 0.1, max= 5.0)
    params.add('w0', min= 0.01, max= 10.0)
    params.add('damping', min= 0.0, max= 10.0)
    params.add('t0', min= 1.0, max= 10.0)
    fitted_params = minimize(secOrderModelFunction, params, args=(t_dt,y_noise,), method='least_squares')
    # Getting the fitted values
    K_fit = fitted_params.params['K'].value
    w0_fit = fitted_params.params['w0'].value    
    damping_fit = fitted_params.params['damping'].value   
    offset_tijd = fitted_params.params['t0'].value
    print("inserted parameters:\n")
    print("K = "+str(K)) 
    print("w_n = "+str(w_n)) 
    print("damping = "+str(damping))
    print("fitted parameters:\n")
    print("K_fit = "+str(K_fit)) 
    print("w0_fit = "+str(w0_fit)) 
    print("damping_fit = "+str(damping))
    print("offset_tijd = "+str(offset_tijd))
    
    plt.show()