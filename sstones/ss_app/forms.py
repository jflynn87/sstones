from django import forms
from django.forms import ModelForm, MultipleChoiceField
from .models import Days, TimeSlots, Event, Appointment, Staff, Client, Notes,\
                FocusAreas, Package, Invoice, Receipt
import datetime
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.forms.models import modelformset_factory
from django.forms.formsets import BaseFormSet
from django.forms import inlineformset_factory
import ss_app.views
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User


from django.utils.safestring import mark_safe
from django.db.models import Max
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import send_mail
import manage_cal


class CalUpdateForm(forms.ModelForm):

    class Meta:
        model = Days
        fields = ['day', 'closed', 'note']


    def __init__(self, *args, **kwargs):
         super(CalUpdateForm, self).__init__(*args,**kwargs)
         self.fields['day'].widget.attrs['readonly']=True
         self.fields['day'].widget.attrs['size']= '11'
         self.fields['day'].widget.attrs['style']= 'border: 0px solid'
         self.fields['note'].required = False


CalUpdateFormSet = modelformset_factory(Days, form=CalUpdateForm, extra=0)

class SlotsForm(forms.ModelForm):

      CHOICES=(
            ("B", "Booked"),
            ("C", "Closed"),
            ("O", "Open"),
            ("R", "Requested")
                )

      class Meta:
          model = TimeSlots
          fields = ['day', 'start_time', 'end_time', 'available', 'assigned_to', 'comments']
          widgets = {
            'start_time': forms.TimeInput(format="%H:%M"),
            'end_time': forms.TimeInput(format="%H:%M")
          }

      def __init__(self, *args, **kwargs):
           super(SlotsForm, self).__init__(*args,**kwargs)
           self.fields['comments'].required = False
           self.fields['assigned_to'].required = False
           self.fields['available'].required = False
           self.fields['day'].required = False
           self.fields['start_time'].widget.attrs['readonly']=True
           self.fields['end_time'].widget.attrs['readonly']=True
           self.fields['assigned_to'].widget.attrs['disabled']=True
           self.fields['start_time'].widget.attrs['size']= '6'
           self.fields['start_time'].widget.attrs['style']= 'border: 0px solid'
           self.fields['end_time'].widget.attrs['size']= '6'
           self.fields['end_time'].widget.attrs['style']= 'border: 0px solid'


SlotsFormSet = modelformset_factory(TimeSlots, SlotsForm, extra=0 )

class SimpleApptform(ModelForm):

    class Meta:
        model=Appointment
        fields= '__all__'
        widgets = {'date': forms.TextInput({}),
                    'time': forms.Select(attrs= {}),
                    'comments': forms.Textarea(attrs= {'rows':3, 'cols':50, 'style': 'width: 100%'}),
                    }


class AppointmentForm(ModelForm):

    class Meta:
         model=Appointment
         fields=['comments', 'date', 'time', 'location']
         widgets = {'date': forms.TextInput({}),
                    'time': forms.Select(attrs= {}),
                    'comments': forms.Textarea(attrs= {'rows':3, 'cols':50, 'style': 'width: 100%'}),
                    }

    def __init__(self, *args, **kwargs):
