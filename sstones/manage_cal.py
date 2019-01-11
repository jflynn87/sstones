import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","sstones.settings")

from dotenv import load_dotenv
project_folder = os.path.expanduser('~')
load_dotenv(os.path.join(project_folder, '.env'))

SECRET_KEY = os.environ['SECRET_KEY']

import django
django.setup()

from ss_app.models import Days, TimeSlots, Staff, Appointment
from django.core.mail import send_mail
import datetime

def setup_cal():
    '''adds a new day and time slots to the calendar.  Deletes old days
        where there were no meetings'''

    start_time = '9:00'
    end_time = '20:00'
    slot_time = 60

    # Start date from today to next 5 day
    start = Days.objects.latest('day')
    start_date = start.day + datetime.timedelta(days=1)
    print ('start date(max date + 1)', start_date)
    end_date = datetime.datetime.now().date() + datetime.timedelta(days=180)
    print ('end (new date)', end_date)

    days = {}
    date = start_date

    while date <= end_date:

            hours = []
            time = datetime.datetime.strptime(start_time, '%H:%M')
            end = datetime.datetime.strptime(end_time, '%H:%M')
            while time <= end:
                    hours.append(time.strftime("%H:%M"))
                    days[str(date)]=hours
                    time += datetime.timedelta(minutes=slot_time)
                    date += datetime.timedelta(days=1)

    add_day_list = []
    for day, times in days.items():

        days = Days()
        days.day = day

        if datetime.datetime.strptime(day, '%Y-%m-%d').weekday() == 6:
            days.closed = True
        else:
            days.closed = False
        add_day_list.append(days.day)
        print ("saving day: ", days.day)
        days.save()

        for time in times:
            for person in Staff.objects.all():
                slots = TimeSlots()
                slots.day = days
                slots.start_time = time
                end_time = datetime.datetime.strptime(time, '%H:%M')
                end_time += datetime.timedelta(minutes=50)
                slots.end_time = end_time
                slots.available = "O"
                slots.assigned_to = person
                slots.save()

    old_dates = Days.objects.filter(day__lt=datetime.datetime.today())

    keep_days_list = []
    del_days_list = []
    for date in old_dates:
        if Appointment.objects.filter(date=date.day).exists():
            print ('keep day', date)
            keep_days_list.append(date)
        else:
            print ('delete day', date)
            del_days_list.append(date)
            Days.objects.get(pk=date.pk).delete()

    check_sum = (TimeSlots.objects.all().count() / Days.objects.all().count())

    #12 slots a day, 2 staff so should = 24
    if check_sum == 24:
        msg = "Dates and slots look good"
    else:
        msg = "Looks like an issue with the number of slots, not checking out"

    mail_sub = "SS dates updated"
    mail_content = "Summary of updates from date process: " + "\r" \
    "start date: " + str(start_date)  + "\r" \
    "end date: " + str(end_date) + "\r" \
    "added dates: " + str(add_day_list) + "\r" \
    "keep days: " + str(keep_days_list)  + "\r" \
    "deleted days: " + str(del_days_list) + "\r" \
    + msg

    mail_recipients = ['jflynn87@hotmail.com']
    send_mail(mail_sub, mail_content, 'steppingstonetk.gmail.com', mail_recipients)  #add fail silently

setup_cal()
