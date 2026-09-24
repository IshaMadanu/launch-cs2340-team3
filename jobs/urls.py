from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='jobs.index'),
    path('recruiter/', views.recruiter_jobs, name='jobs.recruiter'),
    path('create/', views.create_job, name='jobs.create'),
    path('<int:id>/edit/', views.edit_job, name='jobs.edit'),
    path('<int:id>/delete/', views.delete_job, name='jobs.delete'),
    path('<int:id>/', views.show, name='jobs.show'),
]

