# Install on Windows.
Er is op het moment alleen een installatiehandleiding met bijbehorende installer voor Windows. De installer is gebasseerd op WinPython  [[1]](#1) ,een speciaal voor Windows geconfigureerde Python distro, compleet met een rijke verzameling aan grafische (plotting) mogelijke, wiskundige pakketten en de nodig algoritmes voor ML en databewerking. 
## Installatiehandleiding labcontrol:
1. Je krijgt van de practicumbegeleiding een downloadlink naar het bestand labcontrol.exe.
2. Download het bestand labcontrol.exe naar jouw computer.
3. Verplaats labcontrol.exe naar de root van jouw HDD. Zeer waarschijnlijk is dat `c:\`.
4. Dubbelklik op labcontrol.exe. De installer maakt als eerste een subdirectory `labcontrol` aan. Daarin wordt alle benodigde software gezet en relevante snelkoppelingen aangemaakt. Deze directory wordt vanaf nu kortweg root genoemd. Let op: het uitpakken van de software door de installer kan een poosje duren! Hoe je een eventuele blokkering van Windows kan oplossing lees je hier.
4. Wacht tot installer klaar is met installeren. Open de zojuist aangemaakte `c:\labcontrol` map met de Windows Verkenner.
5. Start, via de snelkoppelingen in de `labcontrol` map, Jupyter Notebook op. Eerst verschijnt er een CMD shell. Hiermee wordt een Jupyter Notebook Server instantie opgestart. Daarna wordt, via een webpagina, het startscherm van Jupyter Notebook getoond. Met dit startscherm kun je Jupyter Notebook pagina's openen.  **Let op: notebooks niet openen via de Windows Verkenner!! Alleen openen via het Jupyter Notebook startscherm!!!**
6. Selecteer en open het bestand `getStarted.ipynb`. In een nieuw tabblad verschijnt een notebook waarmee het installeren van (a) een Windows device driver en (b) een Python binding wel heel eenvoudig wordt. Lees de instructies op deze notebook goed door.

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
