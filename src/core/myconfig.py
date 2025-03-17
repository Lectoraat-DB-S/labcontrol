import core.Settings as setting
import pyvisa

def getRM():
    setting.setRmPath()
    global rm
    rm = pyvisa.ResourceManager(setting.visaPath)
    

    
    

    
