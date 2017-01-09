from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django_countries.fields import CountryField
from django.utils import timezone


# http://procrastinatingdev.com/django/using-configurable-user-models-in-django-1-5/
class UserCredManager(BaseUserManager):
    def create_user(self, username, email, password=None, db='users'):
        user = self.model(username=email, password=password)
        user.set_password(password)
        ap = AnnotatorProfile(nickname=username,email=email)
        ap.save(using=db)
        user.annotator_id = ap
        user.save(using=db)
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

class UserFedback(models.Model):
    feedback_id     = models.AutoField( primary_key=True )
    email           = models.ForeignKey( AnnotatorProfile, to_field="email" )
    date_created    = models.DateTimeField( auto_now_add=True, null=True )
    eval_overall    = models.PositiveSmallIntegerField()
    eval_usefull    = models.PositiveSmallIntegerField()
    eval_experience = models.PositiveSmallIntegerField()
    eval_interface  = models.PositiveSmallIntegerField()
    eval_efficiency = models.PositiveSmallIntegerField()
    general_comment = models.CharField( max_length=5000)


class FeatureRequest(models.Model):
    feature_id  = models.AutoField( primary_key=True )
    email       = models.ForeignKey(AnnotatorProfile, to_field="email")
    title       = models.CharField( max_length=100 )
    short_description   = models.CharField( max_length=5000 )
    extra_description   = models.TextField()
    date_created        = models.DateTimeField(auto_now_add=True, null=True)
    alt_contact         = models.CharField( max_length=500 )


class BugReport(models.Model):
    bugreport_id    = models.AutoField( primary_key=True )
    email           = models.ForeignKey(AnnotatorProfile, to_field="email")
    CR = 'Create'
    ED = 'Edit'
    EX = 'Export'
    SE = 'Search'
    OT = 'Other'
    FUNCTIONALITY_CHOICES = (
        (CR, 'Create annotation'),
        (ED, 'Edit annotation'),
        (EX, 'Export annotation'),
        (SE, 'Ssearch annotation'),
        (OT, 'Other functionality')
    )
    not_working     = models.CharField(max_length=2,
                                      choices=FUNCTIONALITY_CHOICES,
                                      default=OT)
    expected            = models.CharField( max_length=5000 )
    actual              = models.CharField( max_length=5000 )
    extra_description   = models.TextField()
    browser             = models.CharField( max_length=200 )
    severity            = models.PositiveSmallIntegerField()
    date_created        = models.DateTimeField(auto_now_add=True, null=True)
    alt_contact         = models.CharField( max_length=500 )

