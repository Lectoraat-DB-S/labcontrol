from devices.BaseScope import BaseAcquisition
import pyvisa

class TekAcquisition(BaseAcquisition):
    """"Subclass of BaseDisplay for Tektronix TDS1k en 2k scope series. This class implements the baseclass."""

    @classmethod
    def getAcquisitionClass(cls):
        """ Tries to get (instantiate) the device"""
        if cls is TekAcquisition:
            return (cls)
        else:
            return None   
        
    def __init__(self, visaInstr:pyvisa.resources.MessageBasedResource):
        super().__init__(visaInstr)

    def mode(self):
        """Queries the oscilloscope's current acquisition mode.
        Returns the current acquisition setting, which is one of SAMple, PEAKdetect or AVErage."""
        return self.visaInstr.query("ACQuire:MODe?")

    def mode(self, acqMode):
        """Sets the oscilloscope's mode of acquisition.
        Parameters: acqMode, the new acquisiton mode.
        Valid values of parameter acqMode are:
            1 or "sample"       : Setting the sample acquisition.
            2 or "peakdetect"   : Setting peakdetect acquisition.
            3 or "average"      : Setting the averaging acquisition mode.
        If averaging has been selected, one should also set the number of averages."""
        if acqMode== "sample" or acqMode == 1:
            mode = "SAMple"
        elif acqMode== "peakdetect" or acqMode == 2:
            mode = "PEAKdetect"
        elif acqMode== "average"or acqMode == 3:
            mode = "AVErage"
        else:
            return
        self.visaInstr.write(f"ACQuire:MODe {mode}")
        return
    
    def getNumOfAcquisition(self):
        """Indicates the number of acquisitions that have taken place since starting
        oscilloscope acquisition. The maximum number of acquisitions that can be
        counted is 231-1. See TDS programming manual, page 2-41, for further information."""
        return self.visaInstr.query("ACQuire:NUMACq?")

    def averaging(self):
        """Queries the number of oscilloscope waveform acquisitions setted, that make up an averaged
        waveform."""
        return self.visaInstr.query("ACQuire:NUMAVg?")

    def averaging(self, nrOfAvg):
        """Sets the number of oscilloscope waveform acquisitions that make up an averaged
        waveform.
        Parameters: nrOfAvg, the new acquisiton mode.
        Valid values of parameter nrOfAvg are:
            4   : Setting the number of acquisitions to 4.
            16  : Setting the number of acquisitions to 16.
            64  : Setting the number of acquisitions to 64.
            128 : Setting the number of acquisitions to 128.
        """
        
        if nrOfAvg <= 4:
            numAvg = 4
        elif nrOfAvg <= 16:
            numAvg = 16
        elif nrOfAvg <= 64:
            numAvg = 64
        else:
            numAvg = 128
        self.visaInstr.write(f"ACQuire:NUMAVg {numAvg}")
    
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
        