# Necessary imports for all related BaseScope classes to arrange for auto registration of the Tektronix scope
from devices.tektronix.scope.TekScopes import TekScope 
from devices.tektronix.scope.Channel import TekChannel,TekWaveForm, TekWaveFormPreamble
from devices.tektronix.scope.Vertical import TekVertical
from devices.siglent.sds.Scopes import SiglentScope # For auto registration
# For auto registration of BaseSupplies subclasses
from devices.Korad.KoradSupply import Korad3305P, KoradChannel 
from devices.siglent.spd.PowerSupply import SiglentPowerSupply
# For auto registration of BaseDMM subclasses
from devices.siglent.sdm.DigitalMultiMeter import SiglentDMM