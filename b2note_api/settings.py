import os

mongo_settings = {
        'MONGO_HOST': 'localhost',
        'MONGO_PORT': 27017,
        'MONGO_DBNAME': os.environ['MONGODB_NAME'],
        'MONGO_USERNAME': os.environ['MONGODB_USR'],
        'MONGO_PASSWORD': os.environ['MONGODB_PWD'],
        'DOMAIN': {
            'annotations': {
                'datasource' : {
                    'source': 'b2note_app_annotation'
                    },
                #'url' : 'annotations/<regex("[a-f0-9]{24}"):annotation_id>/files',
                }
            },
        'RESOURCE_METHODS' : ['GET'],
        'ITEM_METHODS' : ['GET'],
        'ALLOW_UNKNOWN' : True, # http://stackoverflow.com/questions/34666941/python-eve-get-response-does-not-contain-contents-of-resource-unless-i-specify
        'DEBUG' : True,
        'INFO'  : True,
}

