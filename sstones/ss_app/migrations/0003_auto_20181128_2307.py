# Generated by Django 2.0.4 on 2018-11-28 14:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ss_app', '0002_auto_20181128_2206'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='client',
            name='focus_areas',
        ),
        migrations.AddField(
            model_name='client',
            name='focus_areas',
            field=models.ManyToManyField(null=True, to='ss_app.FocusAreas'),
        ),
    ]