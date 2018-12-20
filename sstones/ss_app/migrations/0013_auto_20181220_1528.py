# Generated by Django 2.0.4 on 2018-12-20 06:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ss_app', '0012_auto_20181219_1851'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='location',
            field=models.TextField(choices=[('1', 'Stepping Stones Office'), ('2', 'Another Location (please include location in comments)')], max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='days',
            name='day',
            field=models.DateField(unique=True),
        ),
    ]
