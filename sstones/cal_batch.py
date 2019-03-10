import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","sstones.settings")

from dotenv import load_dotenv
project_folder = os.path.expanduser('~')
load_dotenv(os.path.join(project_folder, '.env'))

SECRET_KEY = os.environ['SECRET_KEY']

import django
django.setup()
import manage_cal


if __name__ == '__main__':
    print ('starting calendar')
    manage_cal.setup_cal()
    #create_groups()

    print ("complete")
