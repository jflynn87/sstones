import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","sstones.settings")

import django
django.setup()

from ss_app.models import Days, TimeSlots, Staff


import datetime


def setup_cal():
    '''adds a new day and time slots to the calendar.'''

    start_time = '9:00'
    end_time = '20:00'
    slot_time = 60

    # Start date from today to next 5 day
    start = Days.objects.latest('day')
    start_date = start.day
    print ('start', start_date)
    end_date = datetime.datetime.now().date() + datetime.timedelta(days=180)
    print ('end', end_date)
    #start_date = datetime.datetime.now().date()
    #end_date = datetime.datetime.now().date() + datetime.timedelta(days=180)

    days = {}
    date = start_date

    while date <= end_date:

        #if date.weekday() != 7:
            hours = []
            time = datetime.datetime.strptime(start_time, '%H:%M')
            end = datetime.datetime.strptime(end_time, '%H:%M')
            while time <= end:
                #if date.weekday() not in [6]:
                    hours.append(time.strftime("%H:%M"))
                    days[str(date)]=hours
                    time += datetime.timedelta(minutes=slot_time)
                    date += datetime.timedelta(days=1)
                #else:
                #    date += datetime.timedelta(days=1)


    for day, times in days.items():

        days = Days()
        days.day = day

        if datetime.datetime.strptime(day, '%Y-%m-%d').weekday() == 6:
            days.closed = True
        else:
            days.closed = False
        days.save()

        #staff = Staff.objects.get(name="Unassigned")

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

                #slots.objects.get_or_create(day=days,start_time=time,end_time='a',open=True)
                slots.save()






setup_cal()
