from django import forms

from .models import Education, Link, Profile, Project, Skill, WorkExperience


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["name", "headline", "bio", "location"]


class WorkExperienceForm(forms.ModelForm):
    class Meta:
        model = WorkExperience
        fields = ["company", "title", "start_date", "end_date", "description"]


class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = [
            "institution",
            "degree",
            "field_of_study",
            "start_date",
            "end_date",
        ]


class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ["name"]


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "description"]


class LinkForm(forms.ModelForm):
    class Meta:
        model = Link
        fields = ["label", "url"]


WorkExperienceFormSet = forms.inlineformset_factory(
    Profile,
    WorkExperience,
    form=WorkExperienceForm,
    extra=1,
    can_delete=True,
)

EducationFormSet = forms.inlineformset_factory(
    Profile,
    Education,
    form=EducationForm,
    extra=1,
    can_delete=True,
)

SkillFormSet = forms.inlineformset_factory(
    Profile,
    Skill,
    form=SkillForm,
    extra=1,
    can_delete=True,
)

ProjectFormSet = forms.inlineformset_factory(
    Profile,
    Project,
    form=ProjectForm,
    extra=1,
    can_delete=True,
)

LinkFormSet = forms.inlineformset_factory(
    Profile,
    Link,
    form=LinkForm,
    extra=1,
    can_delete=True,
)