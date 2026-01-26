### import for using undefined names as parameters, which will be resolved later
from __future__ import annotations #is this import still necessary. It is not defined by pep484

import devices.BaseLogger


#### import for autoregistration of BaseScope subclasses ##########
# section: Tektronix scope
from devices.tektronix.scope.TekScopes import TekScope 
from devices.tektronix.scope.Channel import TekChannel,TekWaveForm, TekWaveFormPreamble
from devices.tektronix.scope.Vertical import TekVertical
from devices.tektronix.scope.Horizontal import TekHorizontal
from devices.tektronix.scope.Trigger import TekTrigger
from devices.tektronix.scope.Acquisition import TekAcquisition
from devices.tektronix.scope.display import TekDisplay


# section: Siglent scope
from devices.siglent.sds.Scopes import SiglentScope

#from devices.siglent.sds.SDS1000.SDS1k import SiglentScope1k # For auto registration
#from devices.siglent.sds.SDS1000.Channel import SDSChannel, SDSWaveForm, SDSWaveFormPreamble
#from devices.siglent.sds.SDS1000.Vertical import SDSVertical
#from devices.siglent.sds.SDS1000.Horizontal import SDSHorizontal
#from devices.siglent.sds.SDS1000.Trigger import SDSTrigger

#from devices.siglent.sds.SDS2000.SDS2k import SiglentScope # For auto registration
#from devices.siglent.sds.SDS2000.Channel import  SDS2kChannel, SDS2kWaveForm, SDSWaveFormPreamble
#from devices.siglent.sds.SDS2000.Vertical import SDS2kVertical
#from devices.siglent.sds.SDS2000.Horizontal import SDSHorizontal
#from devices.siglent.sds.SDS2000.Trigger import SDSTrigger

# For auto registration of BaseSupplies subclasses
#from devices.Korad.KoradSupply import Korad3305P, KoradChannel 
from devices.siglent.spd.PowerSupply import SiglentPowerSupply, SPDChannel
# For auto registration of BaseDMM subclasses
from devices.siglent.sdm.DigitalMultiMeter import SiglentDMM

# For auto registration of BaseGenerator subclasses
from devices.siglent.sdg.Generator import SiglentGenerator
from devices.siglent.sdg.Channels import SDGChannel
from devices.OWON.awgDGE1060 import OWONGenerator, OWONGenChannel

# For auto registration of BaseDMM subclasses
#from devices.siglent.sdm import DigitalMultiMeter