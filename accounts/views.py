from django.shortcuts import render, render_to_response, redirect
from django.template import RequestContext
from django.contrib.auth import login as django_login, authenticate, logout as django_logout
from django.forms.models import model_to_dict
from accounts.forms import AuthenticationForm, RegistrationForm, OldRegistrationForm, ProfileForm
from accounts.models import AnnotatorProfile, UserCred, UserFeedback, FeatureRequest, BugReport

from b2note_app.nav_support_functions import list_navbarlinks, list_shortcutlinks

from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template import loader
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from b2note_devel.settings import DEFAULT_FROM_EMAIL, SUPPORT_DEST_EMAIL
from django.views.generic import *
from .forms.reset_password import PasswordResetRequestForm, SetPasswordForm, AccountRetrieveForm
from .forms.user_feebacks import FeedbackForm, FeatureForm, BugReportForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models.query_utils import Q
from django.db import IntegrityError

from oic.oic import Client
from oic.utils.authn.client import CLIENT_AUTHN_METHOD
from oic.oic.message import ProviderConfigurationResponse
from oic.oic.message import RegistrationResponse
import json
from oic import rndstr
from oic.utils.http_util import Redirect
from oic.oic.message import AuthorizationResponse
import os
from django.http import HttpResponse
import json
import requests.packages.urllib3

import logging


stdlogger = logging.getLogger('b2note')



