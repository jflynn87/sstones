# Generated by Django 2.0.4 on 2019-03-21 11:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ss_app', '0022_auto_20190125_2146'),
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=3000)),
                ('closed', models.BooleanField(default=False)),
                ('create_date', models.DateField(auto_now_add=True)),
                ('client', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='ss_app.Client')),
            ],
        ),
    ]