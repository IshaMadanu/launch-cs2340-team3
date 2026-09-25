from django import forms
from django.forms import inlineformset_factory

from .models import Education, Link, Profile, Skill, WorkExperience


class ProfileForm(forms.ModelForm):
    class Meta:
        CHOICES = [('one', 'One'), ('two', 'Two')]
        model = Profile
        fields = ["name", "headline", "bio"]
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 6, "placeholder" : "Tell use a little bit about yourself!"}),
            "headline" : forms.TextInput(attrs={"placeholder" : "CS Student @ Georgia Tech Interested in AI and Robotics"}),
        }


class WorkExperienceForm(forms.ModelForm):
    class Meta:
        model = WorkExperience
        fields = ["company", "title", "start_date", "end_date", "description"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 3}),
        }


class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = ["institution", "degree", "field_of_study", "start_date", "end_date"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }


class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ["name"]


class LinkForm(forms.ModelForm):
    class Meta:
        model = Link
        fields = ["label", "url"]


WorkExperienceFormSet = inlineformset_factory(
    Profile,
    WorkExperience,
    form=WorkExperienceForm,
    extra=1,
    can_delete=True,
)

EducationFormSet = inlineformset_factory(
    Profile,
    Education,
    form=EducationForm,
    extra=1,
    can_delete=True,
)

SkillFormSet = inlineformset_factory(
    Profile,
    Skill,
    form=SkillForm,
    extra=1,
    can_delete=True,
)

LinkFormSet = inlineformset_factory(
    Profile,
    Link,
    form=LinkForm,
    extra=1,
    can_delete=True,
)