def feedbackpage(request):
    """
    Page for users to provide feedbacks on their epxerience of the service.
    One form for each of the 3 tabs (user-feedback, feature request and bug report).

    :param request:
    :return:
    """

    navbarlinks = list_navbarlinks(request, ["Help page"])
    navbarlinks.append({"url": "/help#helpsection_fedbackpage", "title": "Help page", "icon": "question-sign"})
    shortcutlinks = list_shortcutlinks(request, [])

    try:

        if request.session.get("user"):
            userprofile = AnnotatorProfile.objects.using('users').get(pk=request.session.get("user"))

            if request.method == 'POST':

                dest = SUPPORT_DEST_EMAIL

                if request.POST.get("feedback_submit") != None:

                    feedback_f = FeedbackForm(data=request.POST)

                    if feedback_f.is_valid():
                        names_t = {}
                        for fname in ["id_eval_overall", "id_eval_usefull", "id_eval_experience", "id_eval_interface", "id_eval_efficiency"]:
                            names_t[fname] = 0
                            if fname in request.POST:
                                if request.POST[fname] and isinstance(int(str(request.POST[fname])), int):
                                    names_t[fname] = int(str(request.POST[fname]))


                        fdbck = UserFeedback( email=userprofile,
                                              general_comment=feedback_f.cleaned_data["general_comment"],
                                              eval_overall=names_t["id_eval_overall"],
                                              eval_usefull=names_t["id_eval_usefull"],
                                              eval_experience=names_t["id_eval_experience"],
                                              eval_interface=names_t["id_eval_interface"],
                                              eval_efficiency=names_t["id_eval_efficiency"],
                                              )

                        fdbck.save()

                        c = {'form': feedback_f, 'names_t': names_t, 'nl': list(names_t.keys()),
                             'user_contact': userprofile.email, 'user_experience': userprofile.annotator_exp}
                        email_template_name = 'accounts/userfeedback_email.html'
                        # copied from django/contrib/admin/templates/registration/password_reset_email.html to templates directory
                        # Email subject *must not* contain newlines
                        email = loader.render_to_string(email_template_name, c)
                        send_mail('B2Note user evaluation feedback',
                                  email, DEFAULT_FROM_EMAIL,
                                  [dest], fail_silently=False)

                        msg = "Thank you for providing us your feedback."

                        data_dict = {"navbarlinks":  navbarlinks,
                                     "shortcutlinks": shortcutlinks,
                                     "msg": msg}

                        return render_to_response('accounts/feedback_page.html', data_dict, context_instance=RequestContext(request))

                if request.POST.get("feature_submit") != None:

                    feature_f = FeatureForm(data=request.POST)

                    if feature_f.is_valid():

                        featr = FeatureRequest( email=userprofile,
                                              title             = feature_f.cleaned_data["title"],
                                              short_description = feature_f.cleaned_data["short_description"],
                                              extra_description = feature_f.cleaned_data["extra_description"],
                                              alt_contact       = feature_f.cleaned_data["alt_contact"],
                                              )

                        featr.save()

                        c = {'form': feature_f, 'user_contact': userprofile.email, 'user_experience': userprofile.annotator_exp}
                        email_template_name = 'accounts/userfeedback_email.html'
                        # copied from django/contrib/admin/templates/registration/password_reset_email.html to templates directory
                        # Email subject *must not* contain newlines
                        email = loader.render_to_string(email_template_name, c)
                        send_mail('B2Note user feature request',
                                  email, DEFAULT_FROM_EMAIL,
                                  [dest], fail_silently=False)

                        msg = "Thank you for submitting a feature request."

                        data_dict = {"navbarlinks":  navbarlinks,
                                     "shortcutlinks": shortcutlinks,
                                     "msg": msg}

                        return render_to_response('accounts/feedback_page.html', data_dict, context_instance=RequestContext(request))

                if request.POST.get("bug_submit") != None:

                    bugreport_f = BugReportForm(data=request.POST)

                    if bugreport_f.is_valid():

                        names_t = {}
                        for fname in ["id_severity", "id_affected_function"]:
                            names_t[fname] = 0
                            if fname in request.POST:
                                if request.POST[fname]:
                                    if str(request.POST[fname]) in [str(x) for x in range(5)]:
                                        names_t[fname] = int(str(request.POST[fname]))
                                    elif isinstance(str(request.POST[fname]), str):
                                        names_t[fname] = str(request.POST[fname])

                        bugrep = BugReport( email               = userprofile,
                                            affected_function   = str(names_t["id_affected_function"]),
                                            short_description   = bugreport_f.cleaned_data["short_description"],
                                            extra_description   = bugreport_f.cleaned_data["extra_description"],
                                            severity            = int(names_t["id_severity"]),
                                            browser             = bugreport_f.cleaned_data["browser"],
                                            alt_contact         = bugreport_f.cleaned_data["alt_contact"],
                                            )

                        bugrep.save()

                        c = {'form': bugreport_f, 'names_t': names_t, 'nl': list(names_t.keys()),
                             'user_contact': userprofile.email, 'user_experience': userprofile.annotator_exp}
                        email_template_name = 'accounts/userfeedback_email.html'
                        # copied from django/contrib/admin/templates/registration/password_reset_email.html to templates directory
                        # Email subject *must not* contain newlines
                        email = loader.render_to_string(email_template_name, c)
                        send_mail('B2Note user bug report',
                                  email, DEFAULT_FROM_EMAIL,
                                  [dest], fail_silently=False)

                        msg = "Thank you for submitting a bug report."

                        data_dict = {"navbarlinks":  navbarlinks,
                                     "shortcutlinks": shortcutlinks,
                                     "msg": msg}

                        return render_to_response('accounts/feedback_page.html', data_dict, context_instance=RequestContext(request))


            feedback_f  = FeedbackForm()
            feature_f   = FeatureForm()
            bugreport_f = BugReportForm()

            data_dict = {"navbarlinks": navbarlinks,
                         "shortcutlinks": shortcutlinks,
                         "feedback_f": feedback_f,
                         "feature_f": feature_f,
                         "bugreport_f": bugreport_f }

            return render_to_response('accounts/feedback_page.html', data_dict, context_instance=RequestContext(request))

        else:
            return redirect('/logout')
    except Exception:
        print("Could not load or redirect from fedebackpage view.")
        stdlogger.error("Could not load or redirect from fedebackpage view.")
        return False



