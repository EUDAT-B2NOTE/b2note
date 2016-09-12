"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from b2note_app.models import Annotation
from django.core.urlresolvers import reverse
from django.conf import settings
from django.db import connections
from b2note_app.mongo_support_functions import *
import json

#class B2noteappFailTest(TestCase):
    #"""
        #TestCase class that  the collection between the tests
    #"""
    #def _pre_setup(self):
        #from mongoengine.connection import connect, disconnect
        #disconnect()
        #import urllib, os
        #pwd = urllib.quote_plus(os.environ['MONGODB_PWD'])
        #uri = "mongodb://" + os.environ['MONGODB_USR'] + ":" + pwd + "@127.0.0.1/" + self.mongodb_name + "?authMechanism=SCRAM-SHA-1"
        
        #connect(self.mongodb_name, host=uri)
        #super(B2noteappTest, self)._pre_setup()

    #def _post_teardown(self):
        #from mongoengine.connection import get_connection, disconnect
        #connection = get_connection()
        #connection.drop_database(self.mongodb_name)
        #disconnect()
        #super(B2noteappTest, self)._post_teardown()
    
    #def test_dont_create_annotation(self):
        #a = CreateAnnotation(u"test_target")
        #self.assertEqual(a, None)

class B2noteappTest(TestCase):
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
        super(B2noteappTest, self)._pre_setup()

    def _post_teardown(self):
        from mongoengine.connection import get_connection, disconnect
        connection = get_connection()
        connection.drop_database(self.mongodb_name)
        disconnect()
        super(B2noteappTest, self)._post_teardown()
        
    def create_annotation(self, jsonld_id="test", type=["others"]):
        return Annotation.objects.create(jsonld_id=jsonld_id, type=type)
    
    def test_annotation_creation(self):
        a = self.create_annotation()
        self.assertTrue(isinstance(a, Annotation))
        self.assertEqual(a.jsonld_id, "test")
        
    def test_create_annotation(self):
        # DB just created with no annotations in there
        before = Annotation.objects.filter().count()
        self.assertEqual(before, 0)
        a = CreateAnnotation(u"test_target")
        self.assertTrue(type(a) is unicode and len(a)>0)
        # DB with 1 annotations created
        after = Annotation.objects.filter().count()
        self.assertEqual(after, 1)
        # get the ID of the created annotation
        db_id = Annotation.objects.filter()[0].id
        self.assertEqual(a, db_id)
        
    def test_dont_create_annotation(self):
        a = CreateAnnotation(1234)
        self.assertFalse(a)
        a = CreateAnnotation("")
        self.assertFalse(a)
        #a = CreateAnnotation(u"test_target")
        #self.assertEqual(a, None)
        
    def test_create_semantic_tag(self):
        # DB just created with no annotations in there
        before = Annotation.objects.filter().count()
        self.assertEqual(before, 0)
        a = CreateSemanticTag(u"https://b2share.eudat.eu/record/30", '{"uris":"test_uri", "labels": "test_label"}')
        self.assertTrue(a)
        # DB with 1 annotations created
        after = Annotation.objects.filter().count()
        self.assertEqual(after, 1)
        # get the ID of the created annotation
        db_id = Annotation.objects.filter()[0].id
        self.assertEqual(a, db_id)
        
        
    def test_dont_create_semantic_tag(self):
        a = CreateSemanticTag(1234, '{"uris":"test_uri", "labels": "test_label"}')
        self.assertTrue(not a)
        a = CreateSemanticTag(u"https://b2share.eudat.eu/record/30", '{"labels": "test_label"}')
        self.assertTrue(not a)
        
    def test_create_free_text(self):
        # DB just created with no annotations in there
        before = Annotation.objects.filter().count()
        self.assertEqual(before, 0)
        a = CreateFreeText(u"https://b2share.eudat.eu/record/30", u"testing free text")
        self.assertTrue(a)
        # DB with 1 annotations created
        after = Annotation.objects.filter().count()
        self.assertEqual(after, 1)
        # get the ID of the created annotation
        db_id = Annotation.objects.filter()[0].id
        self.assertEqual(a, db_id)
        
    def test_dont_create_free_text(self):
        a = CreateFreeText(u"https://b2share.eudat.eu/record/30", 1234)
        self.assertTrue(not a)
        a = CreateFreeText(u"https://b2share.eudat.eu/record/30", "")
        self.assertTrue(not a)
        
    def test_interface_main_view(self):
        a = self.create_annotation()
        url = reverse("b2note_app.views.interface_main")
        resp = self.client.post(url, {'pid_tofeed': 'pid_test', 'subject_tofeed': 'subject_test'} )
        self.assertEqual(resp.status_code, 200)
        self.assertIn("subject_test", resp.content)


    def test_create_annotation_view(self):
        url = reverse("b2note_app.views.create_annotation")
        json_dict = {}
        json_dict['pid_tofeed'] = 'pid_test'
        json_dict['subject_tofeed'] = 'subject_test'
        json_dict['ontology_json'] = json.dumps({'labels' : 'annotation_test',
                                                'uris': 'uri_test'})

        # DB just created with no annotations in there
        before = Annotation.objects.filter().count()
        self.assertEqual(before, 0)
        resp = self.client.post(url, json_dict )
        self.assertEqual(resp.status_code, 200)
        self.assertIn("annotation_test", resp.content)
        # DB with 1 annotations created
        after = Annotation.objects.filter().count()
        self.assertEqual(after, 1)
        # get the ID of the created annotation
        db_id = Annotation.objects.filter()[0].id
        # check that the ID is present in the response 
        self.assertIn(db_id, resp.content)
        # return the db_id value for deleting the annotation from DB
        return db_id
        
        
    def test_delete_annotation_view(self):
        db_id = self.test_create_annotation_view()
        url = reverse("b2note_app.views.delete_annotation")
        resp = self.client.post(url, {'pid_tofeed': 'pid_test', 'subject_tofeed': 'subject_test', 'db_id': db_id})
        self.assertEqual(resp.status_code, 200)
        self.assertNotIn("annotation_test", resp.content)
        # check that there is no annotations in the DB
        self.assertEqual(Annotation.objects.filter().count(), 0)
        
    
    def test_export_annotations_view(self):
        db_id = self.test_create_annotation_view()
        url = reverse("b2note_app.views.export_annotations")    
        resp = self.client.post(url, {'pid_tofeed': 'pid_test', 'subject_tofeed': 'subject_test'})
        self.assertEqual(resp.status_code, 200)
        self.assertIn("annotation_test", resp.content)
        
    def test_download_json_view(self):
        self.test_export_annotations_view()
        
        url = reverse("b2note_app.views.download_json")    
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("annotation_test", resp.content)



