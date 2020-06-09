import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","sstones.settings")

#from dotenv import load_dotenv
#project_folder = os.path.expanduser('~')
#load_dotenv(os.path.join(project_folder, '.env'))

#SECRET_KEY = os.environ['SECRET_KEY']

import django
django.setup()

from ss_app.models import Days, TimeSlots, Staff, Appointment
from django.core.mail import send_mail
import datetime
from django.db.models import Max

from ss_app import update_ss_cal

update_ss_cal.setup_cal()