#        print ('appt form init', kwargs)
#        self.request = kwargs.pop('request')
#        print (self.request)
#        if kwargs.get('user') != None:
#            self.user = kwargs.pop('user')
#        else:
#            self.user = None
        super(AppointmentForm, self).__init__(*args, **kwargs)
        if not kwargs.get('instance'):
            self.fields['time'].queryset = TimeSlots.objects.none()
        else:
            appt = Appointment.objects.get(pk=self.instance.pk)
            day = Days.objects.get(day=appt.date)
            slots = TimeSlots.objects.filter(day=day)

            self.fields['time'].queryset = TimeSlots.objects.filter(day=day)
            #self.initial['time'] = TimeSlots.objects.get(pk=self.instance.time.pk)
        self.fields['date'].required = False
        self.fields['time'].required = False
        self.fields['comments'].required = False
        self.fields['location'].required = False
        self.fields['location'].initial = 1

        if 'date' in self.data:
            try:
               date = self.data.get('date')
               if date != '':
                 self.fields['time'].queryset = TimeSlots.objects.filter(day=Days.objects.get(day=date))
            except Exception:
               #user = User.objects.get(username=self.user)
               #if user.is_superuser:
            #       print ('create day')
             #  else:
               self.errors['date'] = ['Invalid date.  Please enter a valid date']


    def clean(self, *args, **kwargs):
        #print ('clean', kwargs)
        #user = User.objects.get(username=self.user)
        cleaned_data = super(AppointmentForm, self).clean()

        if cleaned_data.get('date') == None and cleaned_data['comments'] == '':
            print ('raising form error')
            raise forms.ValidationError("Please enter either a message or a meeting date/time")

        if cleaned_data.get('date') != None:
            try:
                day = Days.objects.get(day=cleaned_data.get('date'))
                print (day)
                if day.closed:
                    self.errors['date'] = ["We are closed that day, please choose another day or email us by clicking the link below."]
                #if day.day < datetime.datetime.now().date() and not user.is_superuser:
                #    self.errors['date'] = ['Invalid date.  Please choose a future date']
                else:
                    if cleaned_data.get('time') == None:
                        self.errors['time'] = ['Please select a time from the list']

            except ObjectDoesNotExist:
                # if self.user:
                #     if user.is_superuser:
                #         day = Days()
                #         day.day = self.data.get('date')
                #         day.closed = False
                #         day.save()
                #         manage_cal.setup_cal(cleaned_data.get('date'))
                # else:
                self.errors['date'] = ["Please contact us via email to schedule for that date."]
            except Exception as e:
                print (e)
                self.errors['date'] = ["Please choose another date, or email us for help."]

        return cleaned_data



class CreateEvent(forms.Form):
    day = forms.DateField(label="Start Date", widget=forms.TextInput(attrs=
                                {
                                    'class':'datepicker'
                                }))
    start_time = forms.TimeField(widget=forms.TextInput(attrs=
                                {
                                    'class':'timepicker'
                                }))
    end_time = forms.TimeField(widget=forms.TextInput(attrs=
                                {
                                    'class':'timepicker'
                                }))
    note = forms.CharField()


    def clean(self):
        if self.is_valid():
            cleaned_data = super(DaysOffForm, self).clean()
            start = self.cleaned_data['start_time']
            end = self.cleaned_data['end_time']

            if start > end:
                raise forms.ValidationError("start date should be before end date")


class UserCreateForm(UserCreationForm):
    class Meta:
        fields = ("username", "email", "password1", "password2")
        model = get_user_model()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Display name"
        self.fields["email"].label = "Email address"

class CreateClientForm(ModelForm):


        class Meta:
            model = Client
            #fields = "__all__"
            fields  = ['name', 'email', 'phone', 'coverage', 'package', 'focus_areas' ]
            widgets = {
            'focus_areas': forms.CheckboxSelectMultiple(choices=FocusAreas.objects.all())
            }


        def __init__(self, *args, **kwargs):
            super(CreateClientForm, self).__init__(*args, **kwargs)

            self.fields['phone'].required = False
            self.fields['focus_areas'].required = False
            self.fields['coverage'].required = False
            self.fields['package'].required= False


class CreateNotesForm(ModelForm):
        class Meta:
            model = Notes
            fields = ['appointment', 'items_discussed', 'follow_ups']

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['appointment'].disabled = True
            self.fields['appointment'].required = False

        def clean(self):
            cleaned_data = super(CreateNotesForm, self).clean()
            if cleaned_data.get('items_discussed') == None:
                self.errors['items_discussed'] = "Please enter data"
            if cleaned_data.get('follow_ups') == None:
                self.errors['follow_ups'] = "Please enter data"

            return cleaned_data


CreateNotesFormSet = modelformset_factory(Notes, form=CreateNotesForm, extra=0)

class CreatePackageForm(ModelForm):
    class Meta:
        model = Package
        fields = "__all__"

