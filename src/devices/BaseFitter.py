import numpy as np
import lmfit
from lmfit.model import ModelResult
import math
import matplotlib.pyplot as plt
from devices.BaseScope import BaseWaveForm
from astropy.timeseries import LombScargle  # zit vaak in astropy

import numpy as np




VALID_METHODS = ['least_squares', 'differential_evolution', 'brute',
                 'basinhopping', 'ampgo', 'nelder', 'lbfgsb', 'powell', 'cg',
                 'newton', 'cobyla', 'bfgs', 'tnc', 'trust-ncg', 'trust-exact',
                 'trust-krylov', 'trust-constr', 'dogleg', 'slsqp', 'emcee',
                 'shgo', 'dual_annealing']


class FitSine():
    """A class for fitting a model of a sine,"""
    def __init__(self, amp=1, freq=1000, phase=0, offset=0):
        self._amp = amp
        self._freq = freq
        self._phase = phase
        self._offset = offset
        self._model = None
        self._params = None
        self._result = None
        self._method = "basinhopping"
        self._summary = None
        self._bestval = None
        self._WF: BaseWaveForm = None
        self._xdat = None
        self._ydat = None
        self._yfit = None
        #best estimation section
        self._bestAmp = 0
        self._bestFreq = 0
        self._bestPhase = 0
        self._bestOffset = 0

    # Best properties
    @property
    def bestAmp(self):
        if self._bestval == None:
            return None
        return self._bestval["amp"]
    
    @property
    def bestFreq(self):
        if self._bestval == None:
            return None
        return self._bestval["freq"]
    
    @property
    def bestPhase(self):
        if self._bestval == None:
            return None
        return self._bestval["phase"]
    
    @property
    def bestOffset(self):
        if self._bestval == None:
            return None
        return self._bestval["offset"]
    
    

    def sine_function(self, x, amp, freq, phase, offset):
        return amp * np.sin((2*np.pi*freq * x) + phase) + offset

    @property
    def WF(self):
        return self._WF
    
    @WF.setter
    def WF(self, newWF):
        self._WF = newWF

    @property
    def amp(self):
        return self._amp

    @amp.setter
    def amp(self, newVal):
        """Property for setting the amp parameter of the SineModel. This method also call the makeParam function of this class,
        in order to set the proper lmfit params for doing the fit."""
        self._amp = newVal
        #self.makeParam()
    
    @property
    def phase(self):
        return self._phase

    @phase.setter
    def phase(self, newVal):
        self._phase = newVal
        #self.makeParam()


    @property
    def offset(self):
        return self._offset 

    @offset.setter
    def offset(self, newVal):
        self._offset = newVal
        #self.makeParam()   

    @property
    def freq(self):
        return self._freq

    @freq.setter
    def freq(self, newVal):
        self._freq = newVal
        #self.makeParam()

    @property
    def phaseDeg(self):
        return (self.phase*180.0)/math.pi
    
    @property
    def params(self):
       return self._params
       
    @params.setter
    def params(self, fitParams):
        self._params = fitParams

    @property 
    def method(self):
        return self._method
    
    @method.setter
    def method(self, newMethod):
        if newMethod in VALID_METHODS:
            self._method = newMethod

    @property     
    def xdat(self):
        self._xdat = self._WF.scaledXdata
        return self._xdat

    @property     
    def ydat(self):
        self._ydat = self._WF.scaledYdata
        return self._ydat    

    @property     
    def yfit(self):
        return self._yfit
    

    @yfit.setter     
    def yfit(self, newFitData):
        self._yfit = newFitData
            

    def setData(self, xdata, ydata):
        self._xdat = xdata
        self._ydat = ydata

    def setAPrioriData(self, amp=0, freq=0, phase=0, offset = 0):
        self.amp = amp
        self.freq = freq
        self.phase = phase
        self.offset = offset
    

    def makeParam(self):
        #TODO: check whether 0.95*self will work. Goal: better control over variantion of parameters.
        self.params = self._model.make_params(amp={'value': self.amp, 'min': 0.95*self.amp, 'max': 1.05*self.amp, 'vary': True},
                            freq={'value': self._freq, 'min': 0.01*self._freq, 'max': 1.1*self._freq, 'vary': True},
                            phase={'value': self._phase, 'min': -np.pi, 'max': np.pi, 'vary': True},
                            offset={'value': self._offset, 'min': -0.1, 'max': +0.1, 'vary': True})
        #self.params.create_uvars()
    


    def makeFit(self):
        #self._model = lmfit.Model(self.sine_function, independent_vars=['x'], param_names=['amp', 'freq', 'phase', 'offset'])
        self._model = lmfit.Model(self.sine_function)
        #guess = self.guess_sine_params(self.xdat, self.ydat)
        #guess = self.guess_sine_params_irregular(self.xdat, self.ydat)
        self.makeParam()
        #self.params  = self._model.make_params(**guess)
        #self.params['freq'].set(vary=False)
        #self.params['amp'].set(vary=False)
        #self.params.create_uvars()
        self._result = self._model.fit(data=self.ydat, params=self.params, x=self.xdat, 
                                       method=self.method)
        #print(self._result.fit_report())
        #for name, par in self._result.params.items():
        #    print(name, par.value, par.stderr)
        self._summary = self._result.summary()
        self._bestval = self._summary['best_values']
        self.yfit = self.sine_function(self.xdat, self.bestAmp, self.bestFreq, self.bestPhase, 
                                       self.bestOffset)

    def printFittedParam(self):
        print(f"Value of fitted amp: {self.amp}")
        print(f"Value of fitted freq: {self.freq}")
        print(f"Value of fitted phase: {self.phase}")
        print(f"Value of fitted offset: {self.offset}")

    #TODO: statistische gegevens eruit halen: hoe goed is de fit
    #TODO: beter om het lmfit ingebouwde lmfit sinus model te pakken?
    #TODO: een plot functie om te zin of de fit gelukt is. En op basis daarvan een functie om melding te krijgen als 
    # fit onder en bepaalde grens komt.

