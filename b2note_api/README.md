# B2NOTE Api

This component is based on Eve - Python REST Api framework based on Flask [1].
Specific schema definition is provided for data annotations according to W3C data model.

# prepare development environment

You may need to install required packages
into python virtual env. 
```bash
yum -y install python36
python3 -m venv py3
source py3/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

# run development environment

You may need to activate `py3` virtual env in advance by `source py3/bin/activate`
Run `python b2note_api.py` then open `http://localhost:5000`

This will start Eve providing REST Api to interact with b2note schema in mongodb database.

# run unittests

You may need to activate `py3` virtual env in advance by `source py3/bin/activate`
Run or `python -m unittest`

This will first detect whether API is running on port 5000. If not,
the development server is started. Tests are executed.

# Oauth integration

Python authlib [3] and loginpass [4] are used for Oauth2 integration. 
Specific integration for B2Access has been implemented at loginpass_b2access.py. These settings are taken from environment variables

```
B2ACCESS_API_URL="https://unity.eudat-aai.fz-juelich.de/"
# for production use B2ACCESS_API_URL="https://b2access.eudat.eu:443/oauth2-as/oauth2-authz"
B2ACCESS_CLIENT_ID="your registered ID at url above"
B2ACCESS_CLIENT_SECRET="your registered SECRET at url above"
B2ACCESS_REDIRECT_URI=endpoint to redirect back to b2note instance e.g.:http://localhost/b2note
```
endpoint handler for `/b2access/*` are defined at `b2note_auth.py`
Optional authentication from Google account is available.

# MongoDB integration

MongoDB [5] is expected to run locally as mongod. 
The values to connect to mongodb are taken from these environment variables, with sample values:
```
MONGODB_NAME='b2notedb'
MONGODB_USR='b2note'
MONGODB_PWD='b2note'
```

# Integration to WSGI
`api.wsgi` contains wsgi script to run this API component in apache2 or nginx web server.
To configure apache, you need a mod_wsgi module installed 
and configured to refer to python virtual environment using `python-home` [6]. 
Sample configuration:
``` 
LoadModule wsgi_module "/home/vagrant/py3/lib64/python3.6/site-packages/mod_wsgi/server/mod_wsgi-py36.cpython-36m-x86_64-linux-gnu.so"
WSGIPythonHome "/home/vagrant/py3"
WSGIDaemonProcess b2note_api user=vagrant group=vagrant processes=1 threads=5 python-home=/home/vagrant/py3 python-path=/home/vagrant/b2note/b2note_api
WSGIPassAuthorization On
WSGIScriptAlias /api /home/vagrant/b2note/b2note_api/api.wsgi

    <Directory /home/vagrant/b2note/b2note_api>
        Require all granted
        WSGIProcessGroup b2note_api
        WSGIApplicationGroup %{GLOBAL}
        Order allow,deny
	Allow from all
    </Directory> 
```
Consult bootstrap scripts for further details from [2]

# References
- [1] Eve - Python REST Api framework: https://docs.python-eve.org/en/stable/
- [2] B2NOTE Virtual Machine: https://github.com/e-sdf/B2NOTE-VirtualMachine
- [3] Authlib: https://authlib.org/ 
- [4] Loginpass: https://github.com/authlib/loginpass
- [5] MongoDB: https://www.mongodb.com/
- [6] mod_wsgi Virtual Environments: https://modwsgi.readthedocs.io/en/develop/user-guides/virtual-environments.html?highlight=virtualenv