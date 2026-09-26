from django.contrib.auth.forms import UserCreationForm
from django.forms.utils import ErrorList
from django.utils.safestring import mark_safe
from django import forms
from django.forms import inlineformset_factory
from .models import Education, Link, Profile, Skill, WorkExperience

from django.contrib.auth.models import User

class CustomErrorList(ErrorList):
    def __str__(self):
        if not self:
            return ''
        return mark_safe(''.join([f'<div class="alert alert-danger" role="alert">{e}</div>' for e in self]))

class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    ROLE_CHOICES = [
        ('candidate', 'Candidate'),
        ('recruiter', 'Recruiter')
    ]

    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    company_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class':'form-control', 'id': 'id_company_name'})
    )
    company_email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'id': 'id_company_email'})
    )

    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        for fieldname in ['email', 'username', 'password1',
        'password2']:
            self.fields[fieldname].help_text = None
            self.fields[fieldname].widget.attrs.update(
                {'class': 'form-control'}
            )

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
    can_delete=False
)

EducationFormSet = inlineformset_factory(
    Profile,
    Education,
    form=EducationForm,
    extra=1,
    can_delete=False
)

SkillFormSet = inlineformset_factory(
    Profile,
    Skill,
    form=SkillForm,
    extra=1,
    can_delete=False
)

LinkFormSet = inlineformset_factory(
    Profile,
    Link,
    form=LinkForm,
    extra=1,
    can_delete=False
)
