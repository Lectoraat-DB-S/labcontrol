import devices.siglent.sdm.DigitalMultiMeter as multimeter
from devices.siglent.sds.Scopes import SiglentScope
printDebug = True

def meetweerstandTW(labDev :multimeter.SiglentDMM):
    print("Meetprocedure voor het meten van weerstandswaarde (two-wire measurement)")
    print("Sluit de meetkabels aan en sluit ze kort.")
    input("Druk een toets om verder te gaan.")
    Rloss=labDev.get_resistanceTW()
    print(Rloss)
    print("Sluit de weerstand aan.")
    input("Druk een toets om verder te gaan.")
    Rx=labDev.get_resistanceTW()
    print(Rx-Rloss)
    return (Rx-Rloss)
    

def meetInterneWeerstandGenerator():
    #voor deze meting heb je een DMM, een funtiegenerator en een scoopnodig
    dmm = multimeter.SiglentDMM()
    scope = SiglentScope()
    #scope.CH1
    if scope == None:
        print("Fout: geen scoop gevonden! Exit!")
        return
    else:
        print("Scoop gevonden!")
        
    Rload = meetweerstandTW(dmm)
    print("Stel kanaal 1 van de functiegenerator in op sinus, 1 kHz, 2 Vpp. Let op: zet kanaal 1 wel aan! ")
    input("Druk een toets om verder te gaan.")
    print("Sluit een oscilloscoop aan op kanaal 1 van de functiegenerator. Gebruik daarvoor kanaal 1 van de oscilloscoop. ")
    input("Druk een toets om verder te gaan.")
    print("Meet met de oscilloscoop de amplitude (piek-piek)")
    #VmeasPPstudOpen=float(input("Voer meetwaarde amplitude in"))
    print("Meet met de oscilloscoop de frequentie in Hz")
    #freqstud=float(input("Voer meetwaarde frequentie (Hz) in"))
    input("Druk een toets om verder te gaan.")
    #opvragen van instelling van oscilloscoop en controle goed/niet goed
    #eventueel instellen scoop voor de beste meting
    VmeasPPOpen=scope.CH1.getAmplitude()
    print("Meetwaarde amplitude: "+str(VmeasPPOpen))
    freqmeas=scope.CH1.getFrequency()
    print("Meetwaarde frequentie: "+str(freqmeas))
    #Controleer meetwaarden student met autom waarden. 
    print("Sluit de weerstand aan op kanaal 1 van de functiegenerator (zie schema).")
    print("Sluit de oscilloscoop op de juiste manier over de weerstand aan.")
    print("Meet met de oscilloscoop de amplitude (piek-piek) van de spanning over de weerstand")
    input("Druk een toets om verder te gaan.")
    #VmeasPPstudLoaded=float(input("Voer meetwaarde amplitude in"))
    VmeasPPLoaded=scope.CH1.getAmplitude()
    print("Meetwaarde opbelaste amplitude: "+str(VmeasPPLoaded))
    #Bepaal interne impedantie van functiegenerator.
    print("Meetresultaten")
    print("Onbelaste bronspanning:"+str(VmeasPPOpen))
    print("Belaste bronspanning:"+str(VmeasPPLoaded))
    print("waarde interne bron:")
    RB=(VmeasPPOpen/VmeasPPLoaded-1)*Rload
    print(RB)
    