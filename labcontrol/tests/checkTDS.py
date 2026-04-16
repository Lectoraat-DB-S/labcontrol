# code for checking functionality of fysical connected TDS (opposite of mocking)
from devices.tektronix.scope.TekScopes import TekScope, TekVertical
from devices.BaseScope.BaseScope import Scope
from devices.BaseScope.BaseVertical import Vertical

def checkMathFunctions():
    scope: TekScope
    scope = Scope.getDevice()
    vert: Vertical = scope.vertical
    print(vert.getMath('FFT', vert.chan(1)))