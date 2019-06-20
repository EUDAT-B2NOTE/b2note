# 04/06/2019 - new Eve schema - for validation of w3c web annotation data model - body
from eve import Eve
from bson import objectid
from eve_swagger import swagger, add_documentation
#from b2note_auth import B2NoteAuth
import b2note_auth

from b2note_settings import *
import os

# configures endpoint stored in annotation id's
prefix = '/annotations'
apiurl = 'http://localhost/api'

# if B2NOTE_API_URL is defined then it's used instead of default localhost
if os.environ.get('B2NOTE_API_URL') is not None:
    apiurl = os.environ.get('B2NOTE_API_URL')

# this is custom generation of _id field and duplicates
# the value into id field with url
def addAnnotationId(items):
    #print('Adding annotation, adding id')
    for item in items:
        item['_id']=objectid.ObjectId()
        item['id']=apiurl+prefix+'/'+str(item['_id'])
        #print(item)

#preparation for oauth - uncomment if enabled
#app = Eve(settings=b2note_eve_settings,auth=MyBasicAuth)


#app = Eve(auth=MyBasicAuth)
app = Eve(settings=b2note_eve_settings,auth=b2note_auth.B2NoteAuth)

# register swagger -openapi
app.config['SWAGGER_INFO'] = b2note_swagger_settings
app.register_blueprint(swagger)

#register secret key
app.secret_key=os.environ.get("GAUTH_B2NOTE_SECRET_KEY", default=False)

# register oauth providers and related services in app for b2note
b2note_auth.register(app)

# register EVE custom hook on instert
app.on_insert_annotations += addAnnotationId

if __name__== "__main__":
  print('Instantiating standalone server.')
  app.run()
