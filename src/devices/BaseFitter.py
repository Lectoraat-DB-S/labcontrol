import numpy as np
import lmfit
from lmfit.model import ModelResult
import math
import matplotlib.pyplot as plt


VALID_METHODS = ['least_squares', 'differential_evolution', 'brute',
                 'basinhopping', 'ampgo', 'nelder', 'lbfgsb', 'powell', 'cg',
                 'newton', 'cobyla', 'bfgs', 'tnc', 'trust-ncg', 'trust-exact',
                 'trust-krylov', 'trust-constr', 'dogleg', 'slsqp', 'emcee',
                 'shgo', 'dual_annealing']


class FitSine():
    """A class for fitting a model of a sine,"""
    def __init__(self, amp, freq, phase, offset):
        self._amp = amp
        self._freq = freq
        self._phase = phase
        self._offset = offset
        self._model = lmfit.Model(self.sine_function)
        self._params = None
        self._result = None
        self._method = "basinhopping"
        self._summary = None
        self._bestval = None
        self._xdat = None
        self._ydat = None
        self._yfit = None

    def sine_function(self, x, amp, freq, phase, offset):
        return amp * np.sin(2*math.pi*freq * x + phase) + offset

    @property
    def amp(self, newVal):
        self._amp = newVal

    @property
    def amp(self):
        if self._bestval != None:
            return self._bestval['amp']
        else:
            return None

    @property
    def freq(self, newVal):
        self._freq = newVal

    @property
    def freq(self):
        if self._bestval != None:
            return self._bestval['freq']
        else:
            return None

    @property
    def phase(self):
        if self._bestval != None:
            return self._bestval['phase']
        else:
            return None

    @property
    def offset(self):
        if self._bestval != None:
            return self._bestval['offset']
        else:
            return None


    @property
    def params(self):
        if self._params != None:
            return self._params
        else:
            return None
    
    @property
    def params(self, fitParams):
        if fitParams != None:
            self._params = fitParams

    @property
    def method(self, newVal):
        if newVal in VALID_METHODS:
            self._method = newVal

    def makeParam(self):
        self._params = self._model.make_params(amp={'value': self._amp, 'min': 0, 'max': 4*self._amp},
                            freq={'value': self._freq, 'min': 0.1*self._freq, 'max': 10.0*self._freq},
                            phase={'value': self._phase, 'min': 0.001, 'max': 89.99},
                            offset={'value': self._offset, 'min': -10, 'max': 10})
    @property     
    def xdat(self, xdata):
        if xdata != None:
            self._xdat = xdata
        
    @property     
    def ydat(self, ydata):
        if ydata != None:
            self._ydat = ydata
        

    @property     
    def yfit(self):
        if self._yfit != None:
            return self._yfit
        else:
            None


    def setData(self, xdata, ydata):
        self._xdat = xdata
        self._ydat = ydata


    def makeFit(self):
        self._result = self._model.fit(self._ydat, self._params, x=self._xdat, method=self._method)
        self._summary = self._result.summary()
        self._bestval = self._summary['best_values']
        self._yfit = self.sine_function(self._xdat, self.amp, self.freq, self.phase, self.offset)


    #TODO: statistische gegevens eruit halen: hoe goed is de fit
    #TODO: beter om het lmfit ingebouwde lmfit sinus model te pakken?
    #TODO: een plot functie om te zin of de fit gelukt is. En op basis daarvan een functie om melding te krijgen als 
    # fit onder en bepaalde grens komt.

class PhaseEstimator(object):

    def __init__(self, inputSignal=None, outputSignal=None, timeData=None, debugPrint=False):
        self._input = inputSignal
        self._output = outputSignal
        self._tAxis = timeData
        self._phaseDiff = None
        self.inputFitter = FitSine()
        self.outputFitter = FitSine()
        self.inputFitter.setData(timeData, inputSignal)
        self.outputFitter.setData(timeData, outputSignal)
        self._debug = debugPrint
        
    @property
    def input(self):
        return self._input
    
    @property
    def input(self, signal):
        if signal != None:
           self._input = signal

    @property
    def output(self):
        return self._output
    
    @property
    def output(self, signal):
        if signal != None:
           self._output = signal 
           
    @property
    def tAxis(self):
        return self._tAxis
    
    @property
    def tAxis(self, timeData):
        if timeData != None:
           self._tAxis = timeData 


    @property
    def phaseDiff(self):
        if self._phaseDiff != None:
            return (self._phaseDiff*180.0)/math.pi
        else:
            return None

    @property
    def phaseDiff(self, value):
        self._phaseDiff = value
    
    def estimate(self):
        """Estimates the phase difference between input and output, assuming fitparams for both signals have been set."""
        if self.inputFitter.params == None or self.outputFitter.params == None:
            #TODO: decide if use makeparam of return none.
            return None
        else:
            self.inputFitter.makeFit()
            self.outputFitter.makeFit()
            self.phaseDiff = self.outputFitter.phase - self.inputFitter.phase
            #TODO: check chi squared value or other indication of fit.
            return self._phaseDiff
        
    

    def estimate(self, inputParam = None, outputParam = None):
        """Estimates the phase difference between input and output, assuming fitparams for both signals have NOT been set."""
        myInputParam = inputParam
        myOutputParam = outputParam
        if inputParam == None:
            self.inputFitter.makeParam()
            myInputParam = self.inputFitter.params
        if outputParam == None:
            self.outputFitter.makeParam()
            myOutputParam = self.outputFitter.params
        self.inputFitter.makeFit()
        self.outputFitter.makeFit()
        self.phaseDiff = self.outputFitter.phase - self.inputFitter.phase
        #TODO: check chi squared value or other indication of fit.
        if self._debug:
            plt.figure(1)
            # first plot original input data
            plt.plot(self.inputFitter.xdat, self.inputFitter.ydat)
            # then plot fitted sinefunction 
            plt.plot(self.inputFitter.xdat, self.inputFitter.yfit)
            plt.show()
        return self._phaseDiff
