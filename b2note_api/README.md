# B2NOTE Api

This project is configuration of Eve framework with W3C Data Annotation model
implemented by B2NOTE service. 

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

Run `python b2note_api.py` then open `http://localhost:5000`

This will start Eve providing REST Api to interact with b2note schema in mongodb database.



