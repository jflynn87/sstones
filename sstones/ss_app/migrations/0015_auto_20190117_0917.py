# Generated by Django 2.0.4 on 2019-01-17 00:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ss_app', '0014_auto_20190116_1336'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='amount',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='invoice',
            name='status',
            field=models.CharField(choices=[('1', 'Issued'), ('2', 'Paid')], max_length=30),
        ),
    ]