from enum import Enum

class MeasType(Enum):
    AC = 0
    DC = 1

def checkMeasType(type2Check):
    meastype = "DC"
    if type2Check == MeasType.DC:
        meastype = "DC"
    elif type2Check == MeasType.AC:
        meastype = "DC"
    else:
        # Hmm, `direction` does not compare equal to any enum value:
        #raise ValueError("Invalid direction "+ str(direction))
        meastype = "DC"
    return meastype