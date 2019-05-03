# TODO why it is imported when not used?
from django.conf import settings
from django.contrib.auth.hashers import check_password
from accounts.models import UserCred

class EmailAuthBackend(object):
    """
    A custom authentication backend. Allows users to log in using their email address.
    """

    def authenticate(self, email=None, password=None, db='users', needpassword=True):
        """
        Authentication method
        
        if needpassword is set to False, will return the user regardless of password
        
        """
        try:
            user = UserCred.objects.using(db).get(username=email)
            if user.check_password(password) or not needpassword:
                return user
        except UserCred.DoesNotExist:
            return None

    # old auth method
    # def authenticate(self, email=None, password=None, db='users'):
    #     """
    #     Authentication method
    #     """
    #     try:
    #         user = UserCred.objects.using(db).get(username=email)
    #         if user.check_password(password):
    #             return user
    #     except UserCred.DoesNotExist:
    #         return None


    def get_user(self, user_id, db='users'):
        try:
            user = UserCred.objects.using(db).get(pk=user_id)
            if user.is_active:
                return user
            return None
        except UserCred.DoesNotExist:
            return None