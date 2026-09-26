from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Job, CartItem, Application
from accounts.models import Profile
from .forms import JobForm
from django.core.exceptions import PermissionDenied
from functools import wraps
from django.contrib import messages
from django.db.models import Q
from django.conf import settings

# Create your views here.

#Recruiter:

def is_recruiter(user):
    return user.is_superuser or (getattr(user, 'account', None) and user.account.role == 'recruiter')

def recruiter_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        account = getattr(request.user, 'account', None)
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
def job_applicants(request, id):
    job = get_object_or_404(Job, id=id, recruiter=request.user)

    applications = (
        Application.objects
        .filter(job=job)
        .select_related('user', 'user__profile')
    )

    return render(request, 'jobs/job_applicants.html', {
        'job': job,
        'applications': applications,
    })


@recruiter_required
def applicant_detail(request, id, application_id):
    application = get_object_or_404(
        Application.objects.select_related('user', 'user__profile'),
        id=application_id,
        job__id=id,
        job__recruiter=request.user,
    )

    return render(request, 'jobs/applicant_detail.html', {
        'application': application,
        'profile': application.user.profile,
    })    

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
    jobs = Job.objects.all()

    search = request.GET.get('search', '')
    location = request.GET.get('location', '')
    min_salary = request.GET.get('min_salary', '')
    max_salary = request.GET.get('max_salary', '')
    work_type = request.GET.get('work_type', '')
    visa = request.GET.get('visa', '')

    if search:
        jobs = jobs.filter(
            Q(title__icontains=search) |
            Q(skills__icontains=search)
        )

    if location:
        jobs = jobs.filter(location__icontains=location)

    if min_salary:
        jobs = jobs.filter(salary__gte=min_salary)

    if max_salary:
        jobs = jobs.filter(salary__lte=max_salary)

    if work_type:
        jobs = jobs.filter(work_type=work_type)

    if visa == 'yes':
        jobs = jobs.filter(visa_sponsorship=True)
    elif visa == 'no':
        jobs = jobs.filter(visa_sponsorship=False)

    template_data = {
        'title': 'Jobs',
        'jobs': jobs,
    }

    return render(request, 'jobs/index.html', {
        'template_data': template_data
    })

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

@recruiter_required
def candidate_search(request):
    """
    Lets a recruiter search candidate profiles by skill, headline,
    bio, work experience, or education.
    """
    query = request.GET.get("q", "").strip()

    results = Profile.objects.all()

    if query:
        results = results.filter(
            Q(skills__name__icontains=query)
            | Q(headline__icontains=query)
            | Q(bio__icontains=query)
            | Q(work_experiences__company__icontains=query)
            | Q(work_experiences__description__icontains=query)
            | Q(educations__institution__icontains=query)
        )

    results = (
        results
        .distinct()
        .prefetch_related(
            "skills",
            "educations",
            "work_experiences",
        )
    )

    return render(
        request,
        "jobs/candidate_search.html",
        {
            "query": query,
            "results": results,
        },
    )

def job_map(request):
    jobs = Job.objects.all()

    return render(request, 'jobs/map.html', {
        'jobs': jobs,
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY,
    })
