from eve import Eve
from flask import request
from settings import mongo_settings
import json, requests

app = Eve(settings=mongo_settings)


@app.route('/create_annotation', methods=['POST'])
def post_to_django():
    pid = request.values.get('pid_tofeed')
    subject = request.values.get('subject_tofeed')
    url='https://b2note.bsc.es/interface_main'
    data = {"pid_tofeed": str(pid), "subject_tofeed": str(subject) }
    headers = {'Content-Type':'application/json'}
    r = requests.post(url, data=data)
    return str(r.text)

if __name__ == '__main__':
    app.run()
