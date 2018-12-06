from django import forms
from django.forms import ModelForm, MultipleChoiceField
from .models import Days, TimeSlots, Event, Appointment, Staff, Client, Notes,\
                FocusAreas
import datetime
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.forms.models import modelformset_factory
from django.forms.formsets import BaseFormSet
from django.forms import inlineformset_factory
import ss_app.views


from django.utils.safestring import mark_safe


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

      # available = forms.ChoiceField(choices=CHOICES, initial="O")
      # assigned_to = forms.ChoiceField()
      # comments = forms.CharField(max_length=100)

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
           self.fields['start_time'].widget.attrs['size']= '6'
           self.fields['start_time'].widget.attrs['style']= 'border: 0px solid'
           self.fields['end_time'].widget.attrs['size']= '6'
           self.fields['end_time'].widget.attrs['style']= 'border: 0px solid'


SlotsFormSet = modelformset_factory(TimeSlots, SlotsForm, extra=0 )



class AppointmentForm(ModelForm):

    class Meta:
         model=Appointment
         #fields=['name','email','phone','comments', 'date', 'time', 'location']
         fields=['comments', 'date', 'time', 'location']
         widgets = {'date': forms.TextInput({}),
                    'time': forms.Select(attrs= {}),
                    'comments': forms.Textarea(attrs= {'rows':3, 'cols':50, 'style': 'width: 100%'}),
                    }

    def __init__(self, *args, **kwargs):
        super(AppointmentForm, self).__init__(*args, **kwargs)
        self.fields['time'].queryset = TimeSlots.objects.none()
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
            except (ValueError, TypeError):
               pass


    def clean(self, *args, **kwargs):
        print (self.data)
        cleaned_data = super(AppointmentForm, self).clean()

        if cleaned_data.get('date') == None and cleaned_data['comments'] == '':
            print ('raising form error')
            raise forms.ValidationError("Please enter either a message or a meeting date/time")

        try:
            if cleaned_data.get('date') < datetime.datetime.now().date():
                print ('raising date error')
                self.errors['date'] = ['Invalid date.  Please choose a future date']
            else:
                if cleaned_data.get('time') == None:
                    print ('time error')
                    self.errors['time'] = ['Please select a time from the list']
        except Exception as e:
                #pass is ok as it has comments per the edit above
                print ('date exception', e)
                pass


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
            #CHOICES = ()
            #for focus in FocusAreas.objects.all():
            #    choice = (focus.focus_area, focus.focus_area)
            #    CHOICES = CHOICES + (choice,)
            #print ('choices', CHOICES)

            model = Client
            #exclude = ('focus_areas','coverage')
            fields = "__all__"
            widgets = {
            'focus_areas': forms.CheckboxSelectMultiple(choices=FocusAreas.objects.all())
            }


        def __init__(self, *args, **kwargs):
            super(CreateClientForm, self).__init__(*args, **kwargs)

            #focus_list = []
            #client = Client.objects.get(pk=self.instance.pk)
            #print (type(client.focus_areas))

            #for focus in client.focus_areas:
            #    focus_list.append(focus)
            #print (focus_list)
            self.fields['phone'].required = False
            self.fields['focus_areas'].required = False
            self.fields['coverage'].required = False
            #self.fields['focus_areas'].initial = (focus for fa in focus_list)

#            self.fields['focus_areas'] = MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
#                                             choices=CHOICES)

class CreateNotesForm(ModelForm):
        class Meta:
            model = Notes
            fields = ['appointment', 'items_discussed', 'follow_ups', 'paid']

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['appointment'].disabled = True
            self.fields['appointment'].required = False
            #self.fields['items_discussed'].required = False
            #self.fields['follow_ups'].required = False
            #self.fields['paid'].required = False
            #if self.instance.appointment != None:
            #    print ('form', self.instance.appointment.date)
            #    if self.instance.appointment.date > datetime.datetime.now().date():
            #        print ('false', self.instance.appointment.date)
            #        self.fields['focus_areas'].reqired = False
            #        self.fields['items_discussed'].reqired = False
            #        self.fields['follow_ups'].reqired = False

        def clean(self):
            cleaned_data = super(CreateNotesForm, self).clean()
            if cleaned_data.get('items_discussed') == None:
                self.errors['items_discussed'] = "Please enter data"
            if cleaned_data.get('follow_ups') == None:
                self.errors['follow_ups'] = "Please enter data"

            return cleaned_data


CreateNotesFormSet = modelformset_factory(Notes, form=CreateNotesForm, extra=0)
