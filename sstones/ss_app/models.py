from django.db import models
from django.urls import reverse, reverse_lazy
from django.contrib.auth.models import User
from django.db import models
from datetime import datetime



class Days(models.Model):
    day = models.DateField()
    closed = models.BooleanField()
    note = models.CharField(max_length=100, null=True)

    def __str__(self):
        return str(self.day)


    #def get_absolute_url(self):
    #    return reverse("ss_app:days")


class Staff(models.Model):
    name = models.CharField(max_length=100)


    def __str__(self):
        return self.name


class TimeSlots(models.Model):
    AVAILABLE_CHOICES = (
        ("B", "Booked"),
        ("C", "Closed"),
        ("O", "Open"),
        ("R", "Requested")
    )
    day = models.ForeignKey(Days,on_delete=models.CASCADE,related_name='slots')
    start_time = models.TimeField()
    end_time = models.TimeField()
    available = models.CharField(max_length=1,choices=AVAILABLE_CHOICES)
    assigned_to = models.ForeignKey(Staff, null=True, on_delete=models.CASCADE)
    comments = models.CharField(max_length=100, null=True)

    def __str__(self):
        return str(self.start_time)[0:5] + " - " + str(self.end_time)[0:5]


    def get_queryset(self,day):
        return self.objects.filter(day=day)


class Event(models.Model):
    name = models.CharField(max_length=100,null=True)
    time = models.ForeignKey(TimeSlots,on_delete=models.CASCADE,null=True)
    date = models.ForeignKey(Days,on_delete=models.CASCADE,null=True)
    note = models.CharField(max_length=100,null=True)
    num_spaces = models.PositiveIntegerField(default=10)

    def __str__(self):
        return self.name


class FocusAreas(models.Model):
    focus_area = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.focus_area

class Client(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, null=True)
    coverage = models.ForeignKey(Staff, on_delete=models.CASCADE, null=True)
    focus_areas = models.ManyToManyField(FocusAreas)

    def __str__(self):
        return self.name


class Appointment(models.Model):
    LOCATIONS=(
                   ("1", "Our Office"),
                   ("2", "Your Office (please include location in comments)"),
                   ("3", "Other (please include location in comments)")
             )

    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True)
    comments = models.TextField(max_length=300, null=True)
    date = models.DateField(null=True)
    time = models.ForeignKey(TimeSlots, on_delete=models.CASCADE, related_name="appt", null=True)
    location = models.TextField(max_length=100, null=True, choices=LOCATIONS)
    message_read = models.BooleanField(default=False)

    def __str__(self):
        return str(self.date) + ' ' + str(self.time)


class Notes(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, null=True)
    note_date = models.DateField(auto_now_add=True)
    items_discussed = models.TextField(null=True)
    follow_ups = models.TextField(null=True)
    paid = models.BooleanField(default=False)

    def __str__(self):
        return  str(self.note_date)
