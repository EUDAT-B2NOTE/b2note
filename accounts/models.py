from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django_countries.fields import CountryField
from django.utils import timezone


# http://procrastinatingdev.com/django/using-configurable-user-models-in-django-1-5/
class UserCredManager(BaseUserManager):
    def create_user(self, username, email, password=None):
        user = self.model(username=email, password=password)
        user.set_password(password)
        ap = AnnotatorProfile(nickname=username,email=email)
        ap.save(using=self._db)
        user.annotator_id = ap
        user.save(using=self._db)
        return user

# http://blackglasses.me/2013/09/17/custom-django-user-model/
class UserCred(AbstractBaseUser):
    user_id = models.AutoField (primary_key=True)
    username = models.EmailField(unique=True, db_index=True)

    pawd = models.CharField(('password'), max_length=256)
    annotator_id = models.ForeignKey('AnnotatorProfile', db_column='annotator_id')

    USERNAME_FIELD = 'user_id'
    REQUIRED_FIELDS = []

    objects = UserCredManager()
    db = objects._db
    
    def __str__(self):
         return str(self.username)
     
    def getDB(self):
        return self.db


class AnnotatorProfile(models.Model):
    annotator_id    = models.AutoField( primary_key=True )
    nickname        = models.CharField( max_length=32, unique=True )
    first_name      = models.CharField( max_length=32 )
    last_name       = models.CharField( max_length=32 )
    email           = models.EmailField(unique=True, db_index=True)
    country         = CountryField(blank_label='(Select country)')
    organization    = models.CharField( max_length=64 )
    job_title       = models.CharField( max_length=32 )
    annotator_exp   = models.CharField( max_length=16, choices=[('b','beginners'),
                                                              ('i','intermediate'),
                                                              ('e','expert')] )

