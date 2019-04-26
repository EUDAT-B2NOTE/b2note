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
    # upgrade to djongo default on_delete
    annotator_id = models.ForeignKey('AnnotatorProfile', db_column='annotator_id',on_delete=models.CASCADE)

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

class UserFeedback(models.Model):
    feedback_id     = models.AutoField( primary_key=True )
    #upgrade to djongo default on_delete
    email           = models.ForeignKey( AnnotatorProfile, to_field="email",on_delete=models.CASCADE)
    date_created    = models.DateTimeField( auto_now_add=True, null=True )
    eval_overall    = models.PositiveSmallIntegerField()
    eval_usefull    = models.PositiveSmallIntegerField()
    eval_experience = models.PositiveSmallIntegerField()
    eval_interface  = models.PositiveSmallIntegerField()
    eval_efficiency = models.PositiveSmallIntegerField()
    general_comment = models.CharField( max_length=5000, null=True )


class FeatureRequest(models.Model):
    feature_id  = models.AutoField( primary_key=True )
    # upgrade to djongo default on_delete
    email       = models.ForeignKey(AnnotatorProfile, to_field="email", on_delete=models.CASCADE)
    title       = models.CharField( max_length=100, null=True )
    short_description   = models.CharField( max_length=5000, null=True )
    extra_description   = models.TextField( null=True )
    date_created        = models.DateTimeField(auto_now_add=True, null=True)
    alt_contact         = models.CharField( max_length=500, null=True )


class BugReport(models.Model):
    bugreport_id    = models.AutoField( primary_key=True )
    # upgrade to djongo default on_delete
    email           = models.ForeignKey(AnnotatorProfile, to_field="email",on_delete=models.CASCADE)
    affected_function   = models.CharField( max_length=100, null=True )
    short_description   = models.CharField( max_length=5000, null=True )
    extra_description   = models.TextField( null=True )
    severity            = models.PositiveSmallIntegerField()
    browser             = models.CharField( max_length=200, null=True )
    date_created        = models.DateTimeField(auto_now_add=True, null=True)
    alt_contact         = models.CharField( max_length=500, null=True )
