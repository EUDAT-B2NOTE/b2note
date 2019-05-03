"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase, Client
from b2note_app.models import Annotation
from django.urls import reverse
from django.conf import settings
#from django.db import connections
from b2note_app.mongo_support_functions import *
#from b2note_devel.urls import urlpatterns
from accounts.models import UserCred
from django.contrib.auth import authenticate
from importlib import import_module
import json, os

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
    """
        Function: check_urls
        --------------------
        Checks that all urls provided as an argument are reachable.
        
        params:
            urllist (list): list with all urls defined in django.
            depth (int): depth on the hierarchy of urls.
            
        returns:
            bool: True if all urls are reachable. False otherwise.
    """
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
                    print(test_url + ": " + str(response.status_code))
                    return False
    return True

def check_internal_urls(f, app):
    """
        Function: check_internal_urls
        -----------------------------
        Checks that all links included the a template are reachable.
        
        params:
            f (str): path of a template file.
            app (str): name of the django app of the corresponding template.
            
        returns:
            bool: True if all links are reachable. False otherwise.
    """
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(open(f), "html.parser")
    links = soup.find_all('a')
    c = Client()
    
    for tag in links:
        link = tag.get('href', None)
        if link is not None:
            if link[0] != "{" and 'http' not in link:
                url = link
                if link[0] != "/":
                    if link[0] == "#":
                        if len(link) > 1: # avoid links with '#'
                            url = "/" + app + "/" + os.path.splitext(os.path.basename(f))[0] + link
                        else: 
                            pass
                    else:
                        link = "/" + link
                        url = "/" + app + link
                response = c.get(url)
                if response.status_code != 200 and response.status_code != 302:
                    response = c.get(link) # second try with the original link
                    if response.status_code != 200 and response.status_code != 302:
                        return False
        else:
            return False
            
    links = soup.find_all('form')
    for tag in links:
        link = tag.get('action', None)
        if link is not None:
            if link[0] != "{" and 'http' not in link:
                url = link
                if link[0] != "/":
                    if link[0] == "#":
                        if len(link) > 1: # avoid links with '#'
                            url = "/" + app + "/" + os.path.splitext(os.path.basename(f))[0] + link
                        else:
                            pass
                    else:
                        link = "/" + link
                        url = "/" + app + link
                response = c.get(url)
                if response.status_code != 200 and response.status_code != 302:
                    response = c.get(link) # second try with the original link
                    if response.status_code != 200 and response.status_code != 302:
                        return False
        else:
            return False
    
    return True

