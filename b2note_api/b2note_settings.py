"""Setting for Eve framework and related services
"""
from b2note_schema import *
import os

b2note_eve_settings = {
    'MONGO_HOST': 'localhost',
    'MONGO_PORT': 27017,
    'MONGO_DBNAME': os.environ['MONGODB_NAME'],
    'MONGO_USERNAME': os.environ['MONGODB_USR'],
    'MONGO_PASSWORD': os.environ['MONGODB_PWD'],
    'DOMAIN': {
        'annotations': {'allow_unknown': True, 'schema': annotation_schema},
        'ontology':{'allow_unknown':True},
        'userprofile':{'allow_unknown':True},
    },
    'RESOURCE_METHODS': ['GET', 'POST', 'DELETE'],
    'ITEM_METHODS': ['GET', 'PATCH', 'PUT', 'DELETE'],
    'PUBLIC_METHODS': ['GET'],
    'PUBLIC_ITEM_METHODS': ['GET'],
    'XML': False,
    'PAGINATION_LIMIT':8192,
    'SECRET_KEY' : os.environ.get('B2NOTE_SECRET_KEY',default=False),
    'GOOGLE_CLIENT_ID': os.environ.get("GAUTH_CLIENT_ID", default=False),
    'GOOGLE_CLIENT_SECRET': os.environ.get("GAUTH_CLIENT_SECRET", default=False),
    'B2ACCESS_CLIENT_ID': os.environ.get("B2ACCESS_CLIENT_ID", default=False),
    'B2ACCESS_CLIENT_SECRET': os.environ.get("B2ACCESS_CLIENT_SECRET", default=False)
}

b2note_swagger_settings= {
    'title': 'B2NOTE Api',
    'version': '2.0',
    'description': 'B2NOTE API gives access to collection of digital annotation stored in form of W3C data annotation model',
    'termsOfService': 'terms of service',
    'contact': {
        'name': 'B2NOTE',
        'url': 'https://b2note.eudat.eu'
    },
    'license': {
        'name': 'MIT',
        'url': 'https://github.com/EUDAT-B2NOTE/b2note/blob/master/LICENSE.txt',
    },
    'schemes': ['http', 'https'],
}