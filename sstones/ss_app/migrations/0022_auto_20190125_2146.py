# Generated by Django 2.0.4 on 2019-01-25 12:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ss_app', '0021_auto_20190125_2110'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='principal',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='tax',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='total',
            field=models.IntegerField(),
        ),
    ]