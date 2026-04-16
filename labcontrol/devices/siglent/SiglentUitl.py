class SiglentIDN(object):
    def __init__(self, mybrand, mymodel, myserial, myfirmware) -> None:
        self.brand = mybrand
        self.model = mymodel
        self.serial = myserial
        self.firmware = myfirmware
        self.modelNr = None
        self.modelSupp = None
        

    def getModel(self, devStr:str, typeIdStrs:list):
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
        brandStr = "Siglent"
        res = devStr.find(brandStr)
        if res != -1:
            devStr=devStr.strip(brandStr)
        devStr = devStr.strip()
        devStr = devStr.strip("-") #the sectionname should now start with some alphabetic tokens like "SDS" or "SHS"
        myTypeIdStr:str
        typeFound: bool = False
        for myTypeIdStr in typeIdStrs:
            if myTypeIdStr in devStr:
                typeFound = True
        
        if not typeFound: 
            return None
        #A siglent device have been found, now check the numbers
        
        tmp1 = devStr[3:6]
        tmp2 = devStr[3:7]
        devNr = None
        if tmp2.isnumeric():
            #4 digit number
            devNr = int(tmp2)
            suppStr = devStr[7:]
            self.modelNr = devNr
            self.modelSupp = suppStr
        
            return devNr, suppStr
        else:
            if tmp1.isnumeric():
                #it is a 3 digit modelnum
                devNr = int(tmp1)
                suppStr = devStr[6:]
                self.modelNr = devNr
                self.modelSupp = suppStr
                return devNr, suppStr
            else:
                return None
            
    def isModelInRange(self, seriesNr: str, typeIdStrs:list):
        """
        KNOWN_MODELS = [
        "SDS5000X",         #0.9.0 and later
        "SDS2000X Plus",    #1.3.5R3 and later
        "SDS6000 Pro",      #1.1.7.0 and later
        "SDS6000A+",        #1.1.7.0 and later
        "SHS800X",          #1.1.9 and later
        "SHS1000X",         #1.1.9 and later
        "SDS2000X HD",      #1.2.0.2 and later
        "SDS6000L",         #1.0.1.0
    ]
        """
        myTypeIdStr:str
        typeFound: bool = False
        for myTypeIdStr in typeIdStrs:
            if myTypeIdStr in seriesNr:
                typeFound = True
        
        if not typeFound: 
            return False
        
        splitted = seriesNr.split()
        if len(splitted) == 1:
            #het serienummer bestaat uit 1 deel
            (startModelRange, eindModelRange)= createBeginEndRange(splitted[0])
            
            if startModelRange != None and eindModelRange != None:
                myStartRange = int(startModelRange)
                myEndRange = int(eindModelRange)
                if self.modelNr in range(myStartRange, myEndRange):
                    return True
                else:
                    return False
            else:
                return False        
        elif len(splitted) == 2:
            #het serienummer bestaat uit tweedelen
            self.modelSupp = splitted[1]
            (startModelRange, eindModelRange)= createBeginEndRange(splitted[0])
            if startModelRange != None and eindModelRange != None:
                myStartRange = int(startModelRange)
                myEndRange = int(eindModelRange)
                if self.modelNr in range(myStartRange, myEndRange):
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False
    
       
        

def decodeIDN(idnstr:str):
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

        
def createBeginEndRange(theModelStr:str):
    modelStr = theModelStr
    tmp1 = modelStr[0:3]# first three characters are all letters
    if tmp1.isalpha():
        if modelStr[-2:].isalpha():#
            #de laatste twee tekens zijn beide letters
            mymodelNr = modelStr[3:-2]
            machtGetal = len(mymodelNr)-1 #bijv 2000 heeft
            startModelRange = mymodelNr[0]
            eindModelRange = mymodelNr[0]
            for x in range(1, machtGetal):
                startModelRange[x]='0'
                eindModelRange[x] ='9'
            return (startModelRange, eindModelRange)
        elif modelStr[-1:].isalpha():
            #het laatste teken is een letter.
            mymodelNr = modelStr[3:-1]
            machtGetal = len(mymodelNr)-1 #bijv 2000 heeft
            startModelRange = mymodelNr[0]
            eindModelRange = mymodelNr[0]
            for x in range(1, machtGetal):
                startModelRange[x]='0'
                eindModelRange[x] ='9'
            return (startModelRange, eindModelRange)
        return (None, None)
    else:
        return (None, None)
    

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

def getModel(devStr:str):
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
