import logging
import math
import lmfit
import numpy as np

import matplotlib.pyplot as plt
from scipy.fft import fft
from devices.BaseScope.BaseChannel import Channel, WaveForm

logger = logging.getLogger(__name__)
########## BASEFUNCTION ###########
class ScopeFunction(object):
    ADD = {0: "+"}
    SUB = {1: "-"}
    MUL = {2: "*"}
    FFT:dict = {3: "FFT"}
    PHASEFIT = {4: "PHASE"}
    VALIDFUNCTONS:list = [ADD, SUB, MUL, FFT, PHASEFIT]
    def __init__(self, theFunction:dict = None):
        self.functionType = None
        if type(theFunction) != dict or len(theFunction) != 1:
            return
        
        index = [i for i in range(0, len(ScopeFunction.VALIDFUNCTONS)) if (list(theFunction.values()))[0] in ScopeFunction.VALIDFUNCTONS[i].values()]
        if len(index)>0:
            self.functionType = theFunction

    def setOperands(self, oper1 =  None, oper2 = None):
        if oper1 == None and oper2 == None:
            logger.log("Trying to set operands of functions with NoneType!")
            
class ZeroCrossDetect(ScopeFunction):
    def __init__(self, theFunction = None):
        super().__init__(theFunction)   

    def find(self, inputSamp: np.array):
        """"""     
        # to find zero crossings, one need the offset    
        offset = np.mean(inputSamp)
        positive = inputSamp > offset
        idx = np.where(np.bitwise_xor(positive[1:], positive[:-1]))[0]
        return idx


class FFT(ScopeFunction):
    def __init__(self, chan: Channel = None):
        """Inits the BaseFFT.
        param: chan: the (visible) channel of whichthe FFT must be calculated"""
        super().__init__(ScopeFunction.FFT)
        self.scopeChan: Channel = chan
        self._FFT  = None
        self._freqAxis = None

    @property
    def freqAxis(self):
        if self.scopeChan == None or self.scopeChan.WF == None:
            logger.log(logging.ERROR, "Trying to create FFT frequency array of NoneType, return now... ")
            return
        if self.scopeChan.WF.xincr == None:
            self.scopeChan.capture()
       
        myfx = np.arange(self.scopeChan.WF.nrOfSamples)
        self._freqAxis = myfx*(1.0/(self.scopeChan.WF.xincr*self.scopeChan.WF.nrOfSamples))
        return self._freqAxis

    @property
    def FFT(self):
        if self.scopeChan == None or self.scopeChan.WF == None:
            logger.log(logging.INFO, "Trying to take the FFT of NoneType, return now... ")
            return
        if self.scopeChan.WF.xincr == None:
            self.scopeChan.capture()
        self._FFT = fft(self.scopeChan.WF.scaledYdata)
        return self._FFT
    
    def setOperands(self, oper1:Channel =  None, oper2:Channel = None):
        super().setOperands(oper1,oper2)
        if isinstance(oper1, Channel):
            self.scopeChan = oper1

    def setChan(self, newChan: Channel):
        self.scopeChan = newChan

    def get(self):
        myftt= self.FFT
        return (self.freqAxis,self.FFT)
    
    def plot(self, captureFirst: bool = False, linear: bool = True, aliasing:bool = False, autoRange: bool = True):
        """Convenient function for showing a Matplotlib of this fft.
        This function is under construction, it doesn't take the number of samples used for FFT calclulation into
        account. See: https://dsp.stackexchange.com/questions/78188/units-of-a-fast-fourier-transform-fft-and-spectrogram
        Parameters:
            captureFirst: make capture first (True) or not. Default = False.
            linear      : True for lineair axis, False to dB plot. Default = True
            aliasing    : Plotting a complete FFT bin (True), of half of it (False), to prevent aliasing. Default = False
            autoRange   : Automatic scaling of FFT, based on a power threshold."""

        #TODO: implement autoRange
        if self.scopeChan == None or self.scopeChan.WF == None:
            logger.log(logging.ERROR, "Trying to plot FFT without source channel set or data")
            return
        if captureFirst:
            self.scopeChan.capture()
        myfig = plt.figure()
        if not aliasing:
            currFreqAxisSize = int(len(self.freqAxis)/2)
            plotFreqAxis = self.freqAxis[0:currFreqAxisSize-1]
            plotFFTAxis = self.FFT[0:currFreqAxisSize-1]
        else:
            plotFreqAxis = self.freqAxis
            plotFFTAxis = self.FFT
        if autoRange:
            maxFFT = np.max(abs(plotFFTAxis))
            threshold = maxFFT*0.707
            autoRangeFFTBoolIndex = abs(plotFFTAxis)>threshold
            myindex = np.where(autoRangeFFTBoolIndex == True)
            myMaxindex = int(myindex[0])*2
            plotFFTAxis = plotFFTAxis[0:myMaxindex-1]
            plotFreqAxis = plotFreqAxis[0:myMaxindex-1]
        if linear:
            plt.plot(plotFreqAxis, np.abs(plotFFTAxis))
        else:
            plt.plot(np.log10(plotFreqAxis), 20*np.log10(np.abs(plotFFTAxis)))
        plt.title(f"FFT of Channel {self.scopeChan.name}")
        axs = myfig.get_axes()
        axs[0].set_xlabel("frequency [Hz]")
        axs[0].set_ylabel("|X(f)|")
        axs[0].grid(True)
        #plt.show()

        return myfig
    

