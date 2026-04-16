import pyvisa   

class Display(object):
    """BaseDisplay: a baseclass for the abstraction of a Display unit of an oscilloscope.
    All display implementations have to inherit from this baseclass.
    1. This base class takes care for subclass auto registration, according to pep487, See:  
    https://peps.python.org/pep-0487/
    2. Implementing subclasses HAVE TO fully implement the getChannelClass method of this class.
    3. Be sure this BaseChannel implementation has access to all inheriting subclasses during creation. If not, 
    the subclass won't be registered and creating the needed channel object(s) will fail."""

    displayList = []

    def __init_subclass__(cls, **kwargs):
        """Method for auto registration of BaseChannel subclasses according to PEP487.
        DO NOT ALTER THIS METHOD NOR TRY TO OVERRIDE IT.
        """
        super().__init_subclass__(**kwargs)
        cls.displayList.append(cls)
    
    @classmethod
    def getDisplayClass(cls, dev):
        """getChannelClass: factory method for scope channel objects. 
        Remark: this baseclass implementation is empty, must be implemented by the subclass. """
        pass

    def __init__(self, visaInstr:pyvisa.resources.MessageBasedResource):
        """Method voor initialising this Channel object.
        Remark: if the subclass relies the intialisation done below, don't forget to call super().__init()__ !"""
        self.visaInstr = visaInstr

    def format(self):
        pass

    def format(self, mode):
        pass

    def persist(self):
        pass
    
    def persist(self, persmode):
        pass

    

