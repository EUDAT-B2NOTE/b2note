from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.contrib.auth import login as django_login, authenticate, logout as django_logout

from accounts.forms import AuthenticationForm, RegistrationForm


# Create your views here.


def login(request):
    """
    Log in view
    """
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            print "\n"
            print "#" * 30
            print request.POST
            print "#" * 30
            print "\n"
            user = authenticate(username=request.POST['email'], password=request.POST['password'])
            if user is not None:
                if user.is_active:
                    django_login(request, user)
                    return redirect('b2note_app/hostpage')
    else:
        form = AuthenticationForm()
    return render_to_response('accounts/login.html', {'form': form,}, context_instance=RequestContext(request))


def register(request):
    """
    User registration view.
    """
    if request.method == 'POST':
        form = RegistrationForm(data=request.POST)
        if form.is_valid():
            user = form.save( using='users.sqlite3' )
            return redirect('/')
    else:
        form = RegistrationForm()
    return render_to_response('accounts/register.html', {'form': form,}, context_instance=RequestContext(request))


def logout(request):
    """
    Log out view
    """
    django_logout(request)
    return redirect('/')