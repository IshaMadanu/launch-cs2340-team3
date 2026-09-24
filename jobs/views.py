from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Job
from .forms import JobForm

# Create your views here.

#Recruiter:

@login_required
def recruiter_jobs(request):
    jobs = request.user.jobs.all()

    return render(
        request, 
        'jobs/recruiter_jobs.html',
        {'title' : 'Job Postings',
         'jobs': jobs}
    )

@login_required
def create_job(request):
    if request.method == 'POST':
        form = JobForm(request.POST, request.FILES)

        if form.is_valid():
            job = form.save(commit=False)
            job.recruiter = request.user
            job.save()
            return redirect('jobs.recruiter')
    else: 
        form = JobForm() 
        jobs = Job.objects.all()
    return render(request, 'jobs/job_form.html', {
        'jobs': jobs,
        'form' : form,
        'page_title': 'Post a Job',
        'editing': False,
    })



@login_required
def edit_job(request, id):
    job = get_object_or_404(Job, id=id, recruiter=request.user)

    if request.method == 'POST':
        form = JobForm(request.POST, request.FILES, instance=job)

        if form.is_valid():
            form.save()
            return redirect('jobs.index')

    else:
        form = JobForm(instance=job)

    jobs = Job.objects.all()

    return render(request, 'jobs/job_form.html', {
        'jobs': jobs,
        'form': form,
        'editing': True,
    })

@login_required
def delete_job(request, id):
    job = get_object_or_404(Job, id=id, recruiter=request.user)

    if request.method == 'POST':
        job.delete()

    return redirect('jobs.recruiter')

#Both:

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