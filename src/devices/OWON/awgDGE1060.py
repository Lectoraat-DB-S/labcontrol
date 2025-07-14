import pyvisa
from devices.BaseGenerator import BaseGenerator, BaseGenChannel
import usb.core
import usb.backend.libusb1

"""LET OP: het werkt met libusb1 omdat ik o.a. de WinUSB driver voor Windows met zadig heb geïnstalleerd.
Tot nu toe werkt dat wel met libusb1.0.dll. op dit moment (26-5) staat WinUsbTmcDll.dll ook in de scripts dir van de python
omgeving. de vraag is of deze dll zorgt voor de functionaliteit of niet. De driver (.inf) die hoort WinUsbTmcDll.dll, kreeg i
ik niet geinstalleerd: windows weigert, onder vermelding dat de beste driver al geinstalleerd is."""

#dit is wat testcode omdat ik aan het klieren was om de own awg dge1060 aan de praat te krijgen onder python
#backend = usb.backend.libusb1.get_backend(find_library=lambda x: "libusb-1.0.dll")
#dev = usb.core.find(idVendor=0x5345, idProduct=0x1235, backend=backend)
"""
dev=rm.open_resource("USB0::21317::4661::24500365::0::INSTR")
dev.timeout = 2000  # ms
dev.read_termination = '\n'
dev.write_termination = '\n'
print(dev.query("*IDN?"))
dev.write("OUTPut1:STATe ON")
"""

class OWONGenChannel(BaseGenChannel):

    @classmethod
    def getGenChannelClass(cls,  chan_no, dev):
        if cls is OWONGenChannel:
            return cls
        else:
            return None     

    def __init__(self, chan_no: int, dev):
        super().__init__(chan_no, None)
        self.name = f"C{chan_no}"
        self.usbDev = dev

    def write(self, command):
        self.usbDev.write(1, command)

    def enableOutput(self, status:bool):
        if status:
            self.write("OUTPut1:STATe ON")
        else:
            self.write("OUTPut1:STATe OFF")

    def setAmplitude(self, amp):
        self.write(f"SOURce1:VOLTage:LEVel:IMMediate:AMPLitude {amp}Vpp")

    def setFrequency(self, freq):
        self.write(f"SOURce1:FREQuency:FIXed {freq}")

    def setSineWave(self,freq=None, amp=None):
        if freq == None or amp == None:
            return
        else:
            self.write("SOURce1:FUNCtion:SHAPe SINusoid")
            self.write(f"SOURce1:VOLTage:LEVel:IMMediate:AMPLitude {amp}Vpp")
            self.write(f"SOURce1:FREQuency:FIXed {freq}")

    def setPulseWave(self):
        self.write("SOURce1:FUNCtion:SHAPe SINusoid")

    def setSquareWave(self):
        pass

    def setPulseWave(self):
        pass

    def setTriangle(self):
        pass

    def setWave(self):
        """
        <Built_in>::={DC|AbsSine|AbsSineHalf|AmpALT|AttALT|GaussPulse|NegRamp|NPulse|
        PPulse|SineTra|SineVer|StairDn|StairUD|StairUp|Trapezia|Heart|Cardiac|LFPulse|
        Tens1|Tens2|Tens3|EOG|EEG|Pulseilogram|ResSpeed|Ignition|TP2A|ISP|VR|TP1|TP2B|
        P4|TP5A|TP5B|SCR|Surge|Airy|Besselj|Bessely|Cauchy|X^3|Erf|Erfc|ErfcInv|ErfInv|
        Dirichlet|ExpFall|ExpRise|Laguerre| Laplace|Legend|Gauss|HaverSine|Log|LogNormal|
        Lorentz|Maxwell|Rayleigh|Versiera| Weibull|Ln(x)|X^2|Round|Chirp|Rhombus|CosH|Cot|
        CotH|CotHCon|CotHPro|CscCon|Csc|CscPro|CscH|CscHCon|CscHPro|RecipCon|RecipPro|SecCon|
        SecPro|SecH|Sinc|SinH|Sqrt|Tan|TanH|ACos|ACosH|ACot|ACotCon|ACotPro|ACotH|ACotHCon|
        ACotHPro|Acsc|ACscCon| ACscPro|AcscH|ACscHCon|ACscHPro|Asec|ASecCon|ASecPro|ASecH|
        ASin|ASinH|ATan|ATanH|Bartlett|BarthannWin|Blackman|BlackmanH|BohmanWin|Boxcar|ChebWin|
        FlattopWin| Hamming|Hanning|Kaiser|NuttallWin|ParzenWin|TaylorWin|Triang|TukeyWin|Butterworth|
        Combin|CPulse|CWPulse|RoundHalf|BandLimited|BlaseiWave|Chebyshev1|Chebyshev2|DampedOsc|DualTone|
        Gamma|GateVibar|LFMPulse|MCNoise|Discharge|Quake|Radar| Ripple|RoundsPM|StepResp|SwingOsc|TV|Voice|AM|FM|PM|PWM}      
        """
        pass

    def setNoise(self):
        pass

    def setArbitrary(self):
        pass

    def setHarmonic(self, amp, order, phase, type):
        """Zie pag 41, Owon, XDG, programming manual. 
        [SOURce[1|2]]:HARMonic:AMPL
        [SOURce[1|2]]:HARMonic:ORDEr 2-16
        [SOURce[1|2]]:HARMonic:PHASe
        [SOURce[1|2]]:HARMonic:TYPe
        
        """
        pass

    def setModulationMode(self, status: bool):
        """[SOURce[1|2]]:MOD:STATe"""

            


class OWONGenerator(BaseGenerator):
   #@classmethod 
   #def decodeIDN(cls, idnquery):
   #   myidn = IDN()
   #   return myidn.decodeIDN(idnquery)


    @classmethod
    def getGeneratorClass(cls, rm, urls, host):
        """
        Tries to get (instantiate) this device, based on matched url or idn response
        This method will ONLY be called by the BaseScope class, to instantiate the proper object during
        creation by the __new__ method of BaseGenerator.     
        """    
        if cls is OWONGenerator:
            if host == None:
                #for url in myurls:
                    #if urlPattern in url:
                        #mydev = myrm.open_resource(url)
                        #mydev.timeout = 10000  # ms
                        #mydev.read_termination = '\n'
                        #mydev.write_termination = '\n'
                        ##desc = mydev.query("*IDN?")
                        #if desc.find("OWON,DGE1060") > -1: #Tektronix device found via IDN.
                return (cls, 1, None)
                #return (None, 0, None)                          
        else:
            return (None, 0, None)

    def __init__(self, nrOfChan=0, visaInstr=None):
        super().__init__(nrOfChan=nrOfChan, instr=visaInstr)
        backend = usb.backend.libusb1.get_backend(find_library=lambda x: "C:\\Users\\p78511225\\.pyenv\pyenv-win\\versions\\3.13.3\\Scripts\\libusb-1.0.dll")
        dev = usb.core.find(idVendor=0x5345, idProduct=0x1235, backend=backend)
        self.nrOfChan = nrOfChan

        self.channels =list()
        for i in range(1, self.nrOfChan+1):
            self.channels.append({i:OWONGenChannel(i, dev)})

    def chan(self, chanNr): 
        """Gets a channel, based on its index: 1, 2 etc."""
        try: 
            for  i, val in enumerate(self.channels):
                if (chanNr) in val.keys():
                    return val[chanNr]
        except ValueError:
            print("Requested channel not available")
            return None   
      