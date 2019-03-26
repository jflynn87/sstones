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
from django.db.models import Max

def setup_cal(new_date=None):
    '''option to pass in a date to create or not.  If no date passed in, adds
    dates new days up to 6 months from todat.  Creates time slots  for new
    days and deletes old days with no meetings.'''

    print ('new_date', new_date)
    open_time = '09:00'
    close_time = '20:00'
    slot_time = 60

    if new_date != None:
        start_date = datetime.datetime.strptime(new_date, '%Y-%m-%d').date()
        end_date = datetime.datetime.strptime(new_date, '%Y-%m-%d').date()
    else:
        start_date = datetime.datetime.now().date()
        print ('start date(today)', start_date)
        end_date = datetime.datetime.now().date() + datetime.timedelta(days=180)
        print ('end (new date)', end_date)

    date = start_date
    add_day_list = []

    while date <= end_date:
      if not Days.objects.filter(day=date).exists():
        hours = []
        time = datetime.datetime.strptime(open_time, '%H:%M')
        end = datetime.datetime.strptime(close_time, '%H:%M')
        while time <= end:
            hours.append(time.strftime("%H:%M"))
            time += datetime.timedelta(minutes=slot_time)

        days = Days()
        days.day = date

        if date.weekday() == 6:
            days.closed = True
        else:
            days.closed = False

        print ("saving day: ", days.day)
        days.save()
        add_day_list.append(days)

        for time in hours:
            for person in Staff.objects.filter(bookable=True):
                slots = TimeSlots()
                slots.day = days
                slots.start_time = time
                end_time = datetime.datetime.strptime(time, '%H:%M')
                end_time += datetime.timedelta(minutes=50)
                slots.end_time = end_time
                slots.available = "O"
                slots.assigned_to = person
                slots.save()
                print ('saving slot', slots)

      date += datetime.timedelta(days=1)

    if new_date == None:
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

        #12 slots a day, 2 staff so should = 24  Update to calculate automatically from staff len and hours
        if check_sum == 24:
            msg = "Dates and slots look good"
            print (msg)
        else:
            for day in Days.objects.all():
                count = TimeSlots.objects.filter(day=day).count()
                if count != 24:
                    print ('bad day and slot count', day.day, count)
            print (check_sum)
            msg = "Looks like an issue with the number of slots, check logs for bad dates"

        mail_sub = "SS dates updated"
        mail_content = "Summary of updates from date process: " + "\r" \
        "start date (today or passed day): " + str(start_date)  + "\r" \
        "today + 180 days: " + str(end_date) + "\r" \
        "added dates: " + str(add_day_list) + "\r" \
        "keep days: " + str(keep_days_list)  + "\r" \
        "deleted days: " + str(del_days_list) + "\r" \
        + msg

        mail_recipients = ['jflynn87@hotmail.com']
        send_mail(mail_sub, mail_content, 'steppingstonetk.gmail.com', mail_recipients)  #add fail silently

setup_cal()
