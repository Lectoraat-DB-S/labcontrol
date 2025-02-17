# Labcontrol
Labcontrol is educatieve software, gericht op het aansturen van meetappartuur via een (Windows) computer. Labcontrol's uiteindelijk doel is studenten te helpen hun meetopdrachten die tijdens diverse labpractica uitgevoerd moeten worden, correct uitvoeren. Ondersteuning van het practicum kan op verschillende manieren: het uitvoeren van de complete meting door een script, zodat student zijn/haar manueel verkregen meetwaarden of plots vergelijken kan met die van de computer. Labcontrol zou ook metingen tijdens het opbouwen van de schakeling kunnen uitvoeren, zoals het controleren van instellingen, waarbij de student wordt gewaarschuwd als er bepaalde limieten worden overschreden. Maar ook verkeerde of missende verbindingen zouden gecontroleerd kunnen worden, zoals een missende referentie aansluiting. Labcontrol draait op Python en leunt enorm op VISA, meer informatie vind je hier. Het waarom van labcontrol wordt hier nader beschreven (link geven).     
# Installeren op Windows.
Er is op het moment alleen een installatiehandleiding voor Windows. De installer maakt een map 'labcontrol' aan, waarin een Python runtime en een VISA driver installer wordt gekopieerd. WinPython  [[1]](#1) wordt binnen labcontrol gebruikt als de runtime. WinPython is een Windows geconfigureerde Python distro, compleet met een rijke verzameling aan grafische (plotting) mogelijke, wiskundige pakketten en de nodig algoritmes voor ML en databewerking. Een groot voordeel van WinPython is dat er geen wijziging aan de Windows Registry hoeven worden gedaan. Verwijderen van labcontrol is simpel: gewoon de directory verwijderen! 
## Installatiehandleiding labcontrol:
1. Je krijgt van de practicumbegeleiding een downloadlink naar het bestand labcontrol.exe.
2. Download het bestand labcontrol.exe naar jouw computer.
3. Verplaats labcontrol.exe naar de root van jouw HDD. Zeer waarschijnlijk is dat `c:\`.
4. Verwijder de blokkering, zie uitleg [hier](README.md#blokkering-opheffen). Windows blokkeert uitvoerbare code, als deze van buiten de computer komt.
5. Dubbelklik op labcontrol.exe. De installer maakt als eerste een subdirectory `labcontrol` aan. Daarin wordt alle benodigde software gezet en relevante snelkoppelingen aangemaakt. Deze directory wordt vanaf nu kortweg root genoemd. Let op: het uitpakken van de software door de installer kan een poosje duren!
6. Wacht tot installer klaar is met installeren. Open de zojuist aangemaakte `c:\labcontrol` map met de Windows Verkenner.
7. Start, via de snelkoppelingen in de `labcontrol` map, Jupyter Notebook op. Eerst verschijnt er een CMD shell. Hiermee wordt een Jupyter Notebook Server instantie opgestart. Daarna wordt, via een webpagina, het startscherm van Jupyter Notebook getoond. Met dit startscherm kun je Jupyter Notebook pagina's openen.  **Let op: notebooks niet openen via de Windows Verkenner!! Alleen openen via het Jupyter Notebook startscherm!!!**
8. Selecteer en open het bestand `getStarted.ipynb`. In een nieuw tabblad verschijnt een notebook waarmee het installeren van (a) een Windows device driver en (b) een Python binding wel heel eenvoudig wordt. Lees de instructies op deze notebook goed door. Na volledige, succesvolle uitvoering van deze notebook is jouw computer klaar voor 

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
