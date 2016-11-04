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
from b2note_devel.urls import urlpatterns
from accounts.models import UserCred
from django.contrib.auth import authenticate
from django.utils.importlib import import_module
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

def check_urls(urllist, depth=0):
    c = Client()
    for entry in urllist:
        if hasattr(entry, 'url_patterns'):
                check_urls(entry.url_patterns, depth+1)
        else:
            test_url = entry.regex.pattern.translate(None, '^$')
            response = None
            if depth == 1:
                if 'reset_password_confirm' not in test_url:
                    response = c.get('/accounts/' + test_url)
            else:
                response = c.get('/' + test_url)
            
            if response is not None:
                if response.status_code != 200 and response.status_code != 302:
                    print test_url + ": " + str(response.status_code)
                    return False
    return True

class B2noteappTest(TestCase):
    """
        TestCase class that clear the collection between the tests
    """
    mongodb_name = 'test_%s' % settings.MONGO_DATABASE_NAME
    multi_db = True
    
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
        
    def setUp(self):
        self.username='test'
        self.password='123456'
        self.email='test@test.com'
        self.db='users'
        self.db_user = UserCred.objects.create_user(username=self.username, email=self.email, password=self.password, db=self.db)
        settings.SESSION_ENGINE = 'django.contrib.sessions.backends.file'
        engine = import_module(settings.SESSION_ENGINE)
        store = engine.SessionStore()
        store.save()
        self.session = store
        self.client.cookies[settings.SESSION_COOKIE_NAME] = store.session_key
        
    def login(self):
        self.user = authenticate(email=self.email,password=self.password,db=self.db)
        self.assertNotEqual(self.user, None)
        self.assertTrue(self.user.is_active)
        session = self.client.session
        session['user'] = self.user.annotator_id.annotator_id
        session.save()
        r = self.client.login(email=self.email,password=self.password, db=self.db)
        self.assertTrue(r)
    
    def test_settings_view(self):
        r = self.client.login(email=self.email,password=self.password, db=self.db)
        self.assertTrue(r)
        url = reverse("b2note_app.views.settings")
        resp = self.client.get(url) 
        self.assertEqual(resp.status_code, 200)
        self.client.logout()
        resp = self.client.get(url) 
        self.assertEqual(resp.status_code, 302)

    
    def test_hostpage_view(self):
        url = reverse("b2note_app.views.hostpage")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        
    def create_annotation_db(self, jsonld_id="test", type=["others"]):
        return Annotation.objects.create(jsonld_id=jsonld_id, type=type)
    
    def test_create_annotation_db(self):
        a = self.create_annotation_db()
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
        
    def test_create_free_text_keyword(self):
        # DB just created with no annotations in there
        before = Annotation.objects.filter().count()
        self.assertEqual(before, 0)
        a = CreateFreeTextKeyword(u"https://b2share.eudat.eu/record/30", u"testing free text")
        self.assertTrue(a)
        # DB with 1 annotations created
        after = Annotation.objects.filter().count()
        self.assertEqual(after, 1)
        # get the ID of the created annotation
        db_id = Annotation.objects.filter()[0].id
        self.assertEqual(a, db_id)
        
    def test_dont_create_free_text_keyword(self):
        a = CreateFreeTextKeyword(u"https://b2share.eudat.eu/record/30", 1234)
        self.assertTrue(not a)
        a = CreateFreeTextKeyword(u"https://b2share.eudat.eu/record/30", "")
        self.assertTrue(not a)
        
    def test_interface_main_view(self):
        url = reverse("b2note_app.views.interface_main")
        # Creates on annotation on the DB
        a = self.create_annotation_db()
        # Login
        self.login()
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
        json_dict['semantic_submit'] = 'test'

        self.login()
        # DB just created with no annotations in there
        before = Annotation.objects.filter().count()
        self.assertEqual(before, 0)
        resp = self.client.post(url, json_dict, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("annotation_test", resp.content)
        # DB with 1 annotations created
        after = Annotation.objects.filter().count()
        self.assertEqual(after, 1)
        # get the ID of the created annotation
        db_id = Annotation.objects.filter()[0].id
        # return the db_id value for deleting the annotation from DB
        return db_id
        
        
    def test_delete_annotation_view(self):
        url = reverse("b2note_app.views.delete_annotation")
        db_id = self.test_create_annotation_view()
        json_dict = {}
        json_dict['pid_tofeed'] = 'pid_test'
        json_dict['subject_tofeed'] = 'subject_test'
        json_dict['db_id'] = db_id
        json_dict['delete_confirmed'] = 1
        resp = self.client.post(url, json_dict, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertNotIn("annotation_test", resp.content)
        # check that there is no annotations in the DB
        self.assertEqual(Annotation.objects.filter().count(), 0)
        
    
    def test_export_annotations_view(self):
        url = reverse("b2note_app.views.export_annotations") 
        db_id = self.test_create_annotation_view()
        json_dict = {}
        json_dict['pid_tofeed'] = 'pid_test'
        json_dict['subject_tofeed'] = 'subject_test'
        json_dict['all_annotations'] = 1
        resp = self.client.post(url, json_dict)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("annotation_test", resp.content)
        
    def test_download_json_view(self):
        url = reverse("b2note_app.views.download_json")
        self.test_export_annotations_view()
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("annotation_test", resp.content)
    
    # http://stackoverflow.com/questions/1828187/determine-complete-django-url-configuration    
    def parse_urls(self):
        self.assertTrue(check_urls(urlpatterns))

