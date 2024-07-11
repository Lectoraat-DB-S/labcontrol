# Labcontrol 
Labcontrol aims at controlling typical lab devices such as functiongenerators, power supplies and oscilloscopes by means of the VISA standard and python.
VISA is the standard for configuring, programming, and troubleshooting instrumentation systems. It's owned and maintained by National Instrument. 
See: [VISA Product Page](https://www.ni.com/nl-nl/shop/product/ni-visa.html)  

## Background

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

