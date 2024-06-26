import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from lmfit import Parameters,minimize, fit_report

# Creating a random dummy data for our power fittin
# A = 2.5
# lambda = 0.5
# omega = 7.2
# phi = 3.14
t = np.linspace(0,6,100)
y = 2.5*np.exp(-0.5*t)*np.cos(7.2*t+3.14) + np.random.normal(0, 0.25, 100)

# Define the fitting function
def decaying_sine(params,t,y):
    A = params['A']
    lambdas = params['lambdas'] #lambda has a different meaning in python 
    omega = params['omega']
    phi = params['phi']
    y_fit = A * np.exp(-lambdas*t)*np.cos(omega*t+phi)
    return y_fit-y

# Defining the various parameters
params = Parameters()
params.add('A', min= 1.0, max= 5.0)
params.add('lambdas', min= -1.0, max= 1.0)
params.add('omega', min= 0.0, max= 10.0)
params.add('phi', min= 0.0, max= 10.0)

# Calling the minimize function. Args contains the x and y data.
fitted_params = minimize(decaying_sine, params, args=(t,y,), method='nelder')

# Getting the fitted values
A = fitted_params.params['A'].value
lambdas = fitted_params.params['lambdas'].value    
omega = fitted_params.params['omega'].value    
phi = fitted_params.params['phi'].value    

# Pretty printing all the statistical data
print(fit_report(fitted_params))

plt.scatter(t,y,c='black')
plt.xlabel('Time (sec)')
plt.ylabel('Stress (kPa)')
plt.plot(t, A * np.exp(-lambdas*t)*np.cos(omega*t+phi),c='red',ls='-',lw=5)
plt.show();