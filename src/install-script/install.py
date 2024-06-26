import windowsapps

def checkInstalledBase():
    NI_VISA_available = 0
    VSC_available = 0
    Python_available = 0
    installed_applications = windowsapps.get_apps() 
    for app in installed_applications:
        if app == "NI-VISA Driver Wizard":
            print("NI-VISA installed")
            NI_VISA_available = 1
        if app == "Visual Studio Code":
            print("Visual Studio Code")
            VSC_available = 1
        if app == "Python 3.11 (64-bit)":
            Python_available = 1
            print("found a valid Python install")
    return (NI_VISA_available, VSC_available, Python_available)

(a,b,c)=checkInstalledBase()