def request_account_retrieval(request):
    """
    Request account retrieval view.
    """

    navbarlinks = list_navbarlinks(request, [])
    shortcutlinks = list_shortcutlinks(request, [])

    if request.method == 'POST':
        form = AccountRetrieveForm(data=request.POST)
        if form.is_valid():
            c = {'form': form,}
            email_template_name = 'accounts/account_retrieve_email.html'
            # copied from django/contrib/admin/templates/registration/password_reset_email.html to templates directory
            # Email subject *must not* contain newlines
            email = loader.render_to_string(email_template_name, c)
            send_mail('B2Note user request account retrieval',
                      email, DEFAULT_FROM_EMAIL,
                      ['b2note-support@bsc.es'],
                      fail_silently=False)
            messages.success(request,
                             '''The information was sent to the service support team.
                             Unfortunately, for the time being, your access to your B2Note account can not be granted.
                             The support team shall get in contact with you shortly and provide more assistance.
                             Thank you for your interest in B2Note and your understanding.''')
            form = None
        else:
            messages.error(request, "Information does not qualify.")
    else:
        form = AccountRetrieveForm()
    return render_to_response('accounts/request_account_retrieval.html', {
        'shortcutlinks': shortcutlinks,
        'navbarlinks': navbarlinks,
        'form': form,}, context_instance=RequestContext(request))


# http://ruddra.com/2015/09/18/implementation-of-forgot-reset-password-feature-in-django/
class PasswordResetConfirmView(FormView):
    template_name = "accounts/reset_password.html"
    success_url = "accounts/reset_password"
    form_class = SetPasswordForm

    def post(self, request, uidb64=None, token=None, *arg, **kwargs):
        """
        View that checks the hash in a password reset link and presents a
        form for entering a new password.
        """
        UserModel = UserCred()
        form = self.form_class(request.POST)
        assert uidb64 is not None and token is not None  # checked by URLconf
        try:
            if isinstance(uidb64, str): uidb64 = str(uidb64)
            uid = urlsafe_base64_decode(uidb64)
            user = UserCred.objects.using('users').get(pk=uid)

        except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            if form.is_valid():
                new_password = form.cleaned_data['new_password2']
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Password has been reset.')
                return self.form_valid(form)
            else:
                messages.error(request, 'Password reset has not been successful.')
                return self.form_invalid(form)
        else:
            messages.error(request,'The reset password link is no longer valid.')
            return self.form_invalid(form)


class ResetPasswordRequestView(FormView):
    template_name = "accounts/reset_password.html"  # code for template is given below the view's code
    success_url = "/accounts/reset_password"
    form_class = PasswordResetRequestForm

    @staticmethod
    def validate_email_address(email):
        '''
        This method here validates the if the input is an email address or not. Its return type is boolean, True if the input is a email address or False if its not.
        '''
        try:
            validate_email(email)
            return True
        except ValidationError:
            return False

    #http://stackoverflow.com/questions/19687375/django-formview-does-not-have-form-context
    def get_context_data(self, **kwargs):
        context = super(ResetPasswordRequestView, self).get_context_data(**kwargs)
        context['navbarlinks'] = list_navbarlinks()
        context['shortcutlinks'] = list_shortcutlinks()
        return context

    def post(self, request, *args, **kwargs):
        '''
        A normal post request which takes input from field "email_or_username" (in ResetPasswordRequestForm).
        '''

        form = self.form_class(request.POST)
        data = None
        if form.is_valid():
            data = form.cleaned_data["email_or_username"]
        if self.validate_email_address(data) is True:  # uses the method written above
            '''
            If the input is an valid email address, then the following code will lookup for users associated with that email address. If found then an email will be sent to the address, else an error message will be printed on the screen.
            '''
            associated_users = UserCred.objects.using('users').filter(Q(username=data))
            if associated_users.exists():
                for user in associated_users:
                    domain_root = request.META['HTTP_HOST']
                    if domain_root and isinstance(domain_root, str) and domain_root[:len("http://b2note")]=="http://b2note":
                        domain_root = "https://b2note"+domain_root[len("http://b2note"):]
                    c = {
                        'email': user.username,
                        'domain': domain_root, #request.META['HTTP_HOST'],
                        'site_name': 'EUDAT B2Note',
                        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                        'user': user,
                        'token': default_token_generator.make_token(user),
                        'protocol': 'http',
                    }
                    subject_template_name = 'accounts/password_reset_subject.txt'
                    # copied from django/contrib/admin/templates/registration/password_reset_subject.txt to templates directory
                    email_template_name = 'accounts/password_reset_email.html'
                    # copied from django/contrib/admin/templates/registration/password_reset_email.html to templates directory
                    subject = loader.render_to_string(subject_template_name, c)
                    # Email subject *must not* contain newlines
                    subject = ''.join(subject.splitlines())
                    email = loader.render_to_string(email_template_name, c)
                    send_mail(subject, email, DEFAULT_FROM_EMAIL, [user.username], fail_silently=False)
                result = self.form_valid(form)
                messages.success(request,
                                 'An email has been sent. Please check inbox to continue resetting password.')
                return result
            result = self.form_invalid(form)
            messages.error(request, 'This email address does not qualify.')
            return result
        else:
            result = self.form_invalid(form)
            messages.error(request, 'This input does not qualify.')
            return result
        messages.error(request, 'Invalid Input')
        return self.form_invalid(form)


