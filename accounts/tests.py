"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.contrib.auth import login as django_login, authenticate, logout as django_logout
from accounts.models import UserCred
from accounts.views import login
from django.conf import settings
from django.utils.importlib import import_module

class MyRequest(dict):
    def __init__(self, req, session, user):
        self.__dict__ = req
        self.session = session
        self.user = user
        self.__dict__['META'] = {}

class AccountTest(TestCase):
    username='test'
    password='123456'
    email='test@test.com'
    db_user = None
    user = None
    req = None
    
    def setUp(self):
        self.db_user = UserCred.objects.create_user(username=self.username, email=self.email, password=self.password)
        settings.SESSION_ENGINE = 'django.contrib.sessions.backends.file'
        engine = import_module(settings.SESSION_ENGINE)
        store = engine.SessionStore()
        store.save()
        self.session = store
        self.client.cookies[settings.SESSION_COOKIE_NAME] = store.session_key

    def test_register_with_same_credentials(self):
        response = self.client.post('/register', {
            'username': self.email,
            'password': self.password,
            'first_name': 'a',
            'last_name': 'a',
            'organozation': 'a',
            'job_title': 'a',
            'annotator_exp': 'a',
            'country': 'a'
        }, follow=True)
        print("testing registraton")
        print(response.status_code)
        self.assertEqual(response.status_code, 200)

    def test_login(self):
        self.user = authenticate(email=self.email,password=self.password,db=self.db_user.getDB())
        response = self.client.post('/login', {'username': self.email, 'password': self.password}, follow=True)
        self.assertNotEqual(self.user, None)
        self.assertTrue(self.user.is_active)
        session = self.client.session
        session['user'] = self.user.annotator_id.annotator_id
        session.save()
        self.req = MyRequest(response.request, self.client.session, self.user)
        print self.req.session.items()
        django_login(self.req, self.user)
        self.assertTrue(self.user.is_authenticated())
        print self.req.session.items()
        
    def is_created(self):
        return UserCred.objects.get(username=self.email)        
        
    def test_logout(self):
        self.test_login()
        print self.req.session.items()
        django_logout(self.req)
        print self.req.session.items()

        
