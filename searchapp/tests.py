"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from searchapp.models import Annotation
from django.core.urlresolvers import reverse
from django.conf import settings
from django.db import connections
import json

class SearchappTest(TestCase):
    """
        TestCase class that clear the collection between the tests
    """
    mongodb_name = 'test_%s' % settings.MONGO_DATABASE_NAME
    
    def _pre_setup(self):
        from mongoengine.connection import connect, disconnect
        disconnect()
        import urllib, os
        pwd = urllib.quote_plus(os.environ['MONGODB_PWD'])
        uri = "mongodb://" + os.environ['MONGODB_USR'] + ":" + pwd + "@127.0.0.1/" + self.mongodb_name + "?authMechanism=SCRAM-SHA-1"
        
        connect(self.mongodb_name, host=uri)
        super(SearchappTest, self)._pre_setup()

    def _post_teardown(self):
        from mongoengine.connection import get_connection, disconnect
        connection = get_connection()
        connection.drop_database(self.mongodb_name)
        disconnect()
        super(SearchappTest, self)._post_teardown()
        
    def create_annotation(self, jsonld_id="test", jsonld_type=["others"]):
        return Annotation.objects.create(jsonld_id=jsonld_id, jsonld_type=jsonld_type)
    
    def test_annotation_creation(self):
        a = self.create_annotation()
        self.assertTrue(isinstance(a, Annotation))
        self.assertEqual(a.jsonld_id, "test")
        
    def test_interface_main_view(self):
        a = self.create_annotation()
        url = reverse("searchapp.views.interface_main")
        resp = self.client.post(url, {'pid_tofeed': 'pid_test', 'subject_tofeed': 'subject_test'} )
        self.assertEqual(resp.status_code, 200)
        self.assertIn("subject_test", resp.content)


    def test_create_annotation_view(self):
        url = reverse("searchapp.views.create_annotation")
        json_dict = {"ontology_json": {"ancestors": ["ancestor_test"],
                                       "indexed_date":"2016-01-01",
                                       "labels" : "annotation_test",
                                       "text_auto": "annotation_test",
                                       "uris": ["uri_test"],
                                       "id": "id_test",
                                       "_version_": "1"},
                     "pid_tofeed": "pid_test",
                     "subject_tofeed": u"subject_test"
                    }
        resp = self.client.post(url, json_dict )

        self.assertEqual(resp.status_code, 200)
        self.assertIn("test", resp.content)
        
    def test_delete_annotation_view(self):
        url = reverse("searchapp.views.delete_annotation")
        
        resp = self.client.post(url, {'pid_tofeed': 'pid_test', 'subject_tofeed': 'subject_test'})
        self.assertEqual(resp.status_code, 200)
        self.assertIn("test", resp.content)
        
    def test_export_annotations_view(self):
        url = reverse("searchapp.views.export_annotations")
        
        resp = self.client.post(url, {'pid_tofeed': 'pid_test', 'subject_tofeed': 'subject_test'})
        self.assertEqual(resp.status_code, 200)
        self.assertIn("test", resp.content)
        



