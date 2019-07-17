"""B2Note Api - main application to set and execute the server with REST Api for B2Note

Provides REST Api via Python Eve framework
Adds Swagger extension to be compliant with OpenApi
Integrates Oauth2 and selected providers (google,b2access) which might be used by client (b2note_app webcomponent)

# 04/06/2019 - new Eve schema - for validation of w3c web annotation data model - body
# 20/06/2019 - oauth2 integration with authlib and loginpass - new b2access and reuse of google account service
"""
from eve import Eve
from bson import objectid
from eve_swagger import swagger, add_documentation
import b2note_auth
import b2note_settings
import os

# configures endpoint stored in annotation id's
prefix = '/annotations'
# apiurl in order to make proper id with reference to annotation
apiurl = os.environ.get('B2NOTE_API_URL',default='http://localhost/api')

def addAnnotationId(items):
    """this is custom generation of _id field for an annotation

    generates _id as ObjectId() - which is default for mongodb
    duplicates this value into id field with apiurl as prefix,
    thus id is a direct URI to the annotation
    """

    for item in items:
        item['_id']=objectid.ObjectId()
        item['id']=apiurl+prefix+'/'+str(item['_id'])

def addUserprofileRemoveToken(items):
    """this is custom manipulation of userprofile insertion
    """
    for item in items:
        item.pop('token',None)
def replaceUserprofileRemoveToken(item,orig):
    item.pop('token', None)
        #items['token'] = ''
        #print(items)
        #delattr(items,'token')


# define basic app - Eve is instance of Flask,
app = Eve(settings=b2note_settings.b2note_eve_settings,auth=b2note_auth.B2NoteAuth)
# register swagger extension - openapi
app.config['SWAGGER_INFO'] = b2note_settings.b2note_swagger_settings
app.register_blueprint(swagger)

#register secret key for this app
app.secret_key=os.environ.get("B2NOTE_SECRET_KEY", default=False)

# delegate registration of oauth providers and related services in app instance
b2note_auth.register(app)

# register EVE custom hook on instert - will add id field, remove token as defined above
app.on_insert_annotations += addAnnotationId
app.on_insert_userprofile += addUserprofileRemoveToken
app.on_replace_userprofile += replaceUserprofileRemoveToken
app.on_update_userprofile += replaceUserprofileRemoveToken


# if this python script is executed directly - the run the app as standalone server on localhost, usually on port 5000
if __name__== "__main__":
  print('Instantiating standalone server.')
  app.run()
