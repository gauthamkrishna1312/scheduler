from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from home.models import Shedule,User
from django.utils.timezone import localtime
# Create your views here.

@login_required(login_url='signin')
def weekly_gantt(request):
    schedules = Shedule.objects.select_related('user').all()
    chart_data = []
    department_colors = {
            'Reception': 'red',
            'Pricing/Marketing': 'blue',
            'Monitoring/Inspection': 'green',
            'Bookkeeping': 'orange',
            'Sales/Customer Service': 'yellow',
        }

    for schedule in schedules:
        start_str = localtime(schedule.start_time).strftime('%H:%M')
        end_str = localtime(schedule.end_time).strftime('%H:%M')
        
        # Day of week (e.g., 'Monday')
        day = localtime(schedule.start_time).strftime('%A')

        # Employee name
        employee_name = schedule.user.get_full_name() or schedule.user.username

        # Department color map (define it as needed)
        color = department_colors.get(schedule.department, 'gray')

        # Append bar info for Gantt chart
        chart_data.append({
            'x': [start_str, end_str],
            'y': [f'{day} - {employee_name}'],
            'name': schedule.department or "Other",
            'text': [employee_name],
            'color': color,
        })

    context = {
        'chart_data': chart_data,
        'has_schedules': bool(schedules)
        }
    return render(request, 'gantt/base.html', context)

