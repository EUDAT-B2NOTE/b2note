"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.test.client import Client
from accounts.models import UserCred, AnnotatorProfile
from accounts.urls import urlpatterns as aurls
from b2note_devel.urls import urlpatterns as burls

class AccountTest(TestCase):
    username='test'
    password='1234'
    email='test@test.com'
    c=Client()

    def test_create_user(self):
        #UserCred.objects.create_user(username='test', email='test@test.com', password='1234')
        user = UserCred()
        user.set_password(self.password)
        ap = AnnotatorProfile(nickname=self.username, email=self.email)
        ap.save(using='users')
        user.annotator_id= ap
        user.save(using='users')
        
        
    def test_login(self):
        #self.test_create_user()
        response = self.c.get('/consolelogin')
        self.assertEqual(response.status_code, 200)
        response = self.c.post('/consolelogin', {'username': self.username, 'password': self.password})
        self.assertEqual(response.status_code, 200)
        response = self.c.post
        
    
    def test_logout(self):
        #self.test_create_user()
        self.test_login()
        response = self.c.get('/logout')
        self.assertEqual(response.status_code, 302)
        
    # http://stackoverflow.com/questions/1828187/determine-complete-django-url-configuration    
    def parse_urls(self):
        print "Accounts URL's:"
        for url in aurls:
            print url
        
        print "B2note URL's:"
        for url in burls:
            print url
            
        
