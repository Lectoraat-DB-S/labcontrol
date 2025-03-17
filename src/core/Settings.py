import pyvisa
SIM = True

def gebruik_simulatie():
    with pyvisa.ResourceManager("@sim") as rm:
        # Open de virtuele resource
        instrument = rm.open_resource("USB::0x1111::0x2222::0x2468::INSTR")
        
        # Doe je simulatie taken
        print(instrument.query('*IDN?'))  # Bijvoorbeeld een query

    # De ResourceManager wordt nu automatisch gesloten na het verlaten van de 'with'-context.
    
# # Roep de functie aan in dit bestand
# gebruik_simulatie()

# In dit voorbeeld zorgt de with-statement ervoor dat de ResourceManager wordt gesloten zodra je klaar bent met het gebruik ervan, waardoor je problemen met niet-gesloten resources voorkomt.
# 2. Deel dezelfde ResourceManager tussen meerdere bestanden

        
        
# de sim mode van pyvisa is irritant. Chat maar eens om suggestie gevraagd        
        
# Om het probleem te fixen waarbij je een ResourceManager object opnieuw probeert te gebruiken in een ander Python-bestand en tegen een timeout aanloopt, kunnen we de volgende stappen ondernemen:
# 1. Zorg ervoor dat je de resource correct afsluit in het eerste bestand

# Wanneer je de simulatie (@sim) gebruikt, moet je er zeker van zijn dat de resource manager en de gebruikte apparaten goed worden afgesloten voordat je het bestand afsluit. Als de resource niet goed wordt afgesloten, kan dit leiden tot een lock of een probleem bij het opnieuw openen van de resource in een ander bestand.

# Gebruik de with-statement om ervoor te zorgen dat de resource automatisch wordt gesloten, zoals hieronder:
# Voorbeeld van bestand 1 (waar de resource wordt geopend en gebruikt):

# import pyvisa

# def gebruik_simulatie():
#     with pyvisa.ResourceManager('@sim') as rm:
#         # Open de virtuele resource
#         instrument = rm.open_resource('SIM')
        
#         # Doe je simulatie taken
#         print(instrument.query('*IDN?'))  # Bijvoorbeeld een query

#     # De ResourceManager wordt nu automatisch gesloten na het verlaten van de 'with'-context.
    
# # Roep de functie aan in dit bestand
# gebruik_simulatie()

# In dit voorbeeld zorgt de with-statement ervoor dat de ResourceManager wordt gesloten zodra je klaar bent met het gebruik ervan, waardoor je problemen met niet-gesloten resources voorkomt.
# 2. Deel dezelfde ResourceManager tussen meerdere bestanden

# In plaats van telkens een nieuwe ResourceManager aan te maken, kun je de ResourceManager in een centraal bestand maken en deze vervolgens importeren in andere bestanden. Dit voorkomt dat je meerdere ResourceManager-instanties probeert te openen, wat mogelijk leidt tot conflicts of timeouts.
# Stap 1: Maak een centraal bestand voor de ResourceManager

# Laten we een bestand resource_manager.py maken waarin je de ResourceManager maakt:

# # resource_manager.py
# import pyvisa

# # Maak de resource manager aan
# rm = pyvisa.ResourceManager('@sim')

# def get_instrument():
#     return rm.open_resource('SIM')

# Stap 2: Gebruik de gedeelde ResourceManager in andere bestanden

# In je andere Python-bestanden kun je nu de gedeelde ResourceManager gebruiken:

# # bestand_2.py
# from resource_manager import get_instrument

# # Verkrijg het instrument
# instrument = get_instrument()

# # Doe iets met het instrument
# print(instrument.query('*IDN?'))

# Door get_instrument() te gebruiken, hergebruik je de ResourceManager en open je dezelfde virtuele resource zonder opnieuw een nieuwe instantie van de ResourceManager te maken.
# 3. Herstel je ResourceManager-instantie wanneer je een timeout hebt

# Als je merkt dat de ResourceManager een timeout vertoont, kun je proberen de verbinding opnieuw tot stand te brengen of de resource opnieuw in te stellen. Dit kan handig zijn als er een tijdelijke blokkering of probleem is met de verbinding.

# Je kunt bijvoorbeeld een retry-mechanisme toevoegen:

# import pyvisa
# import time

# def open_instrument():
#     rm = pyvisa.ResourceManager('@sim')
#     instrument = None
#     retries = 3
#     for _ in range(retries):
#         try:
#             instrument = rm.open_resource('SIM')
#             break
#         except pyvisa.errors.VisaIOError:
#             print("Timeout, probeer opnieuw...")
#             time.sleep(1)
    
#     if instrument is None:
#         raise Exception("Kan het instrument niet openen na meerdere pogingen")
    
#     return instrument

# # Gebruik de functie
# instrument = open_instrument()
# print(instrument.query('*IDN?'))

# Hiermee probeer je een aantal keren de verbinding tot stand te brengen als er een timeout optreedt.
# Samenvatting:

#     Gebruik de with-statement om de resource automatisch af te sluiten in het eerste bestand.
#     Deel dezelfde ResourceManager tussen meerdere bestanden om conflict te voorkomen.
#     Retry-logica toevoegen voor het geval er een timeout of verbindingsprobleem optreedt.

# Door deze methoden te implementeren, zou je het probleem van timeouts moeten kunnen oplossen en tegelijkertijd de herbruikbaarheid van de resource manager over meerdere bestanden mogelijk maken.

