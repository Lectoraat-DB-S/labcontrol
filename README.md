# Labcontrol - Bestuur al je elektronische meetapparatuur met jouw laptop
Labcontrol maakt het mogelijk om met Python een complete meetopstelling (een Lab) te besturen (control) . Labcontrol is een verzameling van diverse Python bibliotheken (of packages), aangevuld met Python scripts die de al die pakketten wegwerkt achter een standaard interface die het programmeren veel makkerlijker maakt.    
# Installatie op Windows.
Hoewel Labcontrol voor elk OS geschikt is, is er is op het moment alleen een beschrijving voor installatie op Windows. Zie hiervoor de  [installatiehandleiding](docs/installatie.rst).


## Achtergrond info
De basis is WinPython, die ik heb uitgebreid door er een VISA installer en de relevante labcontrol python scripts eraan toe te voegen. Het mooie van WinPython: het is een zelfstandige, losdraaiende Python distro voor Windows. Registreren binnen Windows hoeft niet: pleur de WinPython directory ergens op je computer en runnen maar. Ben je er klaar mee, verwijder je de directory en je bent ervan af, zonder dat je blijft zitten met een nog zwaarder vervuilde WinReg. WinPython heeft naast plotting zo’n beetje alle leuke wiskundige en data-analytische pakketten aan boord met daarbij ook Jupyter. 

## Blokkering opheffen
Als je zoiets als onderstaand scherm te zien krijgt, betekent dat Windows de executable die je wilt laten uitvoeren niet vertrouwt:

<img src="https://github.com/user-attachments/assets/19957f11-656b-4084-bcf4-0575152f7a50" width="248">

Omdat jij de installer van een externe locatie naar jouw laptop download, is de kans is groot dat Windows weigert die installer uit te voeren. Dit komt omdat Windows per definitie code die van buiten de computer komt, wantrouwt. Het gevolg: de uitvoering wordt geblokkeerd. Gelukkig kun je die blokkering eenvoudig opheffen:
* rechtsklikken op het bestand waarvan je de blokkering wilt verwijderen (Tip: houd shift ingedrukt tijdens het klikken)
* kies voor 'Eigenschappen'. Als die niet in de lijst staat, kies je voor meer opties.
* Zet een vinkje in vierkantje bij 'Blokkering opheffen'.

Hieronder zie je voorbeeld op een met de browser gedownloade executable:
1. Shift + rechtermuisklik op het bestand waarvan de blokkering verwijderd moet worden. Kies voor de optie 'Eigenschappen'

<img src="https://github.com/user-attachments/assets/8e4e99bd-3e30-4967-9ff7-900b86454e42" width="300">

2. Een popup verschijnt waarin diverse eigenschappen van het bestand worden weergegeven. Onder in het venster kun is te zien dat het vinkje mist: Windows vertrouwt dit bestand niet, omdat het van buiten de computer komt. Uitvoering wordt geblokt.

<img src="https://github.com/user-attachments/assets/32f251ba-c506-4b17-8764-335477d18e31" width="300">

3. Hef de blokkering op, door het vinkje te zetten middels klikken op het vierkantje. Klik op toepassen en dan op OK.
 
<img src="https://github.com/user-attachments/assets/721ef910-efdb-4a23-a032-3ea386005aa8" width="300">


## References
<a id="1">[1]</a> 
https://winpython.github.io/
