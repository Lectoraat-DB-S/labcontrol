# Labcontrol 
Labcontrol is software for controlling typical lab devices such as functiongenerators, power supplies and oscilloscopes. Labcontrol uses VISA to access the instruments and will be written in Python. See: [VISA Product Page](https://www.ni.com/nl-nl/shop/product/ni-visa.html)  

## Why Labcontrol
Labcontrol is a system in development for circumventing some of today’s ‘educational trends ’ such as insufficient reading skills and having difficulties to memorize some important rules of thumbs. These problems prevent students from doing their labs the right way, yielding to incorrect measurements and there confusing results, preventing them to learn effectively. Labcontrol: a combination of “electronic laboratory” and “digital control”. It aims to  control test and measurement device to be found at a lab bench  of an educational institute and trying help the student during its lab, by forcing correct order of each step of the measurement, by assessing the results of each step and to check the final results and conclusions drawn by the student.
VISA is the standard for configuring, programming, and troubleshooting instrumentation systems. It's owned and maintained by National Instrument. 

## Background
The desire to control equipment remotely goes back to the very early days of computing. Hewlett Packard (HP), not only creator of early computing systems, also designed and produced very nice measurement equipment those days, which HP wanted to interconnect by a standard bus system. By the late 1960s, HP had gained and enormous experience in connecting equipment via bus systems. This resulted in het design of the so called ‘Hewlett-Packard Interface Bus or HP-IB’ during the early 1970s, which led to the IEEE48.1 standard in 1975, for defining he hardware and the IEEE48.2 in 1987, for the protocol and messages specification. In 1990 the successor of IEEE48.2 was founded: the Standard Commands for Programmable Instruments (SCPI), which defined not only classes of controllable instruments but also gave a standard syntax and commands for all programmable test and measurement devices. Although originally created for the IEEE-488.1 (GPIB) bus, SCPI nowadays works seamlessly with all kinds of communication protocols such as RS-232, RS-422, Ethernet and USB. [[1]](#1).

## Windows Install.
Using Labcontrol relies on third party software, some required other optional.
### Required Software
Labcontrol requires:
- VISA driver software from National Instruments.
- A recent Python interpreter.
- Visual Studio Code with
  - 'Microsoft Python' extension for Visual Studio Code
- A clone of this repo.
### Optional software
Optional, but recommended software:
-  git-scm, if you like command line managing of git based repos.
-  'Python Auto Venv' extension for Visual Studio Code

### Install proces
1. Install git-scm 
2. Create a folder (no spaces in name) for cloning this repo into.
3. Navigate to newly created folder and clone the repo by executing: git clone https://github.com/Lectoraat-DB-S/labcontrol.git
4. Download and install VISA driver software from National Instruments.
5. Download latest stable version of Python. 
6. Install Python. Tap de checkbox for 'add to Path' and installation of 'py' with administrive rights.
7. Download and install Visual Studio Code.
8. Start Visual Studio Code
9. Install the 'Microsoft Python' extension for Visual Studio Code. See: https://marketplace.visualstudio.com/items?itemName=ms-python.python for instructions.
10. Install the 'Python Auto Venv' extension for Visual Studio Code. Add the folder of your virtual environment in the VSC settings.
11. In VSC: open the 'labcontrol-python' folder of this labcontrol repository
12. Press Ctrl + Shift + P and type 'Python: create environment'
13. Select the latest python 'venv' environment.
14. Select 'requirements.txt' to install required dependencies.
15. After VCS finished creation of the virtual environment, labcontrol is ready to use!
## Usage
1. Open the C:\github\labcontrol\src\labcontrol-python folder in Visual Studio Code.
2. Select the proper virtual environment through pressing the Pyhton-icon on the left in de VSCode main screen.
3. Open one of the measurement python files in the labcontrol-python folder.  

#Documentation

## References
<a id="1">[1]</a> 
https://www.hp9845.net/9845/tutorials/hpib/
