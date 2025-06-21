from django.urls import path
from . import views

urlpatterns = [
    path('chart/', views.weekly_gantt, name='weekly_gantt'),
]