class SineFitter(object):

    VALID_METHODS = ['least_squares', 'differential_evolution', 'brute',
                    'basinhopping', 'ampgo', 'nelder', 'lbfgsb', 'powell', 'cg',
                    'newton', 'cobyla', 'bfgs', 'tnc', 'trust-ncg', 'trust-exact',
                    'trust-krylov', 'trust-constr', 'dogleg', 'slsqp', 'emcee',
                    'shgo', 'dual_annealing']


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
        self._WF: WaveForm = None
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
        if newMethod in SineFitter.VALID_METHODS:
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
        
        self._model = lmfit.Model(self.sine_function)
        self.makeParam()
        self._result = self._model.fit(data=self.ydat, params=self.params, x=self.xdat, 
                                       method=self.method)
        self._summary = self._result.summary()
        self._bestval = self._summary['best_values']
        self.yfit = self.sine_function(self.xdat, self.bestAmp, self.bestFreq, self.bestPhase, 
                                       self.bestOffset)

    def printFittedParam(self):
        print(f"Value of fitted amp: {self.amp}")
        print(f"Value of fitted freq: {self.freq}")
        print(f"Value of fitted phase: {self.phase}")
        print(f"Value of fitted offset: {self.offset}")

    #TODO: statistische gegevens eruit halen: hoe goed is de fit?
    #TODO: beter om het lmfit ingebouwde lmfit sinus model te pakken?
    #TODO: een plot functie om te zin of de fit gelukt is. En op basis daarvan een functie om melding te krijgen als 
    # fit onder en bepaalde grens komt.



