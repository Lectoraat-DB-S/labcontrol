# Labcontrol 
Labcontrol aims at controlling typical lab devices such as functiongenerators, power supplies and oscilloscopes by means of the VISA standard and python.
VISA is the standard for configuring, programming, and troubleshooting instrumentation systems. It's owned and maintained by National Instrument. 
See: [VISA Product Page](https://www.ni.com/nl-nl/shop/product/ni-visa.html)  

## Background

## Installation on Windows
1. Install git-scm (for commandline cloning of git based repos).
2. Create a folder (no spaces in name) for cloning this repo.
3. Navigate to newly created folder and clone the repo by executing: git clone (https://github.com/Lectoraat-DB-S/labcontrol.git)
4. Download and install VISA driver software from National Instruments.
5. Download latest stable version of Python. (In this case version 3.12.4)
6. Install Python. Tap de checkbox for 'add to Path', installation of 'py' with administrive rights.
7. Download and install Visual Studio Code.
8. Start Visual Studio Code
9. Install the 'Microsoft Python" extension for Visual Studio Code. See: https://marketplace.visualstudio.com/items?itemName=ms-python.python for instructions.
10. Install the 'Python Auto Venv' extension for Visual Studio Code. Add the folder of your virtual environment in the VSC settings.
11. In VSC: open the 'labcontrol-python' folder of this labcontrol repository
12. Press Ctrl + Shift + P and type 'Python: create environment'
13. Select the latest python 'venv' environment.
14. Select 'requirements.txt' to install required dependencies.
15. After the creation of the virtual environment, labcontrol is ready to use!
## Usage
Many ways to Rome exists, therefore this readme gives only two options: command line and Visual Studio Code
### Command line
1. Navigate to the directory you've installed the environment in.
2. Activate the environment: .\Scripts\activate.bat
3. Navigate to the labcontrol python script folder. Assuming same clone folder as before, just navigate to C:\github\labcontrol\src\labcontrol-python

### Visual Studio Code
1. Assumption: a valid Python interpreter has been installed.
2. Install the 'Microsoft Python" extension . See: https://marketplace.visualstudio.com/items?itemName=ms-python.python
3. Install the 'Python Auto Venv' extension. Add the folder of your virtual environment in the VSC settings.
4. Open the C:\github\labcontrol\src\labcontrol-python folder in Visual Studio Code.
5. Select the proper virtual environment through pressing the Pyhton-icon on the left in de VSCode main screen.  

Documentation

