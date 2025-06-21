from home import views
from django.urls import path

urlpatterns = [
    path('', views.index, name='index'),
    path('signup', views.signup, name='signup'),
    path('signin', views.signin, name='signin'),
    path('logout', views.logout, name='logout'),


    path('manage_schedule', views.manage_schedule, name='manage_schedule'),
    path('create_schedule', views.create_schedule, name='create_schedule'),
    path('message', views.sendmessage, name='sendmessage'),
    path('inbox', views.inbox, name='inbox'),
    path('updatestatus', views.update_schedule_status, name='updatestatus'),
]
