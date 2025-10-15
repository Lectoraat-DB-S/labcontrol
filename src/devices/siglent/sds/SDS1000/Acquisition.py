from devices.BaseScope import BaseAcquisition
import pyvisa

class SDSAcquisition(BaseAcquisition):
    """"Subclass of BaseDisplay for Siglent SDS 1000 and 2000 series. This class implements the baseclass."""

    @classmethod
    def getAcquisitionClass(cls):
        """ Tries to get (instantiate) the device"""
        if cls is SDSAcquisition:
            return (cls)
        else:
            return None   
        
    def __init__(self, visaInstr:pyvisa.resources.MessageBasedResource):
        super().__init__(visaInstr)
        self.acqMode = "SAMPLING"

    def mode(self):
        """Queries the oscilloscope's current acquisition mode.
        Returns the current acquisition setting, which is one of SAMple, PEAKdetect or AVErage."""
        return self.visaInstr.query("ACQUIRE_WAY?")

    def mode(self, acqMode):
        """Sets the oscilloscope's mode of acquisition.
        Parameters: acqMode, the new acquisiton mode. For SDS valid options are SAMPLING,PEAK_DETECT,AVERAGE,HIGH_RES
        Valid values of parameter acqMode are:
            1 or "SAMPLING"       : Setting the sample acquisition.
            2 or "peakdetect"   : Setting peakdetect acquisition.
            3 or "average"      : Setting the averaging acquisition mode.
            4 or "HIGH_RES"     : select higres mode.
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
        return self.visaInstr.query("AVERAGE_ACQUIRE?")

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
        if self.acqMode == "AVERAGE":
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
        