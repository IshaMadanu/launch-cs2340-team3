from django import forms
from .models import Job

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'salary', 'skills', 'location', 'description', 'image', 'work_type', 'visa_sponsorship']