Mobike - Server (API)
=====================

# What?
The api for the mobike solution, which communicates with the app.

# Installation
The program uses python 3.4, all the dependencies are visible in requirements.txt and you can install them using pip as follows: pip -r requirements.txt

# config files
* You need to manually create a settings.py file (in the root dir) that looks somewhat like this (assuming you use mysql)
```
from pytz import timezone

DATABASE = {
	'drivername' : 'mysql+oursql',
	'host' : 'localhost',
	'port' : '3306',
	'username' : 'username',
	'password' : 'password',
	'database' : 'mobike',
}

TIMEZONE = timezone('Europe/Brussels')
```

Furthermore, you must manually create the 'mobike' database using phpmyadmin or the command line interface of mysql


# Run
In order to run, you need the following command
python api.py;
Keep in mind that if your distro uses python 2.7 by default, you need to take manual actions:
* either use python3 if its available, see [here](http://askubuntu.com/questions/350751/install-and-run-python-3-at-the-same-time-than-python-2)
* or use a virtualenv, as descibed [here](http://askubuntu.com/questions/279959/how-to-create-a-virtualenv-with-python3-3-in-ubuntu)

# Tests
run py.test in the rootdirectory, it should work