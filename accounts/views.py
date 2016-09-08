from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.contrib.auth import login as django_login, authenticate, logout as django_logout

from accounts.forms import AuthenticationForm, RegistrationForm
from accounts.models import AnnotatorProfile

# Create your views here.


def login(request):
    """
    Log in view
    """
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = authenticate(email=request.POST['username'], password=request.POST['password'])
            if user is not None:
                if user.is_active:
                    django_login(request, user)
                    request.session["user"] = user.user_id
                    return redirect('accounts/profilepage')
    else:
        form = AuthenticationForm()
    return render_to_response('accounts/login.html', {'form': form,}, context_instance=RequestContext(request))


def profilepage(request):
    """
    User profile view.
    """
    if request.session.get("user"):
        userprofile = AnnotatorProfile.objects.using('users').get(pk=request.session.get("user"))
        return render_to_response('accounts/profilepage.html', {'profile': userprofile, }, context_instance=RequestContext(request))
    else:
        return redirect('/')


def register(request):
    """
    User registration view.
    """
    if request.method == 'POST':
        form = RegistrationForm(data=request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('/login.html')
        else:
            print form.errors
    else:
        form = RegistrationForm()
    return render_to_response('accounts/register.html', {'form': form,}, context_instance=RequestContext(request))


def logout(request):
    """
    Log out view
    """
    django_logout(request)
    return redirect('/')