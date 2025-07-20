from scipy.optimize import curve_fit
import numpy as np

def sine_function(x, amp, omega, phase, offset):
    return amp * np.sin(omega * x + phase) + offset

def guessSine(t, y, intialGuess=None):

    if intialGuess == None:
        initial_guess = [1,2, 0, 0]

    # Perform the curve fitting
    params, covariance = curve_fit(sine_function, t, y, p0=intialGuess)

    # Extract the fitted parameters
    A_fit, B_fit, C_fit, D_fit = params

    print(f"Fitted parameters: A={A_fit}, B={B_fit}, C={C_fit}, D={D_fit}")
    # Generate y values using the fitted parameters
    print(f"covariantie = {covariance}")
    return params, covariance