def profilepage(request):
    """
    User profile view.
    """

    navbarlinks = list_navbarlinks(request, ["Help page"])
    navbarlinks.append({"url": "/help#helpsection_useraccountpage", "title": "Help page", "icon": "question-sign"})
    shortcutlinks = list_shortcutlinks(request, [])

    try:
        if request.session.get("user"):
            userprofile = AnnotatorProfile.objects.using('users').get(pk=request.session.get("user"))
            form = ProfileForm(initial = model_to_dict(userprofile) )
            return render_to_response('accounts/profilepage.html', {
                'user_nickname': userprofile.nickname,
                'navbarlinks': navbarlinks,
                'shortcutlinks': shortcutlinks,
                'form': form}, context_instance=RequestContext(request))
        else:
            return redirect('/logout')
    except Exception:
        print("Could not load or redirect from profilepage view.")
        stdlogger.error("Could not load or redirect from profilepage view.")
        return False


def prepare_client():
    # http://pyoidc.readthedocs.io/en/latest/examples/rp.html


    # Instantiate a client
    client = Client(client_authn_method=CLIENT_AUTHN_METHOD)


    # Register the OP
    # endpoints are now loaded from a json file rather than defined here
    # DEV endpoints
    # issuer = "https://unity.eudat-aai.fz-juelich.de:443"
    # authorization_endpoint = "https://unity.eudat-aai.fz-juelich.de:443/oauth2-as/oauth2-authz"
    # token_endpoint = "https://unity.eudat-aai.fz-juelich.de:443/oauth2/token"
    # userinfo_endpoint = "https://unity.eudat-aai.fz-juelich.de:443/oauth2/userinfo"
    # PROD endpoints
    # issuer = "https://b2access.eudat.eu:443"
    # authorization_endpoint = "https://b2access.eudat.eu:443/oauth2-as/oauth2-authz"
    # token_endpoint = "https://b2access.eudat.eu:443/oauth2/token"
    # userinfo_endpoint = "https://b2access.eudat.eu:443/oauth2/userinfo"
    try:
        dir = os.path.dirname(__file__)
        provider_endpoints = json.load(open(dir + '/provider_endpoints.json'))
        issuer = provider_endpoints['issuer']
        authorization_endpoint = provider_endpoints['authorization_endpoint']
        token_endpoint = provider_endpoints['token_endpoint']
        userinfo_endpoint = provider_endpoints['userinfo_endpoint']
    except:
        print("Error when reading provider_endpoints.json")
        stdlogger.error("Error when reading provider_endpoints.json")
        issuer = "error"
        authorization_endpoint = "error"
        token_endpoint = "error"
        userinfo_endpoint = "error"
    op_info = ProviderConfigurationResponse(issuer=issuer, authorization_endpoint=authorization_endpoint, token_endpoint=token_endpoint, userinfo_endpoint=userinfo_endpoint)
    client.provider_info = op_info


    # Set our credentials (that we got from manually registering to B2Access), as well as the redirect URI
    try:
        dir = os.path.dirname(__file__)
        client_credentials = json.load(open(dir + '/client_credentials.json'))
        id = client_credentials['client_id']
        secret = client_credentials['client_secret']
        uri = client_credentials['client_redirect_uri']
    except:
        print("Error when reading client_credential.json")
        stdlogger.error("Error when reading client_credential.json")
        id = "error"
        secret = "error"
        uri = "error"
    # /!\ Added the redirect URI here, else it's not defined later (in args ={[...] client.registration_response["redirect_uris"][0])
    uris = [uri]
    info = {"client_id": id, "client_secret": secret, "redirect_uris": uris}
    client_reg = RegistrationResponse(**info)
    client.store_registration_info(client_reg)
    return client


