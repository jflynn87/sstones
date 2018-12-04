import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","sstones.settings")

import django
django.setup()

from ss_app.models import TimeSlots, Appointment, Days
from django.db.models import Q, Count

def run():
    date = '2018-11-29'
    #staff_cnt = 2
    #slot_list = []
    appts = Appointment.objects.all()

    for apt in appts:
        print (apt.time.pk)
    time_slots = TimeSlots.objects.filter(day=Days.objects.get(day=date))
    for slot in time_slots:
        print (slot, slot.start_time, slot.pk)
        #if slot.available == "O":
        #    slot_list.append(slot)
        #elif TimeSlots.objects.filter(day=Days.objects.get(day=date), start_time=slot.start_time, available__in=('B', 'R')).count() < staff_cnt:
        #    slot_list.append(slot)

    #print (slot_list)

run()
