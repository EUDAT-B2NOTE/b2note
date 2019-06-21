# B2NOTE Api

This project is configuration of Eve framework with W3C Data Annotation model
implemented by B2NOTE service. 

# prepare development environment

You may need to install required packages
into python virtual env. 
```bash
yum -y install python36
python3 -m virtualenv py3
source py3/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

# run development environment

Run `b2note_api.sh` (or `python b2note_api.py`) then open `http://localhost:5000`

This will start Eve providing REST Api to interact with b2note schema in mongodb database.

# run unittests

Run `b2note_apitest.sh` (or `python -m unittest`)

This will first detect whether API is running on port 5000. If not,
the development server is started. Tests are executed.


