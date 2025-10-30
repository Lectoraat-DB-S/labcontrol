Deze pagina beschrijft de installatie van Labcontrol op een Windows 11 computer. Er zijn twee opties om Labcontrol te 
installeren± 1. Handmatig en 2. via een installer geschreven in Powershell script.

Installatiehandleiding labcontrol
=================================

1. Je krijgt van de practicumbegeleiding een downloadlink naar het bestand labcontrol.exe.

2. Download het bestand labcontrol.exe naar jouw computer.

3. Verplaats labcontrol.exe naar de root van jouw SSD. Zeer waarschijnlijk is dat `c:\`.

4. Dubbelklik op labcontrol.exe. De installer maakt als eerste een subdirectory `labcontrol` aan. Daarin wordt alle benodigde software gezet en relevante snelkoppelingen aangemaakt. Deze directory wordt vanaf nu kortweg root genoemd. Let op: het uitpakken van de software door de installer kan een poosje duren! Hoe je een eventuele blokkering van Windows kan oplossing lees je hier.

5. Wacht tot installer klaar is met installeren. Open de zojuist aangemaakte `c:\labcontrol` map met de Windows Verkenner.

6. Start, via de snelkoppelingen in de `labcontrol` map, Jupyter Notebook op. Eerst verschijnt er een CMD shell. Hiermee wordt een Jupyter Notebook Server instantie opgestart. Daarna wordt, via een webpagina, het startscherm van Jupyter Notebook getoond. Met dit startscherm kun je Jupyter Notebook pagina's openen.  **Let op: notebooks niet openen via de Windows Verkenner!! Alleen openen via het Jupyter Notebook startscherm!!!**

7. Selecteer en open het bestand `getStarted.ipynb`. In een nieuw tabblad verschijnt een notebook waarmee het installeren van (a) een Windows device driver en (b) een Python binding wel heel eenvoudig wordt. Lees de instructies op deze notebook goed door.

8. Labcontrol leunt voor de werking zwaar op National Instrument's VISA driver. Installeer deze driver als je dat nog niet gedaan hebt, door het uitvoeren van het codeblok

9. Het laatste codeblok bevat de instructie om de Python binding te installeren. Voer dit codeblok pas uit, als de installatie van VISA volledig afgerond is.
