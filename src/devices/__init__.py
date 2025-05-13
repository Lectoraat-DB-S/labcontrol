#### import for autoregistration of BaseScope subclasses ##########
# section: Tektronix scope
from devices.tektronix.scope.TekScopes import TekScope 
from devices.tektronix.scope.Channel import TekChannel,TekWaveForm, TekWaveFormPreamble
from devices.tektronix.scope.Vertical import TekVertical
from devices.tektronix.scope.Horizontal import TekHorizontal
from devices.tektronix.scope.Trigger import TekTrigger

# section: Siglent scope
from devices.siglent.sds.Scopes import SiglentScope # For auto registration
from devices.siglent.sds.Channel import SDSChannel, SDSWaveForm, SDSWaveFormPreamble
from devices.siglent.sds.Vertical import SDSVertical
from devices.siglent.sds.Horizontal import SDSHorizontal
from devices.siglent.sds.Trigger import SDSTrigger

# For auto registration of BaseSupplies subclasses
from devices.Korad.KoradSupply import Korad3305P, KoradChannel 
from devices.siglent.spd.PowerSupply import SiglentPowerSupply
# For auto registration of BaseDMM subclasses
from devices.siglent.sdm.DigitalMultiMeter import SiglentDMM