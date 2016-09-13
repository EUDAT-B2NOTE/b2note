from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.contrib.auth import login as django_login, authenticate, logout as django_logout
from django.contrib.auth.decorators import login_required
from accounts.forms import AuthenticationForm, RegistrationForm
from accounts.models import AnnotatorProfile

# Create your views here.


def login(request):
    """
    Log in view
    """

    if request.session.get("is_console_access") is not None:
        ica = True
    else:
        ica = False

    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = authenticate(email=request.POST['username'], password=request.POST['password'])
            if user is not None:
                if user.is_active:
                    print type(user), isinstance(user, unicode), user
                    django_login(request, user)
                    print ">>>", user.annotator_id.annotator_id
                    request.session["user"] = user.annotator_id.annotator_id
                    if ica:
                        return redirect('/interface_main')
                    else:
                        return redirect('/profilepage')
    else:
        form = AuthenticationForm()

    return render_to_response('accounts/login.html',{'form': form, 'is_console_access': ica},
                              context_instance=RequestContext(request, {
                                  "pid_tofeed": request.session.get("pid_tofeed"),
                                  "subject_tofeed": request.session.get("subject_tofeed")
                              }))


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
    request.session["is_console_access"] = False
    django_logout(request)
    return redirect('/')