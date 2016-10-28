"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.test.client import Client
from django.contrib.auth import login as django_login, authenticate, logout as django_logout
from accounts.models import UserCred
from accounts.views import login

class AccountTest(TestCase):
    username='test'
    password='123456'
    email='test@test.com'
    user = None
    c = Client()
    
    def setUp(self):
        self.user = UserCred.objects.create_user(username=self.username, email=self.email, password=self.password)
        
    def is_created(self):
        print UserCred.objects.get(username=self.email)
    
    def test_login(self):
        response = self.c.get('/login')
        self.assertEqual(response.status_code, 200)
        #auth = authenticate(email=self.email,password=self.password,db=self.user.getDB())
        auth = self.c.login(email=self.email,password=self.password,db=self.user.getDB())
        self.assertTrue(auth)
        response = self.c.post('/login', {'username': self.email, 'password': self.password})
        self.assertEqual(response.status_code, 200)
        #print response.content
        response = self.c.get('/homepage')
        self.assertEqual(response.status_code, 200)
        
        
    
    def test_logout(self):
        #self.test_create_user()
        self.test_login()
        response = self.c.get('/logout')
        self.assertEqual(response.status_code, 302)
            
        
