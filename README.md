# Labcontrol 
Labcontrolling is controlling typical lab devices like functiongenerators, power supplies and oscilloscopes by means of the VISA standard and python.
VISA is the standard for configuring, programming, and troubleshooting instrumentation systems. It's owned and maintained by National Instrument. 
See: [VISA Product Page](https://www.ni.com/nl-nl/shop/product/ni-visa.html)  

## Background

## Installation on Windows
Assuming a computer without any Python interpreter (pre)installed, one must follow next steps:
1. Download Python. (In this case version 3.12.4)
2. Install Python. Tap de checkbox for 'add to Path', installation of 'py' with administrive rights.
3. Create a virtual environment: for example py -m venv c:\temp\testenv
4. Navigate to the directory you've installed the environment in.
5. Activate the environment: .\Scripts\activate.bat
6. Install pip: py -m pip install --upgrade pip
7. Clone the repo to your computers drive. Assumption is the repo has been cloned to C:\github\labcontrol
8. Install all packages via pip: py -m pip install -r C:\github\labcontrol\src\install-script\pip_requirements.txt
   

Usage

Documentation

