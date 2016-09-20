from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.contrib.auth import login as django_login, authenticate, logout as django_logout
from django.contrib.auth.decorators import login_required
from django.forms.models import model_to_dict
from accounts.forms import AuthenticationForm, RegistrationForm, ProfileForm
from accounts.models import AnnotatorProfile, UserCred

# Create your views here.


def profilepage(request):
    """
    User profile view.
    """
    try:
        if request.session.get("user"):
            userprofile = AnnotatorProfile.objects.using('users').get(pk=request.session.get("user"))
            form = ProfileForm(initial = model_to_dict(userprofile) )
            return render_to_response('accounts/profilepage.html', {'form': form}, context_instance=RequestContext(request))
        else:
            return redirect('/logout')
    except Exception:
        print "Could not load or redirect from profilepage view."
        return False


def login(request):
    """
    Log in view
    """

    ica = False
    if request.session.get("is_console_access") is True:
        ica = True

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
                        request.session["is_console_access"] = False
                        return redirect('/homepage')
    else:
        if request.session.get("user"):
            return redirect('/hostpage', context=RequestContext(request))
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
        print form
        if form.is_valid():
            user = form.save()
            return redirect('/accounts/logout')
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