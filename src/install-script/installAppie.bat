def install_software(package):
	try:
		if package == 'firefox':
			# Download Firefox installer
			url = 'https://download.mozilla.org/?product=firefox-latest&os=win64&lang=en-US'
			installer_path = 'firefox_installer.exe'
			urllib.request.urlretrieve(url, installer_path)
			# Install Firefox silently
			subprocess.check_call([installer_path, '-ms'])
			# Delete the installer file
			os.remove(installer_path)
		else:
			subprocess.check_call(['pip', 'install', package])
		print(f"Successfully installed {package}")
	except subprocess.CalledProcessError:
		print(f"Failed to install {package}")
