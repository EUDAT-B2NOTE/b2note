from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.contrib.auth import login as django_login, authenticate, logout as django_logout
from django.forms.models import model_to_dict
from accounts.forms import AuthenticationForm, RegistrationForm, ProfileForm
from accounts.models import AnnotatorProfile, UserCred, UserFeedback, FeatureRequest, BugReport

from b2note_app.nav_support_functions import list_navbarlinks, list_shortcutlinks

from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template import loader
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from b2note_devel.settings import DEFAULT_FROM_EMAIL
from django.views.generic import *
from forms.reset_password import PasswordResetRequestForm, SetPasswordForm, AccountRetrieveForm
from forms.user_feebacks import FeedbackForm, FeatureForm, BugReportForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models.query_utils import Q
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

                dest = 'abremaud@esciencefactory.com'

                if request.POST.get("feedback_submit") != None:

                    feedback_f = FeedbackForm(data=request.POST)

                    if feedback_f.is_valid():

                        fdbck = UserFeedback( email=userprofile,
                                              general_comment=feedback_f.cleaned_data["general_comment"],
                                              eval_overall=int(feedback_f.cleaned_data["eval_overall"]),
                                              eval_usefull=int(feedback_f.cleaned_data["eval_usefull"]),
                                              eval_experience=int(feedback_f.cleaned_data["eval_experience"]),
                                              eval_interface=int(feedback_f.cleaned_data["eval_interface"]),
                                              eval_efficiency=int(feedback_f.cleaned_data["eval_efficiency"]),
                                              )

                        fdbck.save()

                        c = {'form': feedback_f, 'username': userprofile.nickname}
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

                        c = {'form': feature_f, 'username': userprofile.nickname}
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

                        bugrep = BugReport( email=userprofile,
                                            affected_function   = bugreport_f.cleaned_data["affected_function"],
                                            short_description   = bugreport_f.cleaned_data["short_description"],
                                            extra_description   = bugreport_f.cleaned_data["extra_description"],
                                            severity            = int(bugreport_f.cleaned_data["severity"]),
                                            browser             = bugreport_f.cleaned_data["browser"],
                                            alt_contact         = bugreport_f.cleaned_data["alt_contact"],
                                            )

                        bugrep.save()

                        c = {'form': bugreport_f, 'username': userprofile.nickname}
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
        print "Could not load or redirect from fedebackpage view."
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
            if isinstance(uidb64, unicode): uidb64 = str(uidb64)
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
                messages.error(request, 'Password reset has not been unsuccessful.')
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
                    if domain_root and isinstance(domain_root, (unicode, str)) and domain_root[:len("http://b2note")]=="http://b2note":
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
                                 'An email has been sent. Please check inbox to continue reseting password.')
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
        print "Could not load or redirect from profilepage view."
        stdlogger.error("Could not load or redirect from profilepage view.")
        return False


def login(request):
    """
    Log in view
    """

    navbarlinks = list_navbarlinks(request, ["Login", "Help page"])
    navbarlinks.append({"url": "/help#helpsection_loginpage", "title": "Help page", "icon": "question-sign"})
    shortcutlinks = []

    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = authenticate(email=request.POST['username'], password=request.POST['password'])
            if user is not None:
                if user.is_active:
                    django_login(request, user)
                    request.session["user"] = user.annotator_id.annotator_id
                    return redirect('/interface_main')
    else:
        if request.session.get("user"):
            return redirect('/interface_main', context=RequestContext(request))
        else:
            form = AuthenticationForm()

    return render_to_response('accounts/login.html',{'form': form},
                              context_instance=RequestContext(request, {
                                  'navbarlinks': navbarlinks,
                                  'shortcutlinks': shortcutlinks,
                                  "pid_tofeed": request.session.get("pid_tofeed"),
                                  "subject_tofeed": request.session.get("subject_tofeed")
                              }))


def register(request):
    """
    User registration view.
    """

    navbarlinks = list_navbarlinks(request, ["Registration", "Help page"])
    navbarlinks.append({"url": "/help#helpsection_registrationpage", "title": "Help page", "icon": "question-sign"})
    shortcutlinks = list_shortcutlinks(request, ["Registration"])

    if request.method == 'POST':
        form = RegistrationForm(data=request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('/accounts/logout')
        else:
            print form.errors
    else:
        form = RegistrationForm()
    return render_to_response('accounts/register.html', {
        'navbarlinks': navbarlinks,
        'shortcutlinks': shortcutlinks,
        'form': form,}, context_instance=RequestContext(request))


def logout(request):
    """
    Log out view
    """
    django_logout(request)
    return redirect('/accounts/login')
