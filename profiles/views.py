from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import (
    EducationFormSet,
    LinkFormSet,
    ProfileForm,
    SkillFormSet,
    WorkExperienceFormSet,
)
from .models import Profile


def profile_detail(request, username=None):
    """
    If user is not authenticated, redirect to the login page. Otherwise, go to profile.
    """
    if not request.user.is_authenticated:
        return redirect("accounts.login")
    else:
        profile = get_object_or_404(Profile, user__username=request.user.username)

    return render(request, "profiles/profile_detail.html", {"profile": profile})


@login_required
def profile_edit(request):
    """
    Get the user's profile and uses it to fill out fields on the edit profile page.
    Allows users to update their profile and renders the updated page.
    """
    profile, _ = Profile.objects.get_or_create(
        user=request.user, defaults={"name": request.user.get_full_name() or request.user.username}
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
            for fs in formsets:
                fs.save()
            form.save()
            messages.success(request, "Profile saved.")
            return redirect("profiles:detail")

    return render(
        request,
        "profiles/profile_form.html",
        {
            "form": form,
            "work_formset": work_formset,
            "edu_formset": edu_formset,
            "skill_formset": skill_formset,
            "link_formset": link_formset,
        },
    )