class PhaseEstimator(ScopeFunction):
    
    def __init__(self, inputWF:WaveForm=None, outputWF:WaveForm=None, debugPrint=False):
        super().__init__(ScopeFunction.PHASEFIT)
        #TODO: create input- and outputfitter setters and getters for changing the fitting waveform function.
        self._inputFitter = SineFitter()
        self._outputFitter = SineFitter()
        
        self._inputWF = None
        self._input = None
        self._tAxis = None
        self._inputFitter.WF = None

        self._outWF = None
        self._output = None
        self._outputFitter.WF = None

        if inputWF != None:
            self._inputWF = inputWF
            self._input = inputWF.scaledYdata
            self._tAxis = inputWF.scaledXdata
            self._inputFitter.WF = inputWF

        if outputWF != None:
            self._outWF = outputWF
            self._output = outputWF.scaledYdata
            self._outputFitter.WF = outputWF
        
        
        
        self._debug = debugPrint
        self._phaseDiff = None

    def setOperands(self, oper1:WaveForm=None, oper2:WaveForm=None):
        super().setOperands(oper1, oper2)

        if isinstance(oper1,WaveForm) and isinstance(oper2,WaveForm): 
            self.setWFs(oper1, oper2)
        else:
            logger.log(logging.CRITICAL, "Try to set estimater without setting correct operandtypes!")
            return


    @property
    def inputFitter(self):
        return self._inputFitter

    @property
    def outputFitter(self):
        return self._outputFitter

    @property
    def inputWF(self):
        return self._inputWF
    
    @inputWF.setter
    def inputWF(self, inWF: WaveForm):
        if inWF.any() != None:
           self._inputWF = inWF
           self._input = self.inputWF.scaledYdata
           self.inputFitter.WF = inWF

    @property
    def input(self):
        return self._input
    
    @input.setter
    def input(self, signal):
        if signal.any() != None:
           self._input = signal

    @property
    def outputWF(self):
        return self._outWF
    
    @outputWF.setter
    def outputWF(self, outWF: WaveForm):
        if outWF.any() != None:
           self._outWF = outWF
           self._output = self.outputWF.scaledYdata
           self.outputFitter.WF = outWF
    
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


    

    def setWFs(self, inWF: WaveForm = None, outWF: WaveForm = None):
        if inWF == None or outWF == None:
            logger.log(logging.WARNING, "Trying to set (one of) estimator WF with a None type")
            return
        self.inputWF = inWF
        self.outputWF = outWF

    def setAPriori(self, ampIn=0, ampOut=0, freq=0, phase=0, offset=0):
        #set input param for lmfit with some known values
        self._inputFitter.setAPrioriData(ampIn,freq,phase,offset)
        self._outputFitter.setAPrioriData(ampOut,freq,phase,offset)

    #def estimate(self, wfIn: BaseWaveForm, wfOut: BaseWaveForm):
    def estimate(self):
        """Estimates the phase difference between input and output, assuming fitparams for both signals have been set."""
        
        self._inputFitter.makeFit()
        self._outputFitter.makeFit()
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
        
        myindex = index[0][0]-1
        fig = plt.figure()
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
        ax.legend(["sampled input", "sa mple output","fitted input","fitted output"], loc="lower right")
        input(f'Press [Enter] to proceed to the next plot.')
        plt.clf()


########## BASEMATH ###########
class ScopeMath(object):
    """A class for holding software defined scopefunctions"""
    def __init__(self):
        self.functions:list = [] # list for holding the function
        self.functions.append(FFT())
        self.functions.append(PhaseEstimator())

    def add(self, aFunction: ScopeFunction):
        self.functions.append(aFunction)
    
    def remove(self, aFunction: ScopeFunction):
        """Removes a function from the BaseVertical list. Called by BaseVertical."""
        pass

    #def get(self, aFunction: BaseFunction):
    #    pass

    def get(self, functionStr: str = None, oper1 = None, oper2 = None):
        # self.functions is a list, which element is a dict. So from every item of the list functions, one wants to have the value of the
        # functionType member of the BaseFunction element in the list
        # So the line of code is: (self.function[i]).values(), because every dict element of list has only one value elemet
        if functionStr == None:
            return
        myFunction:ScopeFunction = None
        index = [i for i in range(0, len(self.functions)) if functionStr in self.functions[i].functionType.values()]
        if index != None and len(index)==1:
            myFunction =  self.functions[index[0]]

        if myFunction is None:
            return None
        if oper1 is None:
            return myFunction
        elif oper2 is None:
            myFunction.setOperands(oper1)
        else:
            myFunction.setOperands(oper1, oper2)
        return myFunction
            
            
            
    #def get(self):
    #    return self.functions

    def clear(self):
        "Clears all added functions"
        self.functions.clear()
    
    def visible(self, aFunction: ScopeFunction=None, status: bool=True):
        """Defines whether or not the function will be Visible"""
        pass
