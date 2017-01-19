import os


agent = {
        'jsonld_id' : { 'type' : 'string' },
        'type' : {
                'type' : 'list',
                'schema' : {
                    'type' : 'string',
                    },
                },
        'name' : {
                'type' : 'list',
                'schema' : {
                    'type' : 'string',
                    },
                },
        'nickname' : { 'type' : 'string' },
        'email' : {
                'type' : 'list',
                'schema' : {
                    'type' : 'string',
                    },
                },
        'email_sha1' : {
                'type' : 'list',
                'schema' : {
                    'type' : 'string',
                    },
                },
        'homepage' : {
                'type' : 'list',
                'schema' : {
                    'type' : 'string',
                    },
                },
        }

body = {
        'type' : 'list',
        'schema' : {
            'jsonld_id' : { 'type' : 'string' },
            'value': {'type': 'string'},
            'purpose': {'type': 'string'},
            'type' : {
                'type' : 'list',
                'schema' : {
                    'type' : 'string',
                    },
                },
            'items': { 'type' : 'list',
                       'schema' : {
                           'type' : 'string',
                           'source' : 'string',
                           'value' : 'string'
                       }
                   },
            #'language' : {
            #    'type' : 'list',
            #    'schema' : {
            #        'type' : 'string',
            #        },
            #    },
            #'format' : {
            #    'type' : 'list',
            #    'schema' : {
            #        'type' : 'string',
            #        },
            #    },
            #'processingLanguage' : { 'type' : 'string' },
            #'textDirection' : { 'type' : 'string' },
            #'creator' : {
            #    'type' : 'list',
            #    'schema' : agent,
            #    },
            #'created' : { 'type' : 'datetime' },
            #'modified' : { 'type' : 'datetime' },
            },
        }

target = {
            'type' : 'list',
            'schema' : {
                'jsonld_id' : { 'type' : 'string' },
                'type' : {
                    'type' : 'list',
                    'schema' : {
                        'type' : 'string',
                        },
                    },
                #'format' : {
                #    'type' : 'list',
                #    'schema' : {
                #        'type' : 'string',
                #        },
                #    },
                #'language' : {
                #    'type' : 'list',
                #    'schema' : {
                #        'type' : 'string',
                #        },
                #    },
                #'processingLanguage' : { 'type' : 'string' },
                #'textDirection' : { 'type' : 'string' },
                #'accessibility' : {
                #    'type' : 'list',
                #    'schema' : {
                #        'type' : 'string',
                #        },
                #    },
                #'creator' : {
                #    'type' : 'list',
                #    'schema' : agent,
                #    },
                #'created' : { 'type' : 'datetime' },
                #'modified' : { 'type' : 'datetime' },
                #'rights' : {
                #    'type' : 'list',
                #    'schema' : {
                #        'type' : 'string',
                #        },
                #    },
                #'canonical' : { 'type' : 'string' },
                #'via' : {
                #    'type' : 'list',
                #    'schema' : {
                #        'type' : 'string',
                #        },
                #    },
                },
            }

annotations = {
                'allowed_filters': [
                    'jsonld_id',
                    'created',
                    'modified',
                    'generated',
                    'target.jsonld_id',
                    'body.type',
                    'body.value',
                    'body.purpose',
                    'body.items.type',
                    'body.items.value',
                    'body.items.source',
                    'creator.nickname',
                    'generator.name',
                    ],
                'datasource' : {
                    'source': 'b2note_app_annotation',
                    'projection': {
                        'jsonld_context' : 1,
                        'jsonld_id': 1,
                        'type': 1,
                        'created': 1,
                        'modified': 1,
                        'generated': 1,
                        'motivation': 1,
                        'target.jsonld_id': 1,
                        'body.type': 1,
                        'body.value': 1,
                        'body.purpose': 1,
                        'body.items' : 1,
                        'body.items.type' : 1,
                        'body.items.source' : 1,
                        'body.items.value' : 1,
                        'creator.type': 1,
                        'creator.nickname': 1,
                        'generator.type': 1,
                        'generator.name': 1,
                        'generator.homepage': 1
                        },
                    },
                'schema' : {
                    'jsonld_context' : { 'type' : 'string' },
                    'jsonld_id' : { 'type' : 'string' },
                    'type' : {
                        'type' : 'list',
                        'schema' : {
                            'type' : 'string',
                            },
                        },
                    'body' : body,
                    'target' : target,
                    'motivation': {
                        'type': 'list',
                        'schema': {
                            'type': 'string',
                        },
                    'creator' : {
                        'type' : 'list',
                        'schema' : agent,
                        },
                    'generator' : {
                        'type' : 'list',
                        'schema' : agent,
                        },
                    'created': {'type': 'datetime'},
                    'modified' : { 'type' : 'datetime' },
                    'generated': {'type': 'datetime'},
                    'language': {'type': 'string'},
                    'format': {'type': 'string'},
                    },
                    #'audience' : {
                    #    'type' : 'list',
                    #    'schema' : {
                    #        'jsonld_id' : { 'type' : 'string' },
                    #        'type' : {
                    #            'type' : 'list',
                    #            'schema' : {
                    #                'type' : 'string',
                    #                },
                    #            },
                    #        'props' : { 'type' : 'dict' },
                    #        },
                    #    },
                    #'rights' : {
                    #    'type' : 'list',
                    #    'schema' : {
                    #        'type' : 'string',
                    #        },
                    #    },
                    #'canonical' : { 'type' : 'string' },
                    #'via' : {
                    #    'type' : 'list',
                    #    'schema' : {
                    #        'type' : 'string',
                    #        },
                    #    },
                    #'stylesheet' : {
                    #    'type' : 'dict',
                    #    'schema' : {
                    #        'type' : { 'type' : 'string' },
                    #        'value' : { 'type' : 'string' },
                    #        },
                    #    },
                    },
                #'url' : 'annotations/<regex("[a-f0-9]{24}"):annotation_id>/files',
                }

mongo_settings = {
        'MONGO_HOST': 'localhost',
        'MONGO_PORT': 27017,
        'MONGO_DBNAME': os.environ['MONGODB_NAME'],
        'MONGO_USERNAME': os.environ['MONGODB_USR'],
        'MONGO_PASSWORD': os.environ['MONGODB_PWD'],
        'DOMAIN': {
            'annotations': annotations,
            },
        'RESOURCE_METHODS' : ['GET'],
        'ITEM_METHODS' : ['GET'],
        #'ALLOW_UNKNOWN' : True, # http://stackoverflow.com/questions/34666941/python-eve-get-response-does-not-contain-contents-of-resource-unless-i-specify
        'DEBUG' : True,
        'INFO'  : True,

        #'API_VERSION' : '1',

        'ALLOWED_FILTERS' : [],

        'XML' : False,
}
