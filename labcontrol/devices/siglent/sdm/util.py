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

class SiglentIDN(object):
    #vb mymodel=Siglent SDS2104X-Plus
    def __init__(self, mybrand, mymodel, myserial, myfirmware) -> None:
        self.brand = mybrand
        self.model:str = mymodel
        self.serial = myserial
        self.firmware = myfirmware
        self.modelSeriesId = None
        self.modelNr = None
        self.modelSupp = None

        mySeriesId, myModelNr, myModelSupp = splitModelString(mymodel)
        self.modelNr = int(myModelNr)
        self.modelSupp = myModelSupp
        self.modelSeriesId = mySeriesId
    
            
    def isModelInRange(self, seriesNr: str)->bool: 
        """Method for checking whether or not this IDN falls within a series defined by parameter
        SeriesNr.
        This method performs the following operations and checks.
        1. It split parameter seriesNr in three part: a) the tree letter for defining the series
        b) number of the series and c) the supplemental part consisting one of more letters. TODO:
        the supplemental extraction code will not handle dashes correctly!
        2. Checking if this IDN starts with the same three letters.
        3. create a range out of the parameter seriesNr
        4. If the range creation is successfull, this method check if this IDN falls into the range.
        5. Finally, the supplemental part of this IDN will be compared to the supplemental part of
        the parameter seriesNr.
        Only if all steps succeeds, this method will return True, otherwise it will return False."""
        
        #split the parameter SeriesNr
        tempSeriesId, tempModelNr, tempSuppl = splitModelString(seriesNr)
        
        #check the first 3 letters.
        if self.modelSeriesId not in tempSeriesId:
            return False
        #create a range out of seriesNr
        (startModelRange, eindModelRange)= createBeginEndRange(tempModelNr)
            
        #check of this IDN is in range.
        if startModelRange == None and eindModelRange == None:
            return False
        
    
        myStartRange = int(''.join(startModelRange))
        myEndRange = int(''.join(eindModelRange))
        if self.modelNr not in range(myStartRange, myEndRange):
            return False
        
        #finally, check supplemental part of both.
        if self.modelSupp in tempSuppl:
            return True
        else:
            return False
        
def splitModelString(theModelStr:str)-> tuple[str, str, str]:
    devStr:str = None
    myTempSuppStr = None
    mySeriesIdStr = None
    brandStr = "Siglent"    #stel mymodel=Siglent SDS2104X-Plus 
    res = theModelStr.find(brandStr) #in dit geval wordt siglent gevonden
    if res != -1:
        devStr=theModelStr.strip(brandStr) # en dus is resutlaat devstr = " SDS2104X-Plus"
    else:
        devStr = theModelStr
    
    devStr:str = devStr.strip() # en nu is devStr = "SDS2104X-Plus" (spatie eraf.)
    devStr = devStr.split("-")  # en nu is devStr[0] = "SDS2104X" (-Plus eraf, defStr[1] = Plus.)
    if len(devStr)<1:
        #TODO: dit is een error
        return None, None, None
    
    myDevStr = devStr[0]
    if len(devStr)>1:
        myTempSuppStr = devStr[1]
    
    if "SDM" in myDevStr:
        mySeriesIdStr = "SDM"
    else:
        mySeriesIdStr = None
        return None, None, None
    #A siglent device have been found, now check the numbers
    
    tmp1 = myDevStr[3:6]
    tmp2 = myDevStr[3:7]
    devNrStr = None
    if tmp2.isnumeric():
        #4 digit number
        devNrStr = tmp2
        if myTempSuppStr == None:
            suppStr = myDevStr[7:]
        else:
            suppStr = myDevStr[7:]+"-"+myTempSuppStr
        return mySeriesIdStr, devNrStr, suppStr 
    else:
        if tmp1.isnumeric():
            #it is a 3 digit modelnum
            devNrStr = tmp1
            if myTempSuppStr == None:
                suppStr = myDevStr[6:]
            else:
                suppStr = myDevStr[6:]+"-"+myTempSuppStr
            return mySeriesIdStr,devNrStr, suppStr   
        

