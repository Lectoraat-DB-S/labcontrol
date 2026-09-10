from devices.BaseScope.BaseCommands import IEEE488Command
import logging
import pyvisa

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class SDS1kCommands(IEEE488Command):
    
    INR_TRIGGER_READY = 8192
    INR_NEW_SIGNAL_ACQUIRED = 1
    
    
    def __init__(self, visaInstr = None):
        super().__init__(visaInstr)
    
    @classmethod
    def getIEEE488CommandClass(cls, visaInstr:pyvisa.resources.MessageBasedResource=None):
        """
            Tries to get (instantiate) this device, based on matched cls
            This method will ONLY be called by the BaseScope class or other Scope related Baseclasses, 
            to instantiate the proper object during creation by the __new__ method according to PEP487.     
        """    
        if cls is SDS1kCommands:
            return cls
        else:
            return None   
    
    def OPC(self):
        """Method for sending an * OPC? query to the instrument. 
        A recent version of the programming manual (document number EN02E) states:
        
        The *OPC command sets the operation complete bit in the Standard Event Status Register when all pending device operations have finished. The *OPC? query places an ASCII "1" in the output queue when all pending device operations have completed. The interface hangs until this query returns. 
        
        However, testing with Siglent SDS1202XE (latest firmware version) sampling at low speeds, results in an immediate return from this call. This behaviour might originate of testing the wrong way, but a bug in the firmware is more likely. Especially when the description of the very same command/query from an old programming manual says:
        
        The *OPC (OPeration Complete) command sets to true the OPC bit (bit 0) in the standard Event Status Register (ESR). This command has no other effect on the operation of the oscilloscope because the instrument starts parsing a command or query only after it has completely processed the previous command or query. The *OPC? query always responds with the ASCII character '1' because the oscilloscope only responds to the query when the previous command has been entirely executed.  
        
        This description corresponds to the observed behaviour of the scope. Probably, there is no EN02E version of the firmware available for the 1000X-E oscilloscope series.
        """
        resp = self.visaInstr.query("*OPC?")
        return resp
    
    def INR(self):
        """
        The INR? query reads and clears the contents of the INternal state change Register (INR). 
        The INR register (see table programming manual) records the completion of various internal operations 
        and state transitions.
        
        An old version of the programming manual states cleary only bit 0 and 13 is supported. So this query only returns the value 0,1, 8192 or 8193
        """
        intVal = -1
        inrResp = self.query("INR?")
        #return INR_HASHMAP[inrResp] #this crashed
        inrSplitted = inrResp.split()
        if len(inrSplitted)!=2 or inrSplitted[0] != "INR":
            logger.info("Error INR: unexpected response. Return to caller")
            return "ERROR INR: see log."
        else:
            intVal = int(inrSplitted[1])
        return intVal
    
    def getINR(self):
        """
        The getINR methode uses the INR method to read  contents of the INternal state change Register (INR) after it decodes the value return in easy to read meassages.
        """
        INRHASH=["A new signal has been acquired\n", "A screen dump has terminated\n", "A return to the local state is detected\n", "A time-out has occurred in a data block transfer\n", "A segment of a sequence waveform has been acquired\n",
        "Reserved for LeCroy use\n","Memory card, floppy or hard disk has become full in ―AutoStore Fill‖ mode\n","A memory card, floppy or hard disk exchange has been detected\n","Waveform processing has terminated in Trace A\n","Waveform processing has terminated in Trace B\n","Waveform processing has terminated in Trace C\n", "Waveform processing has terminated in Trace D\n","Pass/Fail test detected desired outcome\n","Trigger is ready\n", "Reserved for future use\n","Reserved for future use\n"]
        inrResp: str = self.INR()
        inrSplitted = inrResp.split()
        if len(inrSplitted)!=2 or inrSplitted[0] != "INR":
            logger.info("Error INR: unexpected response. Return to caller")
            return "ERROR INR: see log."
        else:
            intVal = int(inrSplitted[1])
        msg = ""
        for i in range (0,16):
            myMask =  (intVal >> i) & 0x01
            if myMask:
                msg = msg + INRHASH[i]
                
        if msg == "":
            msg = "No INR messages available."
        return msg
    
    def STB(self):
        """
        Read STB by sending the corresponding SCPI command '*STB?' instead of using the dedicated VISA read_stb() function.
        """
        resp = self.visaInstr.query("*STB?")
        return resp
    
    def getSTB(self):
        """
        This method sends a *STB? query towards the instrument for reading  the contents of the 488.1 defined status register (STB), and the Master Summary Status (MSS). The response represents the values of bits 0 to 5 and 7 of the Status Byte register and the MSS summary message. It translate the byte value into a readable message. See page 109 of the Siglent programming manual RC01020-E01C. 
        """
        STBHASHTABLE={0: "INB: an enabled INternal state change has occurred.\n", 1: "DIO1: reserved.\n", 2:"VAB: a command data value has been adapted.\n", 3: "DIO3: reserved\n", 4: "MAV: output queue is not empty.\n", 5: "ESB: an ESR enabled event has occurred.\n", 6: "MSS/RQS MSS=1 RQS=1: at least 1 bit in STB masked by SRE is 1 service is requested.\n", 7: "DIO7: reserved for future use.\n"}
        
        stbResp: str = self.STB()
        #print(f"stb out: {stbResp}")
        stbSplitted = stbResp.split()
        if len(stbSplitted)!=1:
            logger.info("Error STB: unexpected response. Return to caller")
            return "Error STB. See log."
        else:
            intVal = (int(stbSplitted[0]))&0xFF
        msg = ""
        for i in range (0,16):
            myMask =  (intVal >> i) & 0x01
            if myMask:
                msg = msg + STBHASHTABLE.get(i)
                
        if msg == "":
            msg = "No STB messages available."
        return msg
    
    def SRE(self):
        resp = self.query("*SRE?")
        return resp
    
    def ESE(self, newValue = None):
        if newValue == None:
            resp = self.query("*ESE?")
            return resp
        else:
            self.write(f"*ESE {newValue}")
            return None

    def getESE(self):
        """
        Converts the value returned by ESE() to a readable string.

        """
        ESEHASHTABLE={0: "OPC : Instrument never requests bus control.\n", 1: "RQC: Instrument never requests bus control.\n", 2:"QYE: Query Error occurred.\n", 3: "DDE: Device specific Error occurred.\n", 4: "EXE: Execution Error detected.\n", 5: "CME: Command parser Error has been detected.\n", 6: "URQ: User Request has been issued.\n", 7: "PON: Power off-to-ON transition as occurred.\n", 8: "reserved by IEEE 488.2.\n", 9: "reserved by IEEE 488.2.\n", 10: "reserved by IEEE 488.2.\n", 11: "reserved by IEEE 488.2.\n", 12: "reserved by IEEE 488.2.\n", 13: "reserved by IEEE 488.2.\n", 14: "reserved by IEEE 488.2.\n", 15: "reserved by IEEE 488.2.\n"}
        eseRsp = self.ESE(None)
        eseSplitted = eseRsp.split()
        #print("ESE printout")
        #print (eseRsp)
        if len(eseSplitted)!=1:
            logger.info("Error ESE: unexpected response. Return to caller")
            return "Error ESE. See log."
        else:
            msg = ""
            intVal = int(eseSplitted[0])
            for i in range (0,16):
                myMask =  (intVal >> i) & 0x01
                if myMask:
                    msg = msg + ESEHASHTABLE.get(i)
            if msg=="":
                msg = "ESE: no events available"
            return msg
        
        
    def CMR(self):
        return self.query("CMR?")
    
    def getCMR(self):
        """
        Converts the value returned by CMR() into a humanreadable string.
        """
        CMRHASTABLE = {0: "No ERRORS", 1: "Unrecognized command/query header", 2: "Invalid character", 3: "Invalid separator", 4: "Missing parameter", 5: "Unrecognized keyword", 6: "String error", 7: "Parameter cannot allowed", 8: "Command String Too Long", 9: "Query cannot allowed", 10: "Missing Query mask", 11: "Invalid parameter", 12: "Parameter syntax error", 13: "Filename too long"}
        cmrResp = self.CMR()
        cmrSplitted = cmrResp.split()
        if len(cmrSplitted)!=2 or cmrSplitted[0] != "CMR":
            logger.info("Error CMR: unexpected response. Return to caller")
            return "Error CMR. See log."
        else:
            intVal = int(cmrSplitted[1])
            return CMRHASTABLE.get(intVal)
        
    
    def CLS(self):
        """
        The *CLS command clears all the status data registers.
        """
        self.write("*CLS")
    
    def DDR(self):
        resp = self.query("DDR?")
        return resp
    
    def URR(self):
        resp = self.write("URR")
        return resp
    
    def EXR(self):
        resp = self.query("EXR?")
        return resp
    
    def getEXR(self):
        """
        
        """
        EXRHASTABLE = {0: "EXR: No Error\n", 21: "Permission error. The command cannot be executed in local mode.\n", 22: "Environment error. The instrument is not configured to correctly process a command. For instance, the oscilloscope cannot be set to RIS at a slow timebase.\n", 23: "Option error. The command applies to an option which has not been installed.\n", 25: "Parameter error. Too many parameters specified.\n", 26: "Non-implemented command.\n", 32: "Waveform descriptor error. An invalid waveform descriptor has been detected.\n",36: "Panel setup error. An invalid panel setup data block has been detected.\n", 50: "No mass storage present when user attempted to access it.\n", 53: "Mass storage was write protected when user attempted to create, or a file, to delete a file, or to format the device.\n", 58: "Mass storage file not found.\n", 59: "Requested directory not found.\n", 61: "Mass storage filename not DOS compatible, or illegal filename.\n", 62: "Cannot write on mass storage because filename already exists.\n" }
        exrResp: str = self.EXR()
        exrSplitted = exrResp.split()
        if len(exrSplitted)!=2 or exrSplitted[0] != "EXR":
            logger.error("Error EXR: unexpected response. Return to caller")
            return "Error EXR. See log."
        else:
            intVal = int(exrSplitted[1])
            return EXRHASTABLE.get(intVal)
        
    def ESR(self):
        return self.query("*ESR?")
    
    def getESR(self):
        ESRHASHTABLE={0: "OPC : Instrument never requests bus control.\n", 1: "RQC: Instrument never requests bus control.\n", 2:"QYE: Query Error occurred.\n", 3: "DDE: Device specific Error occurred.\n", 4: "EXE: Execution Error detected.\n", 5: "CME: Command parser Error has been detected.\n", 6: "URQ: User Request has been issued.\n", 7: "PON: Power off-to-ON transition as occurred.\n", 8: "reserved by IEEE 488.2.\n", 9: "reserved by IEEE 488.2.\n", 10: "reserved by IEEE 488.2.\n", 11: "reserved by IEEE 488.2.\n", 12: "reserved by IEEE 488.2.\n", 13: "reserved by IEEE 488.2.\n", 14: "reserved by IEEE 488.2.\n", 15: "reserved by IEEE 488.2.\n"}
        esrRsp = self.ESR()
        #print(f"ESR query = {esrRsp}")
        esrSplitted = esrRsp.split()
        if len(esrSplitted)!=1:
            logger.info("Error ESR: unexpected response. Return to caller")
            return "Error ESR: see log"
        else:
            msg = ""
            intVal = int(esrSplitted[0])
            for i in range (0,16):
                myMask =  (intVal >> i) & 0x01
                if myMask:
                    msg = msg + ESRHASHTABLE.get(i)
            if msg=="":
                msg = "ESR: no events available"
            return msg
    
    def RST(self):
        """
            The RST command initiates a device reset. The RST sets recalls the default setup.
        """
        self.write("*RST")
    
    def SAV(self, panelNr):
        """
            The SAV command stores the current state of the instrument in internal memory. The SAV command stores 
            the complete front-panel setup of the instrument at the time the command is issued."""
        self.write(f"*SAV{panelNr}")

    def RCL(self, panelNr):
        """
            The RCL command sets the state of the instrument, using one of the ten non-volatile panel setups, by 
            recalling the complete front-panel setup of the instrument. Panel setup 0 corresponds to the default panel 
            setup.
        """
        self.write(f"*RCL{panelNr}")