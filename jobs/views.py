from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Job, CartItem, Application
from .forms import JobForm
from django.core.exceptions import PermissionDenied
from functools import wraps
from django.contrib import messages

# Create your views here.

#Recruiter:

def is_recruiter(user):
    return user.is_superuser or (getattr(user, 'profile', None) and user.profile.role == 'recruiter')

def recruiter_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        profile = getattr(request.user, 'profile', None)
        if not is_recruiter(request.user):
            messages.error(request, 'Must be a Recruiter to access this page')
            return redirect('jobs.index')
        return view_func(request, *args, **kwargs)
    return wrapper


@recruiter_required
def recruiter_jobs(request):
    jobs = request.user.jobs.all()

    return render(
        request, 
        'jobs/recruiter_jobs.html',
        {'title' : 'Job Postings',
         'jobs': jobs}
    )

@recruiter_required
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



@recruiter_required
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

@recruiter_required
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

@login_required
def cart(request):
    cart_items = CartItem.objects.filter(
        user=request.user
    ).select_related('job')

    for item in cart_items:
        item.skills_list = [
            skill.strip()
            for skill in item.job.skills.split(',')
            if skill.strip()
        ]

    return render(request, 'jobs/cart.html', {
        'cart_items': cart_items
    })


@login_required
def add_to_cart(request, id):
    job = get_object_or_404(Job, id=id)

    if request.method == 'POST':
        CartItem.objects.get_or_create(
            user=request.user,
            job=job
        )

    return redirect('jobs.cart')


@login_required
def remove_from_cart(request, id):
    cart_item = get_object_or_404(
        CartItem,
        user=request.user,
        job_id=id
    )

    if request.method == 'POST':
        cart_item.delete()

    return redirect('jobs.cart')

@login_required
def apply(request, id):
    if request.method == 'POST':
        job = Job.objects.get(id=id)
        application = Application()
        application.note = request.POST['note']
        application.job = job
        application.user = request.user
        application.save()
    return redirect('jobs.show', id=id)
