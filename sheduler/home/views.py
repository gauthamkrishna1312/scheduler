from datetime import datetime
from django.shortcuts import render
from django.contrib.auth.models import auth
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Shedule, Message
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Shedule,User
# Create your views here.



@user_passes_test(lambda u: u.is_superuser, login_url='signin')
def manage_schedule(request):
    if request.method == 'POST':
        schedule_id = request.POST.get('schedule_id')
        action = request.POST.get('action')

        try:
            schedule = Shedule.objects.get(id=schedule_id)
            if action == 'delete':
                schedule.delete()
                messages.success(request, 'Schedule deleted successfully!')
                return redirect('manage_schedule')

            elif action == 'update':
                title = request.POST['title']
                department = request.POST.get('department', '')
                start_time = request.POST['start_time']
                end_time = request.POST['end_time']
                user_id = request.POST.get('user_id')

                start = datetime.fromisoformat(start_time)
                end = datetime.fromisoformat(end_time)

                # Check if end time is before start time
                if end <= start:
                    messages.error(request, 'End time must be after start time.')
                    return redirect('manage_schedule')

                schedule.title = title
                schedule.department = department
                schedule.start_time = start_time
                schedule.end_time = end_time

                if user_id:
                    schedule.user = User.objects.get(id=user_id)

                schedule.save()
                messages.success(request, 'Schedule updated successfully!')
                return redirect('manage_schedule')

        except Shedule.DoesNotExist:
            messages.error(request, 'Schedule not found.')

        return redirect('manage_schedule')

    # 🟢 Pass all users for dropdown
    users = User.objects.all()
    schedules = Shedule.objects.all().order_by('start_time')

    return render(request, 'manage_schedule.html', {
        'schedules': schedules,
        'users': users
    })


@user_passes_test(lambda u: u.is_superuser, login_url='signin')
def create_schedule(request):
    if request.method == 'POST':
        title = request.POST['title']
        department = request.POST.get('department', '')
        start_time = request.POST['start_time']
        end_time = request.POST['end_time']
        user_id = request.POST['user_id']

        # Parse datetime strings to Python datetime objects
        start = datetime.fromisoformat(start_time)
        end = datetime.fromisoformat(end_time)

        # Check if end time is before start time
        if end <= start:
            messages.error(request, 'End time must be after start time.')
            return redirect('manage_schedule')

        # Proceed with creation if validation passes
        user = User.objects.get(id=user_id)
        Shedule.objects.create(
            user=user,
            title=title,
            department=department,
            start_time=start_time,
            end_time=end_time
        )
        messages.success(request, 'Schedule created successfully!')
        return redirect('manage_schedule')

    users = User.objects.all()
    return render(request, 'manage_schedule.html', {'users': users})


@login_required(login_url='signin')
def index(request):
    current_datetime = timezone.now()
    shedule = Shedule.objects.filter(user=request.user).order_by('start_time')
    users = User.objects.all()

    context = {
        'shedule': shedule,
        'username': request.user.username,
        'users': users if request.user.is_superuser else None
    }

    return render(request, 'index.html', context)


@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('signin') 

@login_required(login_url='signin')
def sendmessage(request):
    if request.method == 'POST':

        sender = request.user
        subject = request.POST['subject']
        body = request.POST['body']

        Message.objects.create(
            sender=sender,
            subject=subject,
            body=body
        )
        messages.success(request, 'Message sent successfully!')
        return redirect('sendmessage')

    return render(request, 'sendmessage.html')




def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2 :
            if User.objects.filter(email = email).exists():
                messages.info(request, 'E mail already exist')
                return render(request, 'signup.html')
            elif User.objects.filter(username = username).exists():
                messages.info(request, 'Username already exist')
                return render(request, 'signup.html')
            else :
                user = User.objects.create_user(username = username, email=email, password=password)
                user.save()
                return redirect('/')
        else :
            messages.info(request, 'Password Not Matching')
            return redirect('signup')
    else :
        return render(request, 'signup.html')

def signin(request):
    if request.method == 'POST' :
        usernameU = request.POST.get('username')
        passwordP = request.POST.get('password')

        user = auth.authenticate(username=usernameU, password=passwordP)

        if user is not None :
            auth.login(request, user)
            return redirect('/') 
        else :
            messages.info(request, 'Username or Password is unmatching')
            return redirect('signin') 
    else :
        return render(request, 'signin.html')