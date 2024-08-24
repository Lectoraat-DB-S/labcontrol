import subprocess
import urllib.request
import os

def install_software(package):
	"""
	Function to install a software package.
	"""
	try:
		if package == 'NI-VISA':
			url = 'https://www.ni.com/en/support/downloads/drivers/download/packaged.ni-visa.521671.html'
			installer_path = 'NI-VISA.exe'
			urllib.request.urlretrieve(url, installer_path)
			subprocess.check_call([installer_path, '-ms'])
			os.remove(installer_path)
		else:
			subprocess.check_call(['pip', 'install', package])
		print("Successfully installed {package}")
	except subprocess.CalledProcessError:
		print("Failed to install {package}")


software_packages = ['numpy', 'pandas', 'matplotlib', 'NI-VISA']

for package in software_packages:
	install_software(package)
