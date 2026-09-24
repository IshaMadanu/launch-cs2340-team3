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
    Public-facing view of a profile. If no username is given, show the
    logged-in user's own profile.
    """
    if username is None:
        if not request.user.is_authenticated:
            return redirect("login")
        profile = get_object_or_404(Profile, user__username=request.user.username)
    else:
        profile = get_object_or_404(Profile, user__username=username)

    return render(request, "profiles/profile_detail.html", {"profile": profile})


@login_required
def profile_edit(request):
    """
    Create-or-update view for the logged-in user's own profile, including
    all related work experience, education, skills, and links via formsets.
    """
    profile, _ = Profile.objects.get_or_create(
        user=request.user, defaults={"name": request.user.get_full_name() or request.user.username}
    )

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
            return redirect("profiles:detail")
    else:
        form = ProfileForm(instance=profile)
        work_formset = WorkExperienceFormSet(instance=profile, prefix="work")
        edu_formset = EducationFormSet(instance=profile, prefix="edu")
        skill_formset = SkillFormSet(instance=profile, prefix="skill")
        link_formset = LinkFormSet(instance=profile, prefix="link")

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