global client
client = prepare_client()

def auth_main(request):
    """
      Function: auth
      ----------------------------
        Redirects to B2Access for authentication

    """
    request.session["connecting"] = 1
    request.session["popup_state"] = "ongoing"
    # http://pyoidc.readthedocs.io/en/latest/examples/rp.html
    # Auth code
    request.session["nonce"] = rndstr()
    request.session["state"] = rndstr()
    args = {"client_id": client.client_id, "response_type": "code", "scope": ["openid", "USER_PROFILE"], "nonce": request.session["nonce"],
            "redirect_uri": client.registration_response["redirect_uris"][0], "state": request.session["state"]}
    auth_req = client.construct_AuthorizationRequest(request_args=args)
    # /!\ client.authorization_endpoint used in the example is not defined (or it's an empty string maybe)
    # using client.provider_info["authorization_endpoint"] instead
    login_url = auth_req.request(client.provider_info["authorization_endpoint"])
    return redirect(login_url)
    # Redirect (cap R) does not work


def auth_redirected(request):
    """
      Function: auth
      ----------------------------
        Deal with the user after they are redirected from B2Access

    """
    # http://pyoidc.readthedocs.io/en/latest/examples/rp.html

    # Get the code
    # response = os.environ.get("QUERY_STRING")
    # doesn't work
    response = request.get_full_path()
    response = response[len('/accounts/auth_redirected'):]
    aresp = client.parse_response(AuthorizationResponse, info=response, sformat="urlencoded")
    try:
        code = aresp["code"]
    except:
        request.session["connecting"] = 0
        request.session["popup_state"]="canceled"
        return HttpResponse('Authentication canceled <script type="text/javascript"> setTimeout(function(){window.close()}, 1000); </script>')
    try:
        assert aresp["state"] == request.session["state"]
    except:
        request.session["connecting"] = 0
        request.session["popup_state"]="canceled"
        print("Incorrect authentication state")
        stdlogger.error("Incorrect authentication state")
        return HttpResponse('Authentication canceled, incorrect state <script type="text/javascript"> setTimeout(function(){window.close()}, 1000); </script>')


    # Use code to get token
    args = {"code": aresp["code"]}
    # I had the error:
    # MissingEndpoint at /auth_redirected, No 'token_endpoint' specified
    # fix:
    client.token_endpoint = client.provider_info["token_endpoint"]
    # pyoidc function do_access_token_request was modified: added 'verify=False' parameter to remove the attempt at decoding and verification
    resp = client.do_access_token_request(state=aresp["state"], request_args=args, authn_method="client_secret_basic", verify=False)
    resp_json = json.loads(resp)
    access_token = resp_json["access_token"]
    request.session["access_token"] = access_token


    # use token to get user info
    user_info_endpoint = client.provider_info['userinfo_endpoint']
    user_info = requests.get(user_info_endpoint, verify=False, headers={'Authorization': 'Bearer ' + access_token})
    user_info = user_info.text
    user_info = json.loads(user_info)
    if "email" in user_info:
        request.session["auth_email"] = user_info["email"]
    else:
        print("Error when reading user email from B2Access")
        stdlogger.error("Error when reading user email from B2Access")
    if "name" in user_info:
        # this is for the dev version of b2access
        request.session["auth_name"] = user_info["name"]
    elif "distinguishedName" in user_info:
        # this is for the master version of b2access
        # u'distinguishedName': u'/C=EU/O=EUDAT/OU=B2ACCESS/CN=31eec9c8-e99e-4393-87d9-3d62d7b04369/CN=aymeric rodriguez',
        request.session["auth_dn"] = user_info["distinguishedName"]
        request.session["auth_name"] = request.session["auth_dn"].split("/")[-1][3:]
    else:
        print("Error when reading user name from B2Access")
        stdlogger.error("Error when reading user name from B2Access")
    #request.session["auth_cn"] = user_info["cn"]
    #request.session["auth_id"] = user_info["unity:persistent"]
    #request.session["auth_sub"] = user_info["sub"]
    #request.session["auth_urn"] = user_info["urn:oid:2.5.4.49"]


    #debug: display user_info
    #return render(request, "accounts/auth_redirected.html", {'state': user_info})


    # parsing name
    name = request.session["auth_name"]
    space = False
    for i in range(len(name)):
        if name[i] == " ":
            space = i
            break
    if space:
        firstname = name[:space]
        surname = name[space + 1:]
    else:
        surname = name
        firstname = name
        stdlogger.info("User " + user_info["email"] + ": can't parse full name (" + name + ") into a firstname and a surname. firstname and surname were both set to" + name)
    request.session["auth_firstname"] = firstname
    request.session["auth_surname"] = surname


    # if user has an account, sign in. If user has no account, write that down
    user = authenticate(email=request.session.get("auth_email"), needpassword=False)
    if user is not None:
        # Login
        if user.is_active:
            django_login(request, user)
            request.session["user"] = user.annotator_id.annotator_id
    else:
        request.session["registration_state"] = "todo"


    # Close popup
    request.session["connecting"] = 0
    return HttpResponse('Success <script type="text/javascript"> setTimeout(function(){window.close()}, 700); </script>')


