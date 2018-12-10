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
    day = Days.objects.get(day='2018-12-9')
    slot = TimeSlots.objects.get(day=day, start_time = "14:00")
    print (slot.pk)
    appt = Appointment.objects.get(time__pk=slot.pk)

    mail = EmailMessage()
    mail_sub = "Your appointment is confirmed"
            #mail_to = "From: "+ client.name
            #mail_email = "   Email: " + client.email
    mail_msg = appt.client.name + ", " + "Thank you for contacting us. You are confirmed"
    fp = open("C:/Users/John/PythonProjects/sstones/sstones/static/images/ss_logo.jpg", 'rb')
    msg_img = MIMEImage(fp.read())
    fp.close()

    msg_plain = render_to_string('C:/Users/John/PythonProjects/sstones/sstones/templates/email.txt', {'appt': appt})
    msg_html = render_to_string('C:/Users/John/PythonProjects/sstones/sstones/templates/email.html', {'appt': appt})
    send_mail("Your Appointment is confirmed",
    msg_plain,
    "steppingstonetk.gmail.com",
    [appt.client.email],
    html_message=msg_html,
    )





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
