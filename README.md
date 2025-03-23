# Labcontrol
Labcontrol is educatieve software, gericht op het aansturen van meetappartuur via een (Windows) computer. Labcontrol's uiteindelijk doel is studenten te helpen hun meetopdrachten correct uit te voeren. Ondersteuning van een practicum door Labcontrol zou op verschillende manieren kunnen: 
* het uitvoeren van de complete meting door een script, zodat student zijn/haar manueel verkregen meetwaarden of plots vergelijken kan met die van de computer.
* Labcontrol zou kunnen controleren op instellingen die de student tijdens het opbouwen van een schakeling moet (of had moeten) maken, zoals het instellen van de juiste stroombegrenzing voor een specifiek labopdracht. Hiermee zou Labcontrol het breadboard en de componenten van de student kunnen beschermen, door de voeding onmiddelijk weer uit te schakelen, als student een meting probeert uitvoeren met de verkeerde instellingen voor het desbetreffende practicum.
* Labcontrol zou ook verkeerde of missende verbindingen kunnen controler, zoals een missende referentie aansluiting, door het (FFT) spectrum te controleren op een (zeer) dominante 50 Hz component. De computer zou de student dan een advies kunnen geven. Waarschijnlijk is dat voor een aantal studenten prettiger dan gecorrigeerd worden door een docent.
Naast ondersteuning van de student, zou labcontrol ook ingezet kunnen worden als meetplatform voor partijen in de 
Labcontrol draait op Python en leunt enorm op VISA, meer informatie vind je [hier](https://github.com/Lectoraat-DB-S/labcontrol/wiki/Labcontrol:-wat-haal-ik-in-huis%3F). Waarom labcontrol wordt ontwikkeld lees je [hier](https://github.com/Lectoraat-DB-S/labcontrol/wiki/Waarom-Labcontrol).

Naast ondersteuning van studenten in een lab, zou labcontrol ook gebruikt kunnen worden als basis voor sensordata-acquisitie systeem.

# Installeren op Windows.
Voor diegene die labcontrol alleen willen gebruiken, is er een installatiehandleiding voor Windows beschikbaar.  Deze handleiding staat in de [wiki](https://github.com/Lectoraat-DB-S/labcontrol/wiki/Labcontroll-installatiehandleiding) van deze repo.

# Bijdragen aan labcontrol
Pushen naar main branch is uitgezet. Ontwikkelaars die willen bijdragen moeten niet de master branch, maar de development branch gebruiken. Geadviseerd wordt om eerst een branch van de development te trekken en daarop de aanpassing aan de code te maken en als dat gedaan is, inclusief test, de branch naar origin te pushen en eventueel te mergen met de development branch. 
## Aanmaken van een virtual environment in Python
Zeer waarschijnlijk zal de code geschreven worden in een IDE als Visual Studio Code, Pycharm of iets anders. Er zijn veel manieren om een git project binnen een IDE te clone en een passende Python Interpreter te configuren. In deze sessie wordt een aanpak 

## Aanbevolen git workflow:
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