def login(request):
    """
    Log in view
    """
    navbarlinks = list_navbarlinks(request, ["Login", "Help page"])
    navbarlinks.append({"url": "/help#helpsection_loginpage", "title": "Help page", "icon": "question-sign"})
    shortcutlinks = []

    login_failed_msg = False

    request.session["connecting"] = 0

    if request.method == 'POST':
        login_failed_msg = True
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = authenticate(email=request.POST['username'], password=request.POST['password'])
            if user is not None:
                if user.is_active:
                    django_login(request, user)
                    request.session["user"] = user.annotator_id.annotator_id
                    login_failed_msg = False
                    return redirect('/interface_main')
    else:
        if request.session.get("user"):
            return redirect('/interface_main', context=RequestContext(request))
        else:
            form = AuthenticationForm()

    popup = 1
    if request.session.get("popup")==0:
        popup = 0
        request.session["popup"] = 1

    return render_to_response('accounts/login.html',{'form': form},
                              context_instance=RequestContext(request, {
                                  'login_failed_msg': login_failed_msg,
                                  'navbarlinks': navbarlinks,
                                  'shortcutlinks': shortcutlinks,
                                  "pid_tofeed": request.session.get("pid_tofeed"),
                                  "subject_tofeed": request.session.get("subject_tofeed"),
                                  "popup": popup,
                              }))


def polling(request):
    if request.session.get("user"):
        return HttpResponse('logged')
    elif (request.session.get('registration_state') == "todo"):
        return HttpResponse('do_registration')
    elif (request.session.get('popup_state') == "canceled"):
        return HttpResponse('cancel')
    elif (request.session["connecting"] == 1):
        return HttpResponse('wait')
    else:
        return HttpResponse('')


def old_login(request):
    """
    Log in view
    """
    navbarlinks = list_navbarlinks(request, ["Login", "Help page"])
    navbarlinks.append({"url": "/help#helpsection_loginpage", "title": "Help page", "icon": "question-sign"})
    shortcutlinks = []

    login_failed_msg = False

    if request.method == 'POST':
        login_failed_msg = True
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = authenticate(email=request.POST['username'], password=request.POST['password'])
            if user is not None:
                if user.is_active:
                    django_login(request, user)
                    request.session["user"] = user.annotator_id.annotator_id
                    login_failed_msg = False
                    return redirect('/interface_main')
    else:
        if request.session.get("user"):
            return redirect('/interface_main', context=RequestContext(request))
        else:
            form = AuthenticationForm()

    return render_to_response('accounts/old_login.html',{'form': form},
                              context_instance=RequestContext(request, {
                                  'login_failed_msg': login_failed_msg,
                                  'navbarlinks': navbarlinks,
                                  'shortcutlinks': shortcutlinks,
                                  "pid_tofeed": request.session.get("pid_tofeed"),
                                  "subject_tofeed": request.session.get("subject_tofeed")
                              }))

