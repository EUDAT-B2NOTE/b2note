#UPGRADE patterns obsolete - use plain old list [ ];
#from django.conf.urls import patterns, url
from django.conf.urls import url
from accounts import views as accounts_views 

from .views import ResetPasswordRequestView, PasswordResetConfirmView

urlpatterns = [
    #url(r'^old_register$', 'accounts_views.old_register', name='old_register'),
    #url(r'^old_login$', 'accounts_views.old_login', name='oldlogin'),
    url(r'^logout$', accounts_views.logout, name='logout'),
    url(r'^profilepage$', accounts_views.profilepage, name='profile'),
    url(r'^feedbackpage$', accounts_views.feedbackpage, name='feedback'),

    url(r'^auth_main', accounts_views.auth_main, name='auth'),
    url(r'^auth_redirected', accounts_views.auth_redirected, name='redirected'),
    url(r'^login$', accounts_views.login, name='login'),
    url(r'^polling$', accounts_views.polling, name='polling'),
    url(r'^abort$', accounts_views.abort, name='abort'),
    url(r'^register$', accounts_views.register, name='register'),



    url(r'^reset_password_confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', PasswordResetConfirmView.as_view(),name='reset_password_confirm'),
    # PS: url above is going to used for next section of implementation.
    url(r'^reset_password$', ResetPasswordRequestView.as_view(), name="reset_password"),
    url(r'^request_account_retrieval$', accounts_views.request_account_retrieval, name='request_account_retrieval'),

]
