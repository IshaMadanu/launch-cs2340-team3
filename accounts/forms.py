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
        model = Profile
        fields = [
            "first_name", "last_name", "name_visible",
            "profile_picture", "picture_visible",
            "headline", "headline_visible",
            "bio",
            "location", "location_visible",
        ]
        widgets = {
            "headline": forms.Textarea(attrs={
                "rows": 4,
                "placeholder": "CS Student @ Georgia Tech interested in AI and Robotics",
            }),
            "location": forms.TextInput(attrs={"placeholder": "City, State"}),
        }
 
 
class WorkExperienceForm(forms.ModelForm):
    class Meta:
        model = WorkExperience
        fields = ["company", "title", "dates", "description", "visible"]
        labels = {"description": "Notes"}
        widgets = {
            "dates": forms.TextInput(attrs={"placeholder": "September 2025 - Present"}),
            "description": forms.Textarea(attrs={"rows": 3}),
        }
 
 
class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = ["institution", "dates", "notes", "visible"]
        labels = {"institution": "School"}
        widgets = {
            "dates": forms.TextInput(attrs={"placeholder": "August 2025 - December 2028"}),
            "notes": forms.Textarea(attrs={"rows": 2}),
        }
 
 
class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ["name", "skills_visible"]
 
 
class LinkForm(forms.ModelForm):
    class Meta:
        model = Link
        fields = ["url", "visible"]
 
 
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