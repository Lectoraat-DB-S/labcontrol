# code for checking functionality of fysical connected TDS (opposite of mocking)
from devices.tektronix.scope.TekScopes import TekScope, TekVertical
from devices.BaseScope import BaseScope, BaseChannel, BaseVertical

def checkMathFunctions():
    scope: TekScope
    scope = BaseScope.getDevice()
    vert = scope.vertical
    print(vert.getMathSettings())