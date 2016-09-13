from django.db import models
from django.contrib.auth.models import AbstractBaseUser, UserManager
from django_countries.fields import CountryField



# http://blackglasses.me/2013/09/17/custom-django-user-model/
class UserCred(AbstractBaseUser):
    user_id = models.AutoField (primary_key=True)
    username = models.EmailField(unique=True, db_index=True)

    pawd = models.CharField(('password'), max_length=256)
    annotator_id = models.ForeignKey('AnnotatorProfile', db_column='annotator_id')

    USERNAME_FIELD = 'user_id'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
         return str(self.username)



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

