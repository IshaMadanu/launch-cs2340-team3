from django.shortcuts import render, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from .forms import CustomUserCreationForm, CustomErrorList, ProfileForm, WorkExperienceFormSet, EducationFormSet, SkillFormSet, LinkFormSet
from django.shortcuts import redirect
from django.forms.utils import ErrorList
from django.utils.safestring import mark_safe
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from .models import Account, Profile
from django.contrib.auth.decorators import login_required
from django.contrib import messages


class CustomErrorList(ErrorList):
    def __str__(self):
        if not self:
            return ''
        return mark_safe(''.join([f'<div class="alert alert-danger" role="alert">{e}</div>' for e in self]))

@login_required
def logout(request):
    auth_logout(request)
    return redirect('home.index')

def login(request):
    template_data = {}
    template_data['title'] = 'Login'
    if request.method == 'GET':
        return render(request, 'accounts/login.html',
            {'template_data': template_data})
    elif request.method == 'POST':
        user = authenticate(
            request,
            username = request.POST['username'],
            password = request.POST['password']
        )
        if user is None:
            template_data['error'] = 'The username or password is incorrect.'
            return render(request, 'accounts/login.html',
                {'template_data': template_data})
        else:
            auth_login(request, user)
            return redirect('home.index')

def signup(request):
    template_data = {}
    template_data['title'] = 'Sign Up'
    if request.method == 'GET':
        template_data['form'] = CustomUserCreationForm()
        return render(request, 'accounts/signup.html',
            {'template_data': template_data})
    elif request.method == 'POST':
        form = CustomUserCreationForm(request.POST, error_class=CustomErrorList)
        if form.is_valid():
            user = form.save()

            Account.objects.create(
                user=user,
                role=form.cleaned_data['role']
            )
            
            return redirect('accounts.login')
        else:
            template_data['form'] = form
            return render(request, 'accounts/signup.html',
                {'template_data': template_data})

def profile_detail(request, username=None):
    """
    If user is not authenticated, redirect to the login page. Otherwise, go to profile.
    """
    # if looking at your own profile
    if username is None:
        if not request.user.is_authenticated:
            return redirect("accounts.login")
        # get or create the current user's profile
        profile, created = Profile.objects.get_or_create(user=request.user, defaults={"name": request.user.get_full_name()})
        
    #if looking at someone else's profile
    else:
        profile = get_object_or_404(Profile, user__username=username)

    return render(request, "accounts/profile_detail.html", {"profile": profile})


@login_required
def profile_edit(request):
    """
    Get the user's profile and uses it to fill out fields on the edit profile page.
    Allows users to update their profile and renders the updated page.
    """
    profile, created = Profile.objects.get_or_create(user=request.user, defaults={"name": request.user.get_full_name()})

    form = ProfileForm(instance=profile)
    work_formset = WorkExperienceFormSet(instance=profile, prefix="work")
    edu_formset = EducationFormSet(instance=profile, prefix="edu")
    skill_formset = SkillFormSet(instance=profile, prefix="skill")
    link_formset = LinkFormSet(instance=profile, prefix="link")

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        work_formset = WorkExperienceFormSet(request.POST, instance=profile, prefix="work")
        edu_formset = EducationFormSet(request.POST, instance=profile, prefix="edu")
        skill_formset = SkillFormSet(request.POST, instance=profile, prefix="skill")
        link_formset = LinkFormSet(request.POST, instance=profile, prefix="link")

        formsets = [work_formset, edu_formset, skill_formset, link_formset]

        if form.is_valid() and all(fs.is_valid() for fs in formsets):
            for fs in formsets:
                fs.save()
            form.save()
            messages.success(request, "Profile saved.")
            return redirect("detail")

    return render(
        request,
        "accounts/profile_form.html",
        {
            "form": form,
            "work_formset": work_formset,
            "edu_formset": edu_formset,
            "skill_formset": skill_formset,
            "link_formset": link_formset,
        },
    )
