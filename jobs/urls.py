from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='jobs.index'),
    path('recruiter/', views.recruiter_jobs, name='jobs.recruiter'),
    path('create/', views.create_job, name='jobs.create'),
    path('<int:id>/edit/', views.edit_job, name='jobs.edit'),
    path('<int:id>/delete/', views.delete_job, name='jobs.delete'),
    path('<int:id>/', views.show, name='jobs.show'),

    # Shopping cart
    path('cart/', views.cart, name='jobs.cart'),
    path('cart/add/<int:id>/', views.add_to_cart, name='jobs.add_to_cart'),
    path('cart/remove/<int:id>/', views.remove_from_cart, name='jobs.remove_from_cart'),

    path('<int:id>/edit/', views.edit_job, name='jobs.edit'),
    path('<int:id>/delete/', views.delete_job, name='jobs.delete'),
    path('<int:id>/', views.show, name='jobs.show'),
]