class B2noteappTest(TestCase):
    """
        TestCase class that clears the collection between the tests.
    """
    mongodb_name = 'test_%s' % settings.MONGO_DATABASE_NAME
    multi_db = True
    
    def _pre_setup(self):
        """
            Function: _pre_setup
            --------------------
            Automatically called before any test for connecting to MongoDB.
        """
        #from mongoengine.connection import connect, disconnect
        #disconnect()
        import urllib.request, urllib.parse, urllib.error, os
        pwd = urllib.parse.quote_plus(os.environ['MONGODB_PWD'])
        uri = "mongodb://" + os.environ['MONGODB_USR'] + ":" + pwd + "@127.0.0.1/" #?authMechanism=SCRAM-SHA-1
        
        #connect(self.mongodb_name, host=uri)
        from pymongo import MongoClient
        self.mclient = MongoClient(uri)
        self.mdb = self.mclient[self.mongodb_name]
        super(B2noteappTest, self)._pre_setup()

    def _post_teardown(self):
        """
            Function: _post_teardown
            --------------------
            Automatically called after any test for dropping the DB and disconnecting from MongoDB.
        """
        #from mongoengine.connection import get_connection, disconnect
        #connection = get_connection()
        #connection.drop_database(self.mongodb_name)
        #disconnect()
        #self.mclient.drop_database(self.mongodb_name)
        super(B2noteappTest, self)._post_teardown()
        
    def setUp(self):
        """
            Function: setUp
            --------------------
            Automatically called before any test for connection to SQLite and generating a new session.
        """
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
        """
            Function: login
            --------------------
            Allows login and authentication in the test environment.
        """
        self.user = authenticate(email=self.email,password=self.password,db=self.db)
        self.assertNotEqual(self.user, None)
        self.assertTrue(self.user.is_active)
        session = self.client.session
        session['user'] = self.user.annotator_id.annotator_id
        session.save()
        r = self.client.login(email=self.email,password=self.password, db=self.db)
        self.assertTrue(r)
        
    def create_annotation_db(self, jsonld_id="test", type=["others"]):
        """
            Function: create_annotation_db
            --------------------
            Creates a new entry in the DB of Annotations
        """

        return Annotation.objects.create(jsonld_id=jsonld_id, type=type,jsonld_context=[],creator=[],generator=[],motivation=[],body=[],target=[])


    def test_create_annotation_db(self):
        """
            Function: test_create_annotation_db
            --------------------
            Tests the creation of an Annotation using directly the model.
        """
        a = self.create_annotation_db()
        self.assertTrue(isinstance(a, Annotation))
        self.assertEqual(a.jsonld_id, "test")
        
    def test_create_annotation(self):
        """
            Function: test_create_annotation
            --------------------
            Tests the creation of an Annotation using the mongo support function.
        """
        # DB just created with no annotations in there
        before = Annotation.objects.filter().count()
        self.assertEqual(before, 0)
        a = CreateAnnotation("test_target")

        #self.assertTrue(type(a) is str and len(a)>0)
        # DB with 1 annotations created
        after = Annotation.objects.filter().count()
        self.assertEqual(after, 1)
        # get the ID of the created annotation
        db_id = Annotation.objects.filter()[0].id
        self.assertEqual(a, db_id)
        
    def test_dont_create_annotation(self):
        """
            Function: test_dont_create_annotation
            --------------------
            Tests the no creation of invalid annotations using the mongo support function.
        """
        a = CreateAnnotation(1234)
        self.assertFalse(a)
        a = CreateAnnotation("")
        self.assertFalse(a)

        
    def test_create_semantic_tag(self):
        """
            Function: test_create_semantic_tag
            --------------------
            Tests the creation of a Semantic Tag using the mongo support function.
        """
        # DB just created with no annotations in there
        before = Annotation.objects.filter().count()
        self.assertEqual(before, 0)
        a = CreateSemanticTag(
            subject_url="https://b2share.eudat.eu/record/30",
            subject_pid="http://hdl.handle.net/11304/test",
            object_json='[{"uris":"test_uri", "labels": "test_label"}]')
        self.assertTrue(a)
        # DB with 1 annotations created
        after = Annotation.objects.filter().count()
        self.assertEqual(after, 1)
        # get the ID of the created annotation
        db_id = Annotation.objects.filter()[0].id
        self.assertEqual(a, db_id)
        
    def test_dont_create_semantic_tag(self):
        """
            Function: test_dont_create_semantic_tag
            --------------------
            Tests the no creation of invalid semantic tags using the mongo support function.
        """
        a = CreateSemanticTag(
            subject_url=1234,
            subject_pid="http://hdl.handle.net/11304/test",
            object_json='{"uris":"test_uri", "labels": "test_label"}')
        self.assertTrue(not a)
        a = CreateSemanticTag(
            subject_url="https://b2share.eudat.eu/record/30",
            subject_pid="http://hdl.handle.net/11304/test",
            object_json='{"labels": "test_label"}')
        self.assertTrue(not a)
        
    def test_create_free_text_keyword(self):
        """
            Function: test_create_free_text_keyword
            --------------------
            Tests the creation of a free text keyword using the mongo support function.
        """
        # DB just created with no annotations in there
        before = Annotation.objects.filter().count()
        self.assertEqual(before, 0)
        a = CreateFreeTextKeyword(
            subject_url="https://b2share.eudat.eu/record/30",
            subject_pid="http://hdl.handle.net/11304/test",
            text="testing free text")
        self.assertTrue(a)
        # DB with 1 annotations created
        after = Annotation.objects.filter().count()
        self.assertEqual(after, 1)
        # get the ID of the created annotation
        db_id = Annotation.objects.filter()[0].id
        self.assertEqual(a, db_id)
        
    def test_dont_create_free_text_keyword(self):
        """
            Function: test_dont_create_free_text_keyword
            --------------------
            Tests the no creation of invalid free text keywords using the mongo support function.
        """
        a = CreateFreeTextKeyword(
            subject_url="https://b2share.eudat.eu/record/30",
            subject_pid=None,
            text=1234)
        self.assertTrue(not a)
        a = CreateFreeTextKeyword(
            subject_url="https://b2share.eudat.eu/record/30",
            subject_pid=None,
            text="")
        self.assertTrue(not a)
        
    def test_settings_view(self):
        """
            Function: test_settings_view
            --------------------
            Tests the view function settings
        """
        r = self.client.login(email=self.email,password=self.password, db=self.db)
        self.assertTrue(r)
        url = reverse("b2note_app.views.settings")
        resp = self.client.get(url) 
        self.assertEqual(resp.status_code, 200)
        self.client.logout()
        resp = self.client.get(url) 
        self.assertEqual(resp.status_code, 302)

    
    def test_hostpage_view(self):
        """
            Function: test_hostpage_view
            --------------------
            Tests the view function hostpage
        """
        url = reverse("b2note_app.views.hostpage")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        
    def test_interface_main_view(self):
        """
            Function: test_interface_main_view
            --------------------
            Tests the view function interface_main
        """
        url = reverse("b2note_app.views.interface_main")
        # Creates on annotation on the DB
        a = self.create_annotation_db()
        # Login
        self.login()
        resp = self.client.post(url, {'pid_tofeed': 'pid_test', 'subject_tofeed': 'subject_test'} )
        self.assertEqual(resp.status_code, 200)
        self.assertIn("subject_test", resp.content)


    def test_create_annotation_view(self):
        """
            Function: test_create_annotation_view
            --------------------
            Tests the view function create_annotation
        """
        #TODO fix reversematch error - updated in django >1.10
        from b2note_app import views as b2note_app_views
        url = reverse(b2note_app_views.create_annotation)
        json_dict = {}
        json_dict['pid_tofeed'] = 'http://hdl.handle.net/11304/test'
        json_dict['subject_tofeed'] = 'https://b2share.eudat.eu/record/30'
        json_dict['ontology_json'] = json.dumps([{'labels' : 'annotation_test',
                                                'uris': 'uri_test'}])
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
        """
            Function: test_delete_annotation_view
            --------------------
            Tests the view function delete_annotation
        """
        url = reverse("b2note_app.views.delete_annotation")
        db_id = self.test_create_annotation_view()
        json_dict = {}
        json_dict['pid_tofeed'] = 'pid_test'
        json_dict['subject_tofeed'] = 'https://b2share.eudat.eu/record/30'
        json_dict['db_id'] = db_id
        json_dict['delete_confirmed'] = 1
        resp = self.client.post(url, json_dict, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertNotIn("annotation_test", resp.content)
        # check that there is no annotations in the DB
        self.assertEqual(Annotation.objects.filter().count(), 0)
        
    
    def test_export_annotations_view(self):
        """
            Function: test_export_annotations_view
            --------------------
            Tests the view function export_annotations
        """
        url = reverse("b2note_app.views.export_annotations") 
        db_id = self.test_create_annotation_view()
        json_dict = {}
        json_dict['pid_tofeed'] = 'pid_test'
        json_dict['subject_tofeed'] = 'https://b2share.eudat.eu/record/30'
        json_dict['all_annotations'] = 1
        resp = self.client.post(url, json_dict)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("annotation_test", resp.content)
        
    def test_download_json_view(self):
        """
            Function: test_download_json_view
            --------------------
            Tests the view function download_json
        """
        url = reverse("b2note_app.views.download_json")
        self.test_export_annotations_view()
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("annotation_test", resp.content)
    
    # http://stackoverflow.com/questions/1828187/determine-complete-django-url-configuration    
    def parse_urls(self):
        """
            Function: parse_urls
            --------------------
            Tests that all urls included in the file urls.py are valid
        """
        self.assertTrue(check_urls(urlpatterns))
        
    def parse_internal_urls(self):
        """
            Function: parse_internal_urls
            --------------------
            Tests that all links included in the templates are valid
        """
        self.login()
        for d in os.listdir(settings.TEMPLATE_PATH):
            for f in os.listdir(settings.TEMPLATE_PATH + "/" + d):
                if os.path.splitext(f)[1] == '.html':
                    path = settings.TEMPLATE_PATH + "/" + d + "/" + f
                    self.assertTrue(check_internal_urls(path, d))

### Tomas tests - proper unit test covering basic structures - limit dependencies
    #test creating annotation, testing whether it contains specified fields, creating another annotation will incriese number of annotations
    def test_a1_create_annotation_check_body_and_target(self):
        # objects can be retrieved
        self.assertTrue(Annotation.objects != None)
        self.assertTrue(Annotation.objects.count()>=0)
        # body and target are defined
        self.assertTrue(Annotation.body != None)
        self.assertTrue(Annotation.target != None)
        a1 = Annotation.objects.create(type=["Annotation"],body=["free text"],target=["http://localhost"],jsonld_context=["jsonld"],creator=[],generator=[],motivation=[])
        self.assertEqual(len(a1.body),1)
        self.assertEqual(a1.body[0],"free text")
        self.assertEquals(len(a1.target),1)
        self.assertEquals(a1.target[0],"http://localhost")

    def test_a2_create_2_annotation_check_number_of_all_increased(self):
        # objects can be retrieved
        self.assertTrue(Annotation.objects != None)
        self.assertTrue(Annotation.objects.count()>=0)
        # body and target are defined
        self.assertTrue(Annotation.body != None)
        self.assertTrue(Annotation.target != None)
        a1 = Annotation.objects.create(type=["Annotation"],body=["free text"],target=["http://localhost"],jsonld_context=["jsonld"],creator=[],generator=[],motivation=[])
        a2 = Annotation.objects.all()
        self.assertEqual(len(a2),1)
        a3 = Annotation.objects.create(type=["Annotation"], body=["free text 2"], target=["http://localhost"],
                                       jsonld_context=["jsonld"], creator=[], generator=[], motivation=[])
        a4 = Annotation.objects.all()
        self.assertEqual(len(a4),2)

