from scipy.optimize import curve_fit
import numpy as np
import lmfit

VALID_METHODS = ['least_squares', 'differential_evolution', 'brute',
                 'basinhopping', 'ampgo', 'nelder', 'lbfgsb', 'powell', 'cg',
                 'newton', 'cobyla', 'bfgs', 'tnc', 'trust-ncg', 'trust-exact',
                 'trust-krylov', 'trust-constr', 'dogleg', 'slsqp', 'emcee',
                 'shgo', 'dual_annealing']

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

def fitSineFunction():
    model = lmfit.Model(sine_function)
    params = model.make_params(amp={'value': 2, 'min': 0, 'max': 10},
                           frequency={'value': 2.0, 'min': 0, 'max': 6.0},
                           decay={'value': 2.0, 'min': 0.001, 'max': 12},
                           offset=1.0)

    # fit with leastsq
    result0 = model.fit(ydat, params, x=x, method='leastsq')
    print("# Fit using leastsq:")
    print(result0.fit_report())

