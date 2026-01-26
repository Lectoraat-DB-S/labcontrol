from devices.BaseScope import BaseAcquisition
from devices.siglent.sds.SDS2000.commands_full import SCPI 
import pyvisa

class SDS2kAcquisition(BaseAcquisition):
    """"Subclass of BaseDisplay for Siglent SDS 2000 series. This class implements the base Acquisiton class.
    The subsequent commands are taken from Siglent Programming Programming Guide PEN11D """

    @classmethod
    def getAcquisitionClass(cls):
        """ Tries to get (instantiate) the device"""
        if cls is SDS2kAcquisition:
            return (cls)
        else:
            return None   
        
    def __init__(self, visaInstr:pyvisa.resources.MessageBasedResource):
        super().__init__(visaInstr)
        self.acqMode = "SAMPLING"

    def mode(self):
        """Queries the oscilloscope's current acquisition mode.
        Returns the current acquisition setting, which is one of SAMple, PEAKdetect or AVErage."""
        return self.visaInstr.query("ACQUIRE_ WAY?")

    def mode(self, acqMode):
        """Sets the oscilloscope's mode of acquisition.
        Parameters: acqMode, the new acquisiton mode. For SDS valid options are SAMPLING,PEAK_DETECT,AVERAGE,HIGH_RES
        Valid values of parameter acqMode are:
            1 or "SAMPLING"       : Setting the sample acquisition.
            2 or "peakdetect"   : Setting peakdetect acquisition.
            3 or "average"      : Setting the averaging acquisition mode.
        If averaging has been selected, one should also set the number of averages."""
        if acqMode== "sample" or acqMode == 1:
            mode = "SAMPLING"
        elif acqMode== "peakdetect" or acqMode == 2:
            mode = "PEAK_DETECT"
        elif acqMode== "average"or acqMode == 3:
            mode = "AVERAGE"
        elif acqMode== "high_res" or acqMode== "HIGH_RES" or acqMode == 4:
            mode = "HIGH_RES"
        else:
            return
        self.visaInstr.write(f"ACQUIRE_WAY {mode}")
        self.acqMode = mode
        return
    
    def getNumOfAcquisition(self):
        """Indicates the number of acquisitions that have taken place since starting
        oscilloscope acquisition. The maximum number of acquisitions that can be
        counted is 231-1. See TDS programming manual, page 2-41, for further information."""
        return self.visaInstr.query("ACQUIRE_WAY?")

    def averaging(self):
        """Queries the number of oscilloscope waveform acquisitions setted, that make up an averaged
        waveform."""
        return self.visaInstr.query("ACQUIRE_WAY?")

    def averaging(self, nrOfAvg):
        """Sets the number of oscilloscope waveform acquisitions that make up an averaged
        waveform.
        Parameters: nrOfAvg, the new acquisiton mode.
        Valid values of parameter nrOfAvg are {4,16,32,64,128,256,512,1024}:
            4   : Setting the number of acquisitions to 4.
            16  : Setting the number of acquisitions to 16.
            64  : Setting the number of acquisitions to 64.
            128 : Setting the number of acquisitions to 128.
            etc
        """
        
        if nrOfAvg <= 4:
            numAvg = 4
        elif nrOfAvg <= 16:
            numAvg = 16
        elif nrOfAvg <= 64:
            numAvg = 64
        elif nrOfAvg <= 128:
            numAvg = 128
        elif nrOfAvg <= 64:
            numAvg = 64
        elif nrOfAvg <= 256:
            numAvg = 256
        elif nrOfAvg <= 512:
            numAvg = 512
        elif nrOfAvg <= 1024:
            numAvg = 1024
        else:
            numAvg = 1024
        self.visaInstr.write(f"ACQUIRE_WAY {self.acqMode},{numAvg}")
    
    def state(self):
        return self.visaInstr.query("ACQuire:STATE?")

    def state(self, runMode):
        """Starts or stops oscilloscope acquisitions.
        Parameters: runMode, the new acquisiton mode.
        Valid values of parameter runMode are:
            4   : Setting the number of acquisitions to 4.
            16  : Setting the number of acquisitions to 16.
            64  : Setting the number of acquisitions to 64.
            128 : Setting the number of acquisitions to 128.
            """
        if runMode == "ON" or runMode == "RUN":
            mode = 1
        elif runMode == "OFF" or runMode == "STOP":
            mode = 0
        elif runMode != 0:
            mode = 1
        elif runMode == 0:
            mode = 0
        self.visaInstr.write(f"ACQuire:STATE {mode}")

    def singleSequence(self):
        response = self.visaInstr.query("ACQuire:STOPAfter?")
        if response == "SEQuence":
            return True
        else:
            return False
        
    def singleSequence(self, mode: bool):
        if mode:
            self.visaInstr.write("ACQuire:STOPAfter SEQuence")
        else:
            self.visaInstr.write("ACQuire:STOPAfter RUNSTop")
        

    #********** SDS2k specific functions. These functions needs, sowehow, ****************************
    #********** remapping on the Acquisition baseclass interface. This is ****************************
    #********** To Be Defined ************************************************************************

    """This is the complete set of SDS2k acquire commands:
     :ACQuire:AMODe
     :ACQuire:CSWeep
     :ACQuire:INTerpolation
     :ACQuire:MMANagement
     :ACQuire:MODE
     :ACQuire:MDEPth
     :ACQuire:NUMAcq
     :ACQuire:POINts
     :ACQuire:SEQuence
     :ACQuire:SEQuence:COUNt
     :ACQuire:SRATe
     :ACQuire:TYPE 
    
    Opmerking: misschien maar als properties gaan wegwerken?
    """
    def  setAcqRateMode(self, newRateMode):
        myMode = "FAST"
        if newRateMode == "FAST" or newRateMode == 1:
            myMode = "FAST"
        else:
            myMode = "SLOW" 
            
        self.visaInstr.write(SCPI["ACQUIRE"]["amode"](myMode))

    def clearSweeps(self):
        self.visaInstr.write(SCPI["ACQUIRE"]["csweep"])

    def setAcqInterpolation(self, state: bool):
        
        if state == False:
            myMode = "OFF"
        else:
            myMode = "ON"

        self.visaInstr.write(SCPI["ACQUIRE"]["interpolation"](myMode))

    def setAcqMemMode(self, newMode):
        if newMode == "AUTO" or newMode == 0:
            myMode = "AUTO"
        elif newMode == "AUTOFSRate" or newMode == 1:
            myMode = "FSRate"
        elif newMode == "FMDepth" or newMode == 2:
            myMode = "FMDepth"
        else:
            myMode = "AUTO"
        self.visaInstr.write(SCPI["ACQUIRE"]["mmanagement"](myMode))

    def setAcqMode(self, newMode):
        if newMode == "YT" or newMode == 0:
            myMode = "YT"
        elif newMode == "XY" or newMode == 1:
            myMode = "XY"
        elif newMode == "ROLL" or newMode == 2:
            myMode = "ROLL"
        else:
            myMode = "YT"
        myDepth = 10e3

    def setAcqMemDepth(self, newDepth):
        
        match(newDepth):
            case 10e3:
                myDepth = 10e3
            case 100e3:
                myDepth = 100e3
            case 1e6:
                myDepth = 1e6
            case 10e6:
                myDepth = 10e6
            case 100e6:
                myDepth = 100e6
            case "10k":
                myDepth = 10e3
            case "100k":
                myDepth = 100e3
            case "1e6":
                myDepth = 1e6
            case "10e6":
                myDepth = 10e6
            case "100e6":
                myDepth = 100e6
            case _:
                myDepth = 10e3
        self.visaInstr.write(SCPI["ACQUIRE"]["mdepth"](myDepth))
 
    def getNumOfAcq(self):
        return self.query(SCPI["TIMEBASE"]["numacq?"]())

    def getNumOfAcqPoints(self):
        return self.query(SCPI["TIMEBASE"]["points?"]())

    def setAcqRes(self, newRes):
        if newRes == 8 or newRes == "8" or newRes == "eight":
            myRes = 8
        elif newRes == 10 or newRes == "10" or newRes == "ten":
            myRes = 10
        else:
            myRes = 10
        self.visaInstr.write(SCPI["ACQUIRE"]["resolution"](myRes))

    def setAcqSeqMode(self, state: bool):
        if state:
            mySeqMode = "ON"
        else:
            mySeqMode = "OFF"

        self.visaInstr.write(SCPI["ACQUIRE"]["sequence"](mySeqMode))

    def setAcqSeqCount(self, newCount):
        self.visaInstr.write(SCPI["ACQUIRE"]["sequence_count"](newCount))

    def setAcqRate(self, newRate):
        self.visaInstr.write(SCPI["ACQUIRE"]["srate"](newRate))

    def setAcqType(self, newType, val = 0):
        validAvgNum = [4,16,32,64,128,256,512]# {4|16|32|64|128|256|512|
        validNrOfBits = [0.5,1.0,1.5,2.0,2.5]#<bits>:=0.5|1.0|1.5|2.0|2.5|
        functionType = 1
        myType = "NORMal"
        if newType == "NORMAL" or newType == "normal" or newType == 0:
            functionType = 1
            self.visaInstr.write(SCPI["ACQUIRE"]["type_1"](val)) 
        elif newType == "PEAK" or newType == "peak" or newType == 1:
            myType = "PEAK"
            functionType = 1
        elif newType == "AVERAGE" or newType == "average" or newType == 2:
            myType = "AVERage"
            functionType = 2
            if val in validAvgNum:
                myVal = val
            else:
                myVal = 4
        elif newType == "ERES" or newType == "eres" or newType == 3:
            myType = "ERES"
            if val in validNrOfBits:
                myVal = 0.5
            functionType = 2
        else:
            functionType = 1
            myType = "NORMal"
        if functionType == 1:
            self.visaInstr.write(SCPI["ACQUIRE"]["type_1"](myType))
        else:
            self.visaInstr.write(SCPI["ACQUIRE"]["type_2"](myType)(myVal))