class PhaseEstimator(object):

    def __init__(self, inputWF:BaseWaveForm=None, outputWF:BaseWaveForm=None, debugPrint=False):
        self._inputWF = inputWF
        self._outWF = outputWF
        self._input = inputWF.scaledYdata
        self._output = outputWF.scaledYdata
        self._tAxis = inputWF.scaledXdata
        self._inputFitter = FitSine()
        self._outputFitter = FitSine()
        self._inputFitter.WF = inputWF
        self._outputFitter.WF = outputWF
        #self._inputFitter.makeParam()
        #self._outputFitter.makeParam()
        self._debug = debugPrint
        self._phaseDiff = None


    @property
    def inputFitter(self):
        return self._inputFitter

    @property
    def outputFitter(self):
        return self._outputFitter
        
    @property
    def input(self):
        return self._input
    
    @input.setter
    def input(self, signal):
        if signal.any() != None:
           self._input = signal

    @property
    def output(self):
        return self._output
    
    @output.setter
    def output(self, signal):
        if signal.any() != None:
           self._output = signal 
           
    @property
    def tAxis(self):
        return self._tAxis
    
    @tAxis.setter
    def tAxis(self, timeData):
        if timeData != None:
           self._tAxis = timeData 


    @property
    def phaseDiffRAD(self):
        """Returns the phase difference between output en input in rad."""
        #return (self._phaseDiff*180.0)/math.pi
        self._phaseDiff = self._outputFitter.bestPhase - self._inputFitter.bestPhase

        return self._phaseDiff
    
    @property
    def phaseDiffDEG(self):
        self._phaseDiff = self._outputFitter.bestPhase - self._inputFitter.bestPhase

        return (self._phaseDiff*180.0)/math.pi

    
    def setAPriori(self, ampIn=0, ampOut=0, freq=0, phase=0, offset=0):
        #set input param for lmfit with some known values
        self._inputFitter.setAPrioriData(ampIn,freq,phase,offset)
        self._outputFitter.setAPrioriData(ampOut,freq,phase,offset)

    #def estimate(self, wfIn: BaseWaveForm, wfOut: BaseWaveForm):
    def estimate(self):
        """Estimates the phase difference between input and output, assuming fitparams for both signals have been set."""
        #self._inputFitter.makeParam()
        #self._outputFitter.makeParam()
        #self.inputFitter.setData(xdata=wfIn.scaledXdata, ydata=wfIn.scaledYdata)

        #self.outputFitter.setData(xdata=wfOut.scaledXdata, ydata=wfOut.scaledYdata)
        self._inputFitter.makeFit()
        self._outputFitter.makeFit()
        #self.phaseDiff = self._outputFitter.bestPhase - self._inputFitter.bestPhase
        #TODO: check chi squared value or other indication of fit.
        if self._debug:
            # y = A sin (2 pi f t + phi),  waar is een zerocrossing?
            # als sin (x)=0 dus als x =0 mod pi. dus als 2 pi f t = -phi
            # dus als t = -phi/(2 pi f)
            #self.bestAmp, self.bestFreq, self.bestPhase, 
            self.plot()                        
            self.printResults()
            
        return  self._outputFitter.bestPhase - self._inputFitter.bestPhase
    
    def printResults(self):
        print(f"Resultaten fitting")
        print(f"Input: amplitude = {self.inputFitter.bestAmp}\n frequentie = {self.inputFitter.bestFreq}.\n fase = {self.inputFitter.bestPhase}\n" + 
              f"offset = {self.inputFitter.bestOffset}")
        print(f"Output: amplitude = {self.outputFitter.bestAmp}\n frequentie = {self.outputFitter.bestFreq}.\n fase = {self.outputFitter.bestPhase}\n" + 
              f"offset = {self.outputFitter.bestOffset}")
    
    def plotResults(self, title=None):
        if title == None:
            mytitle = "Phase Estimation Result"
        else:
            mytitle = title
        fig, axs = plt.subplots(2)
        fig.suptitle(mytitle)
        axs[0].plot(self._inputFitter.xdat, self._inputFitter.ydat, self._inputFitter.xdat, self._outputFitter.ydat)
        axs[1].plot(self._inputFitter.xdat, self._inputFitter.ydat, self._inputFitter.xdat, self._outputFitter.ydat,
                    self._inputFitter.xdat, self._inputFitter.yfit, self._inputFitter.xdat, self._outputFitter.yfit)
        axs[0].set_title("input data")
        axs[1].set_title("fitted sinefunctions on data")
        #TODO: create new subplot with only fitted function and a grahpical indication of the phaseDiff found.
        return fig, axs

    def plot(self):
        plt.ion()
        #tzc_in = -1* self.inputFitter.bestPhase/(2*math.pi*self.inputFitter.bestFreq)
        #tzc_out = -1* self.outputFitter.bestPhase/(2*math.pi*self.outputFitter.bestFreq)
        x = -1* math.asin (self.inputFitter.bestOffset/self.inputFitter.bestAmp) 
        print(f"x waarde = {x}")
        tzc_in = (x- self.inputFitter.bestPhase)/(2*math.pi*self.inputFitter.bestFreq)
        x = -1* math.asin (self.outputFitter.bestOffset/self.outputFitter.bestAmp) 
        tzc_out = (x- self.outputFitter.bestPhase)/(2*math.pi*self.outputFitter.bestFreq)
        print(f"x waarde = {x}")
        print(f"zero crossing in:{tzc_in}")
        print(f"zero crossing out:{tzc_out}")
        #nfit = self.inputFitter.yfit
        infit = self.inputFitter.yfit
        index = np.where(infit >= 0)
        ## outfit = self.outputFitter.yfit
       # tzc_in = outfit[outfit==0]
        myindex = index[0][0]-1
        #tzc_in = self.inputFitter.xdat[myindex]
        #TODO: onderstaande nog niet correct.
        #plt.figure(1)
        fig = plt.figure(1)
        ax = plt.gca()
        # first plot original input data
        ax.plot(self._inputFitter.xdat, self._inputFitter.ydat, self._inputFitter.xdat, self._outputFitter.ydat,
                    self._inputFitter.xdat, self._inputFitter.yfit, self._inputFitter.xdat, self._outputFitter.yfit)
        
        #markers voor zero crossing
        ax.plot([ tzc_in], 0,'o') #marker for zero cross of input signal
        ax.plot([ tzc_out], [0],'o')
        #ax.plot([0, tzc_out],'o') #marker for zero cross of output signal
        line1y =[0, self.inputFitter.bestAmp*1.2]   
        line1x =[tzc_in, tzc_in]
        line2y =[0, self.inputFitter.bestAmp*1.2]
        line2x =[tzc_out, tzc_out]
        if tzc_out > tzc_in:
            line3x =[tzc_in*0.8, tzc_out*1.2]
        else:
            line3x =[tzc_out*0.8, tzc_in*1.2]
        line3y = [self.inputFitter.bestAmp*1.1, self.inputFitter.bestAmp*1.1]
        ax.plot(line1x,line1y,linestyle=':', color='k') # vertical line from first  zc  
        ax.plot(line2x,line2y,linestyle=':', color='k') # vertical line from second  zc
        ax.plot(line3x,line3y,linestyle=':', color='k') # horizontal line, connecting line1 and line 2
        ax.text(line3x[1], line3y[1] , f'Phase_diff {self.phaseDiffDEG} degrees (estimate)', style='italic',
        bbox={'facecolor': 'red', 'alpha': 0.5, 'pad': 10})
        
        plt.title(f"Sampled & parameterized in- & output waveforms", fontsize=14, fontweight='bold')
        ax.set_xlim(min(self.inputFitter.xdat), max(self.inputFitter.xdat))
        #ax.set_ylim(-1, 1)
        fig.suptitle('With estimated phase', fontsize=11)
        #ax.title.set_text(f"Sampled & parameterized waveforms")
        ax.legend(["sampled input", "sample output","fitted input","fitted output"], loc="lower right")
        input(f'Press [Enter] to proceed to the next plot.')
        plt.clf()

