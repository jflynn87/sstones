# Generated by Django 2.0.4 on 2018-11-29 01:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ss_app', '0004_auto_20181129_1042'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='message_read',
            field=models.BooleanField(default=False),
        ),
    ]
