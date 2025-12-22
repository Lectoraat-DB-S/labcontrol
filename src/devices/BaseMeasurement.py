# A base class for organising structured storage of measurements
# terminology: 
#
# 1. Procedure: a sequence of actions conducted in a predefined order. The actions will be performed on an experimental 
# Setup or setting, wich consists of a (number of) power supplies, generators, dmm's and oscilloscopes, around the Device Under
#  Test (DUT) in the center of the setup.
# 2. Action: setting a device (generator, supply for instance) or querying a device (measuring a voltage, getting a waveform
# from a scope). Querying a device is same as acquisition.
# 3. Processing: the steps needed to transform the data gathered during Procedure execution into relevant information.
# 4. Setup: the configuration of hardware and required connections (supply and signals) to/from the DUT and the required data
# connections to the labdevices needed for the setup.
# 5. The Test or the Experiment which is the origin for designing a setup and the construction of some kind of procedure,
# which yield data for further processing.
# Dataprocessing:  digital filtering, quantisation or curve-fitting 
#
#
# Definition of words, based on Internet:
# Electrical Measurements (Wikipedia): Electrical measurements are the methods, devices and calculations used to measure electrical 
# quantities. Measurement of electrical quantities may be done to measure electrical parameters of a system. Using transducers, physical
# properties such as temperature, pressure, flow, force, and many others can be converted into electrical signals, which can then be 
# conveniently measured and recorded. High-precision laboratory measurements of electrical quantities are used in 
# experiments to determine fundamental physical properties such as the charge of the electron or the speed of light, and in the 
# definition of the units for electrical measurements, with precision in some cases on the order of a few parts per million. 
# Less precise measurements are required every day in industrial practice. Electrical measurements are a branch of the science of metrology. 
#
# Experiment:  a procedure carried out in order to support or refute a hypothesis, or determine the efficacy or likelihood 
# of something previously untried. Experiments provide insight into  cause-and-effect by demonstrating what outcome occurs 
# when a particular factor is manipulated.
# 
# Definition of 'test':
#   a procedure intended to establish the quality, performance, or reliability of something, especially before it is taken 
# into widespread use.
# 
# Definition of 'Procedure':
#   a series of actions conducted in a certain order or manner.
#   For Labcontrol: for the Procedure instance one needs certain labdevices and for every labdevice one needs only a subset of 
# all possible "actions" available for tHAT specific labdevices.
#
# If one tries find an value for impedance of a DUT, one performs (an) experiment(s) to measure the impedance.
# A measurement is not just do one iteration during a labsession. A measurements is the process in trying do determine a physical
# quantity and compare it to a theoretical or another measurement.
class LabAction(object):
    """An action is doing a setting or make a quiry to a LabDevice.
    TODO: define if a labdevice belongs to action or the way around."""
    def __init__(self, actionType, BaseLabDevice):
        """Create an Action by defining what kind of action (a setting or a quiry) and the kind of device, e.g. supply, 
        generator or scope."""
        pass
    
    def destroy(self):
        """Remove the action"""
        pass

class Setup(object):
    def __init__(self):
        self.devices = list()

    def addLabDevive(self, dev):
        self.devices.append(dev)
        return 2 # return a id for the device, which might be a visa handle or the handle to the object or index in a list.

    def addAction2Device(self, deviceId, action):
        pass

class Acquisition(object):
    def __init__(self):
        self.tstamp = None # time stamp
        self.type = None    # kind of acquisition: scope waveform (data and preamble), scope meas, dmm meas, generator settings, 
                            # supply settings, scope settings(? probaly equal to preamble)


class MeasurementData(object):
    """MeasurementData: Base class for holding the data, or acquisitions, acquired during procedure execution."""

    def __init__(self):
        self.title = None # the title of the data
        self.descr = None # A description of the data or measurement done
        self.date = None
        self.type = None # type of measurement or data, AC sweep for instance
        self.procedure = None # the procedure needed to get this data.
        self.measData = list() # the container/list to store/dump the data in. Likely to be a long list of pd.Dataframes with data

    def add(self, newData):
        self.measData.append(newData)

class Procedure(object):
    def __init__(self):
        self.sequence = list()
        self.setup = Setup()

    def initialize(self):
        #check if all labdevice of the setup is operational.
        pass

    def addAction(self, newAction):
        """An action is either a. send an setting to a device, whether the device might send a response, or b. send a quiry to
         a device to ask for data."""
        self.sequence.append(newAction)

    def run(self, loop: bool):
        # execute the procedure
        pass        
        