def abort(request):
    request.session['user'] = None

    request.session["registration_state"] = None

    request.session['auth_email'] = None
    #request.session["auth_cn"] = None
    request.session["auth_name"] = None
    request.session["auth_dn"] = None
    #request.session["auth_id"] = None
    #request.session["auth_sub"] = None
    #request.session["auth_urn"] = None
    request.session["auth_firstname"] = None
    request.session["auth_surname"] = None
    request.session["popup"] = 0

    return redirect('/interface_main')


def register(request):
    """
    User registration view.
    """

    navbarlinks = list_navbarlinks(request, ["Registration", "Help page"])
    navbarlinks.append({"url": "/help#helpsection_registrationpage", "title": "Help page", "icon": "question-sign"})
    shortcutlinks = list_shortcutlinks(request, ["Registration"])


    auth_email = request.session["auth_email"]
    auth_firstname = request.session["auth_firstname"]
    auth_surname = request.session["auth_surname"]
    auth_data = {"auth_email": auth_email, "auth_firstname": auth_firstname, "auth_lastname": auth_surname}

    if request.method == 'POST':
        data = request.POST.copy()
        data.update(auth_data)
        form = RegistrationForm(data=data)
        if form.is_valid():
            try:
                user = form.save()
                request.session["registration_state"] = "done"
                user = authenticate(email=auth_email, password="password")
                if user.is_active:
                    django_login(request, user)
                    request.session["user"] = user.annotator_id.annotator_id
            except IntegrityError:
                # catch "UNIQUE constraint failed" error
                # May catch other errors in which case the error message displayed in the UI would not be accurate
                return render_to_response(
                    'accounts/register.html',
                    {'navbarlinks': navbarlinks, 'shortcutlinks': shortcutlinks, 'form': form, 'alreadytaken': True},
                    context_instance=RequestContext(request)
                )

            return redirect('/interface_main')
        else:
            print(form.errors)
    else:
        form = RegistrationForm(data=auth_data)
    return render_to_response('accounts/register.html', {
        'navbarlinks': navbarlinks,
        'shortcutlinks': shortcutlinks,
        'auth_email': auth_email,
        'auth_firstname': auth_firstname,
        'auth_lastname': auth_surname,
        'form': form,}, context_instance=RequestContext(request))

def old_register(request):
    """
    User registration view.
    """

    navbarlinks = list_navbarlinks(request, ["Registration", "Help page"])
    navbarlinks.append({"url": "/help#helpsection_registrationpage", "title": "Help page", "icon": "question-sign"})
    shortcutlinks = list_shortcutlinks(request, ["Registration"])

    if request.method == 'POST':
        form = OldRegistrationForm(data=request.POST)
        if form.is_valid():
            try:
                user = form.save()
            except IntegrityError:
                # catch "UNIQUE constraint failed" error
                # May catch other errors in which case the error message displayed in the UI would not be accurate
                return render_to_response(
                    'accounts/old_register.html',
                    {'navbarlinks': navbarlinks, 'shortcutlinks': shortcutlinks, 'form': form, 'alreadytaken': True},
                    context_instance=RequestContext(request)
                )
            return redirect('/login')
        else:
            print(form.errors)
    else:
        form = OldRegistrationForm()
    return render_to_response('accounts/old_register.html', {
        'navbarlinks': navbarlinks,
        'shortcutlinks': shortcutlinks,
        'form': form,}, context_instance=RequestContext(request))


def logout(request):
    """
    Log out view
    """
    django_logout(request)
    request.session["popup"] = 0
    return redirect('/accounts/login')