def decodeIDN(idnstr:str)->SiglentIDN:
        """
        example
        Siglent Technologies,SDS1204X-E,SDS1EBAC0L0098,7.6.1.15
        """
        splitted = idnstr.split(",")
        if len(splitted) != 4:
            return None
        manufacturer  = "Siglent"
        if manufacturer in splitted[0]:
            if len(splitted[2])==14:
                brand = splitted[0]
                model = splitted[1]
                serial = splitted[2]
                firmware = splitted[3]
                siglentIdn = SiglentIDN(brand,model, serial, firmware) 
                return siglentIdn
        return None

        
def createBeginEndRange(theModelStr:str)-> tuple[list, list]:
    modelLengte = len(theModelStr)
    startModelRange:list =list()
    eindModelRange:list = list()
    startModelRange.append(theModelStr[0])
    eindModelRange.append(theModelStr[0])
    for x in range(1, modelLengte):
        startModelRange.append('0')
        eindModelRange.append('9')
    return (startModelRange, eindModelRange)

#hulpfunctie
def splitAndStripV(response):
    response =response.rstrip()
    response =response.strip("V")
    splitted = response.split(",")
    return float(splitted[1])

def splitAndStripHz(response):
    response =response.rstrip()
    response =response.strip("Hz")
    splitted = response.split(",")
    return float(splitted[1])

def splitAndStripSec(response):
    response =response.rstrip()
    response =response.strip("s")
    response =response.strip("S")
    splitted = response.split(",")
    return float(splitted[1])

def splitAndStripProc(response):
    response =response.rstrip()
    response =response.strip("%")
    splitted = response.split(",")
    return float(splitted[1])
"""
def getModel(devStr:str):
"""
"""
        Parameters: 
            devStr: de sectienaam uit de ini-file
            models: een lijst met typenummers die horen bij deze class. 
        Siglent heeft een strak modelnummer schema, zo lijkt het tenminste. Desktop/Bench scopes beginnen met de 
        letters SDS en handhelds met de letters SHS. Daarna volgen 3 of 4 cijfers en eventueel wat letters, al dan niet met 
        spaties en/of streepjes.
        De ini. file moet deze richtlijn volgen. Mogelijk komt er 'Siglent ' voorafgaande het modelnummer te staan, maar dat 
        zijn dan de opties.
        Aanpak voor decodering:
        1. Zit 'Siglent' in de sectienaam van de ini file? Zo ja, dan moet die vooraan staan. Verder niks mee doen
        2. Zit 'Siglent' niet in de sectie naam, dan moet, na strippen van spaties en streepjes de letters "SDS" of "SHS"
        komen. Zitten die er niet in, return false.
        3. Na de letters "SDS" of "SHS" moeten er 3 of 4 cijfers komen, zo niet -> return false
        4. Het gevonden modelnr van 3 of 4 cijfers moet vergeleken worden met KNOWN_MODELS. 
        Meest eenvoudige manier om te checken of een klasse de juiste sectie uit de ini pakt, is
        door de nummers uit de strings te isoleren.
        Eigenlijk heb ik twee functies nodig: 1. haal de nummers uit een string, bijv 12345AXD34, moet dan twee getallen
        opleveren 12345 en 34. 2. Haal de alpha tekens uit de string, dus bij dezelfde string is dat AXD."""
"""
        brandStr = "Siglent"
        res = devStr.find(brandStr)
        if res != -1:
            devStr=devStr.strip(brandStr)
        devStr = devStr.strip()
        devStr = devStr.strip("-") #the sectionname should now start with "SDS" or "SHS"
        if "SDS" not in devStr and "SHS" not in devStr:
            return None
        #A siglent device have been found, now check the numbers
        
        tmp1 = devStr[3:6]
        tmp2 = devStr[3:7]
        devNr = None
        if tmp2.isnumeric():
            #4 digit number
            devNr = int(tmp2)
            suppStr = devStr[7:]
            return devNr, suppStr
        else:
            if tmp1.isnumeric():
                #it is a 3 digit modelnum
                devNr = int(tmp1)
                suppStr = devStr[6:]
                return devNr, suppStr
            else:
                return None
"""    
