import windowsapps

installed_applications = windowsapps.get_apps() 
for app in installed_applications:
    print(app)
#Gives Dictionary of Application names along with their AppID