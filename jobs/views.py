from django.shortcuts import render
from .models import Job

# Create your views here.

def index(request):
    template_data = {}
    template_data['title'] = 'Jobs'
    template_data['jobs'] = Job.objects.all()
    return render(request, 'jobs/index.html',
                  {'template_data': template_data})

def show(request, id):
    job = Job.objects.get(id=id)
    template_data = {}
    template_data['title'] = job.title
    template_data['job'] = job
    return render(request, 'jobs/show.html',
                  {'template_data': template_data})