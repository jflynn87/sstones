from django.db import models
from django.urls import reverse, reverse_lazy
from django.contrib.auth.models import User
from django.db import models
from datetime import datetime



class Days(models.Model):
    day = models.DateField(unique=True)
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
    assigned_to = models.ForeignKey(Staff, on_delete=models.CASCADE)
    comments = models.CharField(max_length=100, null=True)
    cal_event_id = models.CharField(max_length=256, null=True)
    created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return str(self.start_time)[0:5] + " with " + str(self.assigned_to)


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


class Package(models.Model):
    name = models.CharField(max_length=256)
    type = models.CharField(max_length=30)
    num_of_sessions = models.PositiveIntegerField()
    mtg_duration = models.CharField(max_length=30)
    price = models.PositiveIntegerField()

    def __str__(self):
        return self.name

class Client(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, null=True)
    coverage = models.ForeignKey(Staff, on_delete=models.CASCADE, null=True)
    focus_areas = models.ManyToManyField(FocusAreas)
    package = models.ForeignKey(Package, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name


class Appointment(models.Model):
    LOCATIONS=(
                   ("1", "Stepping Stones Office"),
                   ("2", "Another Location (please include location in comments)"),

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
    #paid = models.BooleanField(default=False)

    def __str__(self):
        return  str(self.note_date)


class Invoice(models.Model):
    STATUS =(
        ("1", "Issued"),
        ("2", "Paid")
    )

    number = models.PositiveIntegerField(unique=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    package = models.ForeignKey(Package, on_delete=models.CASCADE, null=True)
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, blank=True, null=True)
    status = models.CharField(max_length=30, choices=STATUS)
    inv_date = models.DateField()
    principal = models.IntegerField()
    tax = models.IntegerField()
    total = models.IntegerField()
    note = models.CharField(max_length=1000, blank=True)

    def __str__(self):
        return str(self.inv_date) + ": " + str(self.client)

class Receipt(models.Model):
    number = models.PositiveIntegerField(unique=True)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    paid_date = models.DateField()

    def __str__(self):
        return str(self.number)

class Task(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=3000)
    closed = models.BooleanField(default=False)
    create_date = models.DateField(auto_now_add=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name
