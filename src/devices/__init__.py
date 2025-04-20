from devices.tektronix.scope.TekScopes import TekScope # Necessary import for BaseScope fore auto registration of Tektronix class
from devices.siglent.sds.Scopes import SiglentScope # For auto registration
# For auto registration of BaseSupplies subclasses
from devices.Korad.KoradSupply import Korad3305P 
from devices.siglent.spd.PowerSupply import SiglentPowerSupply