class CreateInvoiceForm(ModelForm):
    class Meta:
        model = Invoice
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        print ('init kw', kwargs)
        if kwargs.get('client') != None:
            client_key = kwargs.pop('client')
            print ('client_key',client_key)
            client = Client.objects.get(pk=client_key)
        else:
            kwargs.pop('client')
            client = None

        super(CreateInvoiceForm, self).__init__(*args, **kwargs)

        if client != None:
            self.fields['client'].initial = client
            try:
                if client.package.num_of_sessions == 1:
                    self.fields['appointment'].queryset = Appointment.objects.filter(client=client)
                    self.fields['appointment'].initial = Appointment.objects.filter(client=client, date__lte=datetime.date.today()).latest('date')
                else:
                    self.fields['appointment'].initial = None
                self.fields['principal'].initial = client.package.price * .92
                self.fields['tax'].initial = client.package.price * .08
                self.fields['total'].initial = client.package.price
                self.fields['package'].initial = client.package

            except Exception as e:
                package = Package.objects.get(pk=1) #default is 1 off, hard coded pk.
                self.fields['package'].initial = package

                self.fields['principal'].initial = package.price * .92
                self.fields['tax'].initial = package.price * .08
                self.fields['total'].initial = package.price


                print ('client package excption', e)



        if Invoice.objects.all().exists():
            invoice_num = Invoice.objects.all().aggregate(Max('number'))
            num = invoice_num.get('number__max') + 1
        else:
            num = 1
        self.fields['number'].initial = num
        self.fields['inv_date'].initial=datetime.date.today()

        self.fields['inv_date'].label = "Invoice Date"
        self.fields['status'].initial = '1'


    def save(self):
        if 'send' in self.data:
            send_invoice(self.instance)
        elif 'save' in self.data:
            print ('save')

        return super(CreateInvoiceForm, self).save()

def send_invoice(invoice):
    dir = settings.BASE_DIR + '/ss_app/templates/ss_app/'
    msg_plain = render_to_string(dir + 'invoice_email.txt', {'invoice': invoice})
    msg_html = render_to_string(dir + 'invoice_email.html', {'invoice': invoice})
    print(msg_html)
    send_mail("Stepping Stones Invoice ",
    msg_plain,
    "steppingstonetk.gmail.com",
    [invoice.client.email],
    html_message=msg_html,
     )

    return


class CreateReceiptForm(ModelForm):
    class Meta:
        model = Receipt
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        print ('receipt init kw', kwargs)
        if kwargs.get('client') != None:
            client_key = kwargs.pop('client')
            print ('client_key',client_key)
            client = Client.objects.get(pk=client_key)
        else:
            kwargs.pop('client')
            client = None

        super(CreateReceiptForm, self).__init__(*args, **kwargs)
        if client:
            self.fields['invoice'].queryset = Invoice.objects.filter(client=client, status=1)
        self.fields['paid_date'].initial = datetime.date.today()
        if Receipt.objects.all().exists():
            receipt_num = Receipt.objects.all().aggregate(Max('number'))
            num = receipt_num.get('number__max') + 1
        else:
            num = 1
        self.fields['number'].initial = num

    def save(self):
        if 'send' in self.data:
            print ('instance', self.instance)
            send_receipt(self.instance)

        elif 'save' in self.data:
            print ('save')

        invoice = Invoice.objects.get(pk=self.instance.invoice.pk)
        invoice.status = "2"
        invoice.save()

        return super(CreateReceiptForm, self).save()

def send_receipt(receipt):
    dir = settings.BASE_DIR + '/ss_app/templates/ss_app/'
    msg_plain = render_to_string(dir + 'receipt_email.txt', {'receipt': receipt})
    msg_html = render_to_string(dir + 'receipt_email.html', {'receipt': receipt})
    print(msg_html)
    send_mail("Stepping Stones Receipt ",
    msg_plain,
    "steppingstonetk.gmail.com",
    [receipt.invoice.client.email],
    html_message=msg_html,
     )

    return
