from django.conf import settings
from django.contrib.auth.models import check_password
from accounts.models import UserCred

class EmailAuthBackend(object):
    """
    A custom authentication backend. Allows users to log in using their email address.
    """

    def authenticate(self, email=None, password=None, db='users'):
        """
        Authentication method
        """
        try:
            user = UserCred.objects.using(db).get(username=email)
            if user.check_password(password):
                return user
        except UserCred.DoesNotExist:
            return None

    def get_user(self, user_id, db='users'):
        try:
            user = UserCred.objects.using(db).get(pk=user_id)
            if user.is_active:
                return user
            return None
        except UserCred.DoesNotExist:
            return None