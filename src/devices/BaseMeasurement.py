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
# Experiment:  a procedure carried out in order to support or refute a hypothesis, or determine the efficacy or likelihood 
# of something previously untried. Experiments provide insight into  cause-and-effect by demonstrating what outcome occurs 
# when a particular factor is manipulated.
# Defnition of 'test':
#   a procedure intended to establish the quality, performance, or reliability of something, especially before it is taken into widespread use.
# Definition of 'Procedure':
#   a series of actions conducted in a certain order or manner.
#   For Labcontrol: for the Procedure instance one needs certain labdevices and for every labdevice one needs only a subset of 
# all possible "actions" available for tHAT specific labdevices.
#

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
        

