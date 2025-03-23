# Labcontrol
Labcontrol is educatieve software, gericht op het aansturen van meetappartuur via een (Windows) computer. Labcontrol's uiteindelijk doel is studenten te helpen hun meetopdrachten correct uit te voeren. Ondersteuning van een practicum door Labcontrol zou op verschillende manieren kunnen: 
* het uitvoeren van de complete meting door een script, zodat student zijn/haar manueel verkregen meetwaarden of plots vergelijken kan met die van de computer.
* Labcontrol zou kunnen controleren op instellingen die de student tijdens het opbouwen van een schakeling moet (of had moeten) maken, zoals het instellen van de juiste stroombegrenzing voor een specifiek labopdracht. Hiermee zou Labcontrol het breadboard en de componenten van de student kunnen beschermen, door de voeding onmiddelijk weer uit te schakelen, als student een meting probeert uitvoeren met de verkeerde instellingen voor het desbetreffende practicum.
* Labcontrol zou ook verkeerde of missende verbindingen kunnen controler, zoals een missende referentie aansluiting, door het (FFT) spectrum te controleren op een (zeer) dominante 50 Hz component. De computer zou de student dan een advies kunnen geven. Waarschijnlijk is dat voor een aantal studenten prettiger dan gecorrigeerd worden door een docent.
Naast ondersteuning van de student, zou labcontrol ook ingezet kunnen worden als meetplatform voor partijen in de 
Labcontrol draait op Python en leunt enorm op VISA, meer informatie vind je [hier](https://github.com/Lectoraat-DB-S/labcontrol/wiki/Labcontrol:-wat-haal-ik-in-huis%3F). Waarom labcontrol wordt ontwikkeld lees je [hier](https://github.com/Lectoraat-DB-S/labcontrol/wiki/Waarom-Labcontrol).

Naast ondersteuning van studenten in een lab, zou labcontrol ook gebruikt kunnen worden als basis voor sensordata-acquisitie systeem.

# Installeren op Windows.
Er is op het moment alleen een installatiehandleiding voor Windows. De handleiding staat in de [wiki](https://github.com/Lectoraat-DB-S/labcontrol/wiki/Labcontroll-installatiehandleiding) van deze repo.
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

# Bijdragen aan labcontrol
Pushen naar main branch is uitgezet. Ontwikkelaars die willen bijdragen moeten niet de master branch, maar de development branch gebruiken. Geadviseerd wordt om eerst een branch van de development te trekken en daarop de aanpassing aan de code te maken en als dat gedaan is, inclusief test, de branch naar origin te pushen en eventueel te mergen met de development branch. 
## Aanbevolen workflow:
Advies is om git-scm te gebruiken (https://git-scm.com/downloads). De stappen om (lokaal) een branch vanuit development te maken zijn:

1. `git checkout develop`
  
2. `git checkout -b feature_branch`

3. Maak de aanpassing
<...Dit kan even duren .....dagen of zo>   
4. Test de aanpassing

5. `git add .`

7. `git commit -m "Geef hier een mooie omschrijving van wat je gedaan hebt, graag met ref naar de issue." `

8. `git push -u`

Wanneer je alleen werkt aan een feature, hoef je tussen punt 3. en 4. niet te pullen. Werk je niet alleen, pull dan altijd eerst voordat je weer verder gaat.

## References
<a id="1">[1]</a> 
https://winpython.github.io/
