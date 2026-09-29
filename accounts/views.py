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
        return render(
            request,
            'accounts/login.html',
            {'template_data': template_data}
        )

    elif request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST['username'],
            password=request.POST['password']
        )

        if user is None:
            template_data['error'] = 'The username or password is incorrect.'
            return render(
                request,
                'accounts/login.html',
                {'template_data': template_data}
            )

        else:
            auth_login(request, user)
            next_url = request.POST.get('next') or request.GET.get('next')
            if next_url:
                return redirect(next_url)
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
                role=form.cleaned_data['role'],
                company_name=form.cleaned_data.get('company_name'),
                company_email=form.cleaned_data.get('company_email'),
            )
            
            return redirect('accounts.login')
        else:
            template_data['form'] = form
            return render(request, 'accounts/signup.html',
                {'template_data': template_data})

def _profile_defaults(user):
    """Values used the first time a profile row is created for a user."""
    return {"first_name": user.first_name, "last_name": user.last_name}
 
 
def profile_detail(request, username=None):
    """
    If user is not authenticated, redirect to the login page. Otherwise, go to profile.
    """
    # if looking at your own profile
    if username is None:
        # if not logged in
        if not request.user.is_authenticated:
            return redirect("accounts.login")
        # get or create the current user's profile
        profile, created = Profile.objects.get_or_create(
            user=request.user, defaults=_profile_defaults(request.user)
        )
 
    #if looking at someone else's profile
    else:
        profile = get_object_or_404(Profile, user__username=username)
 
    is_owner = request.user.is_authenticated and request.user == profile.user
 
    def shown(queryset):
        # per-entry visibility (education, work, links)
        return queryset if is_owner else queryset.filter(visible=True)
 
    context = {
        "profile": profile,
        "is_owner": is_owner,
        "show_name": is_owner or profile.name_visible,
        "show_picture": is_owner or profile.picture_visible,
        "show_headline": is_owner or profile.headline_visible,
        "show_location": is_owner or profile.location_visible,
        "educations": shown(profile.educations.all()),
        "work_experiences": shown(profile.work_experiences.all()),
        "links": shown(profile.links.all()),
        "skills": profile.skills.all() if is_owner else profile.skills.filter(skills_visible=True),    
    }
    return render(request, "accounts/profile_detail.html", context)
 
 
@login_required
def profile_edit(request):
    """
    Get the user's profile and uses it to fill out fields on the edit profile page.
    Allows users to update their profile and renders the updated page.
    """
    profile, created = Profile.objects.get_or_create(
        user=request.user, defaults=_profile_defaults(request.user)
    )
 
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
            form.save()
            for fs in formsets:
                fs.save()
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