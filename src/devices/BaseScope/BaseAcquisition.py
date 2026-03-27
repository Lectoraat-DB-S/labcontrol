import pyvisa

class Acquisition(object):
    """Acquisiton: a baseclass for the abstraction of doing acquisitions with an oscilloscope.
    """

    acquisitionList = []

    def __init_subclass__(cls, **kwargs):
        """Method for auto registration of Acquisition subclasses according to PEP487.
        DO NOT ALTER THIS METHOD NOR TRY TO OVERRIDE IT.
        """
        super().__init_subclass__(**kwargs)
        cls.acquisitionList.append(cls)
    
    @classmethod
    def getAcquisitionClass(cls, dev):
        """getAcquisitionClass: factory method for Acquisition objects. 
        Remark: this baseclass implementation is empty, needed logic will have top be implemented by the subclass."""
        pass

    def __init__(self, visaInstr:pyvisa.resources.MessageBasedResource):
        """Method voor initialising this Acquisition object.
        Remark: if the subclass relies on the intialisation done below, don't forget to call super().__init()__ !"""
        self.visaInstr = visaInstr

    def mode(self):
        pass

    def mode(self, acqMode):
        pass

    def getNumOfAcquisition(self):
        pass

    def averaging(self):
        pass

    def averaging(self, nrOfAvg):
        pass

    def state(self):
        pass

    def state(self, runMode):
        pass