##OUDE ZOOOI, van Chat, had ik niks aan.....
"""
    from astropy.timeseries import LombScargle  # zit vaak in astropy

    def guess_sine_params_irregular(self, x, y):
        offset = np.mean(y)
        amp = (np.max(y) - np.min(y)) / 2
        
        # Gebruik Lomb–Scargle voor frequentie
        y_detrended = y - offset
        freq_grid = np.linspace(0.1, 10, 5000)  # scan 0.1–10 Hz
        power = LombScargle(x, y_detrended).power(freq_grid)
        freq = freq_grid[np.argmax(power)]
        
        # Schat fase met regressie
        sin_basis = np.sin(2*np.pi*freq*x)
        cos_basis = np.cos(2*np.pi*freq*x)
        A = np.vstack([sin_basis, cos_basis]).T
        coeffs, _, _, _ = np.linalg.lstsq(A, y_detrended, rcond=None)
        phase = np.arctan2(coeffs[1], coeffs[0])
        
        return dict(amp=amp, freq=freq, phase=phase, offset=offset)
    """
    
"""
    def guess_sine_params(self, x, y):
        
        Schat amplitude, offset, frequentie en fase voor een sinus-fit.
       
        # Offset = gemiddelde
        offset = np.mean(y)

        # Amplitude = halve bereik
        amp = (np.max(y) - np.min(y)) / 2

        # Frequentie schatten met FFT
        y_detrended = y - offset
        fft = np.fft.rfft(y_detrended)
        freqs = np.fft.rfftfreq(len(x), d=(x[1]-x[0]))
        freq = freqs[np.argmax(np.abs(fft[1:])) + 1]  # skip DC

        # Fase schatten via correlatie met een sin/cos basis
        sin_basis = np.sin(2*np.pi*freq*x)
        cos_basis = np.cos(2*np.pi*freq*x)
        A = np.vstack   ([sin_basis, cos_basis]).T
        coeffs, _, _, _ = np.linalg.lstsq(A, y_detrended, rcond=None)
        phase = np.arctan2(coeffs[1], coeffs[0])

        return dict(amp=amp, freq=freq, phase=phase, offset=offset)
     
     oude debug print
     #                           
            tzc_in = -1* self.inputFitter.bestPhase/(2*math.pi*self.inputFitter.bestFreq)
            tzc_out = -1* self.outputFitter.bestPhase/(2*math.pi*self.outputFitter.bestFreq)
            #See for non-blocking plotting: https://www.geeksforgeeks.org/python/plotting-in-a-non-blocking-way-with-matplotlib/
            plt.ion()

            #TODO: onderstaande nog niet correct.
            #plt.figure(1)
            fig, axs = plt.subplots(2)
            # first plot original input data
            axs[0].plot(self._inputFitter.xdat, self._inputFitter.ydat, self._inputFitter.xdat, self._outputFitter.ydat)
            axs[0].title.set_text(f"Sampled waveforms")
            axs[0].legend(["x samples", "y samples"], loc="lower right")
            # then plot fitted sinefunction 
            inphase = self.inputFitter.bestPhase
            outphase = self.outputFitter.bestPhase
            print(f"fase input = {inphase/math.pi}, fase output = {outphase/math.pi}")
            axs[1].plot(self._inputFitter.xdat, self._inputFitter.yfit, self._inputFitter.xdat, self._outputFitter.yfit)
            axs[1].plot([tzc_in, 0],'o') #marker for zero cross of input signal
            axs[1].plot([tzc_out, 0],'o') #marker for zero cross of output signal
            line1y =[0, self.inputFitter.bestAmp*1.2]
            line1x =[tzc_in, tzc_in]
            line2y =[0, self.inputFitter.bestAmp*1.2]
            line2x =[tzc_out, tzc_out]
            if tzc_out > tzc_in:
                line3x =[tzc_in*0.8, tzc_out*1.2]
            else:
                line3x =[tzc_out*0.8, tzc_in*1.2]
            line3y = [self.inputFitter.bestAmp*1.1, self.inputFitter.bestAmp*1.1]
            axs[1].plot(line1x,line1y,linestyle=':', color='b') 
            axs[1].plot(line2x,line2y,linestyle=':', color='r') 
            axs[1].plot(line3x,line3y,linestyle=':', color='k') 
            axs[1].title.set_text(f"parameterized waveforms")
            axs[1].legend(["x samples", "fitted sinewave"], loc="lower right")

     
     
     """