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
        print "\n"
        print "#" * 30
        print request.POST
        print "#" * 30
        print "\n"
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = authenticate(email=request.POST['username'], password=request.POST['password'])
            if user is not None:
                if user.is_active:
                    django_login(request, user)
                    print "REDIRECT"
                    return render_to_response('accounts/profilepage.html', {'user': user,},
                                              context_instance=RequestContext(request))
    else:
        form = AuthenticationForm()
    print "RENDER"
    return render_to_response('accounts/login.html', {'form': form,}, context_instance=RequestContext(request))


def register(request):
    """
    User registration view.
    """
    if request.method == 'POST':
        print "=======>", request.POST
        form = RegistrationForm(data=request.POST)
        print "=======>", form.is_valid()
        if form.is_valid():
            user = form.save()
            return redirect('accounts/profilepage')
    else:
        form = RegistrationForm()
    return render_to_response('accounts/register.html', {'form': form,}, context_instance=RequestContext(request))


def profilepage(request):
    """
    User profile view.
    """
    if request.method == 'POST':
        print "=======>", request.POST
        user = django_login(request, user)
        #form = RegistrationForm(data=request.POST)
        #print "=======>", form.is_valid()
        #if form.is_valid():
        #    user = form.save()
        #    return redirect('/hostpage')
    else:
        return redirect('/')
    return render_to_response('accounts/profilepage.html', {'user': user,}, context_instance=RequestContext(request))


def logout(request):
    """
    Log out view
    """
    django_logout(request)
    return redirect('/')