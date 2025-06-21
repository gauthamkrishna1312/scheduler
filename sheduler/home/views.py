from datetime import datetime
from django.shortcuts import render
from django.contrib.auth.models import auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.utils.timezone import localtime
from .models import Shedule, Message
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Shedule,User
from django.core.mail import send_mail
from urllib.parse import urlencode, quote
from django.conf import settings
from datetime import datetime
# Create your views here.
@login_required(login_url='signin')
def send_schedule_email(schedule):
    user_email = schedule.user.email
    start = localtime(schedule.start_time).strftime('%Y%m%dT%H%M%SZ')
    end = localtime(schedule.end_time).strftime('%Y%m%dT%H%M%SZ')

    title = schedule.title
    department = schedule.department or 'Not specified'
    description = f"Department: {department}\nTitle: {title}"
    
    # Construct the Google Calendar link
    params = {
        "action": "TEMPLATE",
        "text": title,
        "dates": f"{start}/{end}",
        "details": f"{description}\n\nClick to add this schedule to your calendar.",
    }
    google_calendar_link = "https://www.google.com/calendar/render?" + urlencode(params, quote_via=quote)

    # Compose the email message
    message = f"""
        Hi {schedule.user.username},

        You have a new schedule update.

        📌 Title: {title}
        🕒 Start Time: {schedule.start_time}
        🕔 End Time: {schedule.end_time}
        🏢 Department: {department}

        Click below to add this to your Google Calendar:
        {google_calendar_link}

        Regards,
        Your Scheduler App
        """
    send_mail(
        subject="📅 New Schedule Notification",
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user_email],
        fail_silently=False,
    )

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

                start = timezone.make_aware(datetime.fromisoformat(start_time))
                end = timezone.make_aware(datetime.fromisoformat(end_time))

                # start = datetime.fromisoformat(start_time)
                # end = datetime.fromisoformat(end_time)

                # Check if end time is before start time
                if end <= start:
                    messages.error(request, 'End time must be after start time.')
                    return redirect('manage_schedule')

                schedule.title = title
                schedule.department = department
                schedule.start_time = start
                schedule.end_time = end

                if user_id:
                    schedule.user = User.objects.get(id=user_id)

                schedule.save()
                send_schedule_email(schedule)# Notify user about the update
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
        start = timezone.make_aware(datetime.fromisoformat(start_time))
        end = timezone.make_aware(datetime.fromisoformat(end_time))


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
        new_schedule = Shedule.objects.create(
            user=user,
            title=title,
            department=department,
            start_time=start,
            end_time=end
        )
        send_schedule_email(new_schedule)
        messages.success(request, 'Schedule created successfully!')
        return redirect('manage_schedule')

    users = User.objects.all()
    return render(request, 'manage_schedule.html', {'users': users})


@login_required(login_url='signin')
def index(request):
    current_datetime = timezone.now()
    shedule = Shedule.objects.filter(user=request.user).order_by('start_time')
    users = User.objects.all()
    unread_count = 0

    if request.user.is_superuser:
        unread_count = Message.objects.filter(read=False).count()


    context = {
        'shedule': shedule,
        'username': request.user.username, 
        'users': users if request.user.is_superuser else None , # Show users only to superusers
        'unread_count': unread_count, 
    }

    return render(request, 'index.html', context)

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


@login_required(login_url='signin')
def inbox(request):

    sended_user = Message.objects.filter(sender=request.user).order_by('-sent_at')
    message = Message.objects.all().order_by('-sent_at')

    if request.method == 'POST' and request.user.is_superuser:
        if 'delete_message' in request.POST:
            message_id = request.POST.get('message_id')
            try:
                Message.objects.get(id=message_id).delete()
            except Message.DoesNotExist:
                pass

        elif 'clear_all' in request.POST:
            Message.objects.all().delete()

        elif 'toggle_read' in request.POST:
            message_id = request.POST.get('message_id')
            try:
                msg = Message.objects.get(id=message_id)
                msg.read = not msg.read
                msg.save()
            except Message.DoesNotExist:
                pass

        return redirect('inbox')
    context = {
        'sended_user': sended_user,
        'message': message,
    }
  
    return render(request, 'inbox.html', context)


@login_required(login_url='signin')
def update_schedule_status(request):
    now = timezone.now()
    for schedule in Shedule.objects.all():
        if schedule.start_time > now:
            schedule.status = 'pending'
        elif schedule.start_time <= now <= schedule.end_time:
            schedule.status = 'active'
        elif schedule.end_time < now:
            schedule.status = 'expired'
        schedule.save()
    return redirect('/')



@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('signin') 


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