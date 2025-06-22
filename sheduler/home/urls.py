from django.contrib.auth import views as auth_views
from home import views
from django.urls import path


urlpatterns = [
    path('', views.index, name='index'),
    path('signup', views.signup, name='signup'),
    path('signin', views.signin, name='signin'),
    path('login', views.signin, name='login'), #Password reset uses 'login' as the URL for the login page
    path('logout', views.logout, name='logout'),


    path('manage_schedule', views.manage_schedule, name='manage_schedule'),
    path('create_schedule', views.create_schedule, name='create_schedule'),
    path('message', views.sendmessage, name='sendmessage'),
    path('inbox', views.inbox, name='inbox'),
    path('updatestatus', views.update_schedule_status, name='updatestatus'),
    
    

    # Password reset flow
    path('password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('password_base', views.password_base, name='password_base'),

]
