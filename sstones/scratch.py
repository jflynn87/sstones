import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","sstones.settings")

import django
django.setup()

from ss_app.models import TimeSlots, Appointment, Days
from django.db.models import Q, Count
from django.core.mail import send_mail, EmailMultiAlternatives, EmailMessage
from django.template.loader import render_to_string
from email.mime.image import MIMEImage

def run():

        #day = "2018-12-20"
        #if TimeSlots.objects.filter(day__day=day, available__in=['B', 'R']).exists():
            slot  = TimeSlots.objects.filter(available__in=['B', 'R']).annotate(count=Count('available')).values('day__day', 'count')

        #date = slot['day__day']
            print ('slot', slot)
            print (slot[0].get('count'))
            print (slot[0].get('day__day'))
            # for slot in time_slots:
            #     if Appointment.objects.filter(time__pk=slot.pk).exists():
            #         print ('found', slot)
            #     #if slot.available == "O":
                #    slot_list.append(slot)
                #else:
                #    slots = ''



    #these were commented            #msg = EmailMessage(mail_content, 'steppingstonetk.gmail.com',['steppingstonetk@gmail.com'],['jflynn87@hotmail.com'])
    #these were commented            #mail_recipients = ['steppingstonetk@gmail.com'],['jflynn87@hotmail.com'], ['jrc7825@gmail.com']


            #these work
    #mail_recipients = [appt.client.email]
    #print (appt.client.email)
    #email = EmailMultiAlternatives(mail_sub, mail_msg, 'steppingstonetk.gmail.com', mail_recipients)
    #email.content_type = "html"
    #email.mixed_subtype = "related"

    #msg_img.add_header('Content-ID', 'msg_img')
    #email.attach(msg_img)

    #email.send()
    #send_mail(mail_sub, mail_content, 'steppingstonetk.gmail.com', mail_recipients)  #add fail silently
run()
