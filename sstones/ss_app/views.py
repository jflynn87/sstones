from __future__ import print_function
from django.shortcuts import render, redirect, get_object_or_404
from .forms import CreateEvent, SlotsForm, AppointmentForm, UserCreateForm,\
   CreateClientForm, CreateNotesForm, CreateNotesFormSet, SlotsFormSet, CalUpdateFormSet, \
   CalUpdateForm
from django.http import HttpResponseRedirect, HttpResponse
from .models import Event, Appointment, TimeSlots, Days, Staff, Client, Notes
import datetime
from django.views.generic import TemplateView, DetailView, ListView,\
 UpdateView, DeleteView, CreateView, View, FormView
from django.urls import reverse, reverse_lazy
from django.core.mail import send_mail, EmailMultiAlternatives, EmailMessage
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import ProcessFormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Count
from django.core.exceptions import ObjectDoesNotExist


from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

from django.http import JsonResponse
from django.core import serializers
import json

from django.template.loader import render_to_string

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/calendar'

# Create your views here.

def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'ss_app/about.html')

def team(request):
    return render(request, 'ss_app/team.html')

def services(request):
    return render(request, 'ss_app/services.html')



class ThanksPageView(TemplateView):
    template_name= "ss_app/thanks.html"

    def get_context_data(self, *args, **kwargs):
        context = super(ThanksPageView, self).get_context_data(*args, **kwargs)
        print (kwargs)
        context.update ({
        'appt': Appointment.objects.get(pk=kwargs.get('pk'))
        })
        return context





class PaymentPageView(TemplateView):
    template_name= "ss_app/payment.html"



class CalView(LoginRequiredMixin, TemplateView):
    login_url='/ss_app/login'
    model = Days
    success_url = reverse_lazy('ss_app:calendar')
    template_name = "ss_app/days_list.html"
    #paginate_by = 90

    def dispatch(self, request, *args, **kwargs):

        if not self.request.user.is_staff:
            print ('unauthorized')
            return super(CalView, self).dispatch(request, *args, **kwargs)
        else:
            return super(CalView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(CalView, self).get_context_data(**kwargs)

        requests = Appointment.objects.filter\
        (Q(time__available="R") | Q(time__available="B", time__assigned_to=None))
        formset = CalUpdateFormSet(queryset=Days.objects.filter(day__gte=datetime.datetime.now().date()))
        appointment_list = self.get_appt_list()

        context.update({
        'requests': requests,
        'appointments': appointment_list,
        'formset': formset,

        })
        return context


    def get_appt_list(self):
        appointment_list = []

        for appt in Appointment.objects.filter(date__lte=datetime.datetime.now().date(), \
           time__available="B"):
            print ('appt', appt.client)
            if Notes.objects.filter(appointment=appt,\
            items_discussed__isnull=False).exists():
                pass
            else:
                appointment_list.append(appt)

        return appointment_list

    def post(self, request, **kwargs):
        formset = CalUpdateFormSet(request.POST)

        if formset.is_valid():
            for form in formset:
                cd = form.cleaned_data
                print (cd)
                key = cd.get('id')
                day = Days.objects.filter(pk=key.pk).update(closed=cd.get('closed'), note=cd.get('note'))
                message = 'Updates Successful'
        else:
            print (formset.errors)
            message = formset.errors

        appointment_list = self.get_appt_list()
        requests = Appointment.objects.filter\
        (Q(time__available="R") | Q(time__available="B", time__assigned_to=None))

        formset = CalUpdateFormSet(queryset=Days.objects.filter(day__gte=datetime.datetime.now().date()))
        appointment_list = self.get_appt_list()

        return render (request, 'ss_app/days_list.html', {'requests': requests,
                                                          'appointments': appointment_list,
                                                          'formset': formset,
                                                          'message': message,
                                                            })


class SlotsDetail(LoginRequiredMixin, TemplateView):
    login_url = 'ss_app:login'
    model = Days
    form_class = SlotsForm
    template_name = 'ss_app/days_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        day = Days.objects.get(pk=kwargs.get('pk'))
        formset  = SlotsFormSet(queryset=TimeSlots.objects.filter(day=day).order_by('start_time'))
        appt_list = []

        context.update({
        'day': day,
        'formset': formset,
        })
        print (context)
        return (context)


    def post(self, request, **kwargs):
        formset = SlotsFormSet(request.POST)

        if formset.is_valid():
            for form in formset:
                cd = form.cleaned_data
                print (cd)
                key = cd.get('id')
                slot = TimeSlots.objects.get(pk=key.pk)
                if slot.available == cd.get('available') and \
                   slot.assigned_to == cd.get('assigned_to') and \
                   slot.comments == cd.get('comments'):
                   pass
                else:
                   if slot.available != cd.get('available') and \
                      cd.get('available') == "B":
                      slot.available = cd.get('available')
                      slot.assigned_to = cd.get('assigned_to')
                      slot.comments = cd.get('comments')
                      self.add_to_cal(slot)
                      self.send_client_email(slot)
                   else:
                      slot.available = cd.get('available')
                      slot.assigned_to = cd.get('assigned_to')
                      slot.comments = cd.get('comments')

                   slot.save()
                   message = 'Updates Successful'
        else:
            print ('formset errors',formset.errors)
            message = None

        day = Days.objects.get(pk=kwargs.get('pk'))

        return render (request, 'ss_app/days_detail.html', {'day': day,
                                                            'formset': formset,
                                                            'message': message,
                                                            })

    def add_to_cal(self, slot):

        print (slot.assigned_to)
        store = file.Storage('token.json')
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
            creds = tools.run_flow(flow, store)
        service = build('calendar', 'v3', http=creds.authorize(Http()))

        # Insert test events
        page_token = None

        desc = slot.comments
        mtg_start = str(slot.day) + "T" + str(slot.start_time)
        mtg_end = str(slot.day) + "T" + str(slot.end_time)

        try:
            appt = Appointment.objects.get(time=slot)

            event = {'summary': slot.assigned_to.name + ' meeting with: ' + appt.client.name,
                     'description': appt.comments,
                     'location': appt.get_location_display(),
                     'start': {'dateTime':mtg_start,
                               'timeZone': 'Asia/Tokyo',
                              },
                     'end': {'dateTime':mtg_end,
                               'timeZone': 'Asia/Tokyo',
                            },
            }

            event = service.events().insert(calendarId='steppingstonetk@gmail.com', body=event).execute()

        except Exception as e:
            print ('exception', e)

        return

    def send_client_email(self, slot):

        appt = Appointment.objects.get(time__pk=slot.pk)

        msg_plain = render_to_string('C:/Users/John/PythonProjects/sstones/sstones/ss_app/templates/ss_app/email.txt', {'appt': appt})
        msg_html = render_to_string('C:/Users/John/PythonProjects/sstones/sstones/ss_app/templates/ss_app/email.html', {'appt': appt})
        print(msg_html)
        send_mail("Your Appointment is confirmed",
        msg_plain,
        "steppingstonetk.gmail.com",
        [appt.client.email],
        html_message=msg_html,
        )

        return

def appt_get_client(request):
    print (request.GET)
    if request.is_ajax():
        try:
            client = Client.objects.get(email=request.GET.get('client'))
            client_list = []
            client_list.append(client.name)
            client_list.append(client.phone)
        except ObjectDoesNotExist:
            client_list = []

        print (client_list)
        data = json.dumps(client_list)
        return HttpResponse(data, content_type="application/json")

    else:
        print ('not ajax')
        raise Http404

    return


def get_client(request):
    #pass
    if request.is_ajax():
       slots = TimeSlots.objects.filter(day__pk=request.GET.get('activity')).order_by('start_time')
       appt_list = []
       for slot in slots:
           appt = Appointment.objects.filter(time__pk=slot.pk).values('client__name', 'client__pk', 'pk')
           appt_list.append(list(appt))

       data = json.dumps(appt_list)
       print (data)
       return HttpResponse(data, content_type="application/json")
    else:
       print ('not ajax')
       raise Http404

    return slots


class AppointmentCreateView(CreateView):
    model = Appointment
    form_class = AppointmentForm
    success_url =  reverse_lazy('ss_app:thanks')

    def get_context_data(self, **kwargs):
        context = super(AppointmentCreateView, self).get_context_data(**kwargs)
        #required to send proper data on error
        if self.request.POST:
            client = CreateClientForm(self.request.POST)
        else:
            client = CreateClientForm()

        context.update({
        'days': Days.objects.filter(closed=True),
        'client': client,

        })

        return context


    def form_valid(self, form):
        client_form = CreateClientForm(self.request.POST)
        appt_form = AppointmentForm(self.request.POST)
        if client_form.is_valid() and appt_form.is_valid():
            email = client_form.cleaned_data['email']
            print (email)
            if Client.objects.filter(email=email).exists():
                print ('client exists')
                client = Client.objects.get(email=email)
            else:
                print ('create client', client_form['email'])
                client = client_form.save(commit=False)
                client.save()


            if form.instance.time != None:
                slot = TimeSlots.objects.get(pk=form.instance.time.pk)
                if slot.available == "O":
                    appt = appt_form.save(commit=False)
                    appt.client=client
                    appt.save()

                    slot.available = "R"
                    slot.save()
                elif slot.available in ['B', 'R']:
                    new_slot = TimeSlots()
                    new_slot.day = form.instance.time.day
                    new_slot.start_time = form.instance.time.start_time
                    new_slot.end_time = form.instance.time.end_time
                    new_slot.available = "R"
                    new_slot.save()

                    appt = appt_form.save(commit=False)
                    appt.client=client
                    appt.time = new_slot
                    appt.save()
            else:
                    appt = appt_form.save(commit=False)
                    appt.client=client
                    appt.save()


            notes = Notes()
            notes.appointment = appt
            notes.save()


            mail_sub = "SS web form submitted"
            mail_from = "From: "+ client.name
            mail_email = "   Email: " + client.email
            mail_msg = "   Message:  " + form.instance.comments
            mail_date =  "  Date: " +  str(form.instance.date)
            mail_slot = "  Slot:  " + str(form.instance.time)

            mail_content = (mail_from +
                             mail_email +
                             mail_date +
                             mail_slot +
                             mail_msg )

    #these were commented            #msg = EmailMessage(mail_content, 'steppingstonetk.gmail.com',['steppingstonetk@gmail.com'],['jflynn87@hotmail.com'])
    #these were commented            #mail_recipients = ['steppingstonetk@gmail.com'],['jflynn87@hotmail.com'], ['jrc7825@gmail.com']


            #these work
            mail_recipients = ['steppingstonetk@gmail.com'],['jflynn87@hotmail.com'], ['jrc7825@gmail.com']
            send_mail(mail_sub, mail_content, 'steppingstonetk.gmail.com', mail_recipients)  #add fail silently

            print (appt.pk)

            return HttpResponseRedirect(reverse_lazy('ss_app:thanks', args=[appt.pk]))

        else:
            print ('form errors', client_form.errors, appt_form.errors)
            return render (self.request, 'ss_app/appointment_form.html', {'days': Days.objects.filter(closed=True),
                                                                'client': client_form,
                                                                'form': appt_form,

                                                                        })


def load_slots(request,date_dict=None):
    if request.GET:
        date = request.GET.get('day')
    else:
        date = datetime.datetime.strptime(date_dict.get('date'), "%Y-%m-%d")

    staff_cnt = len(Staff.objects.all())

    slot_list = []
    time_slots = TimeSlots.objects.filter(day=Days.objects.get(day=date))
    for slot in time_slots:
        if slot.available == "O":
            slot_list.append(slot)
        elif TimeSlots.objects.filter(day=Days.objects.get(day=date), start_time=slot.start_time, available__in=('B', 'R')).count() < staff_cnt:
            slot_list.append(slot)
        else:
            slots = ''
    return render(request, 'ss_app/slots_dropdown_list_options.html', {'slots':slot_list})

class SignUp(CreateView):
    form_class = UserCreateForm
    success_url = reverse_lazy('login')
    template_name  = 'ss_app/signup.html'


class ClientCreateView(LoginRequiredMixin, CreateView):
    login_url='/ss_app/login'
    model = Client
    form_class = CreateClientForm
    success_url=reverse_lazy('ss_app:client_list')

class ClientUpdateView(LoginRequiredMixin, UpdateView):
    login_url='/ss_app/login'
    model = Client
    form_class = CreateClientForm
    success_url = reverse_lazy("ss_app:client_list")

    def get_context_data(self, **kwargs):
        context = super(ClientUpdateView, self).get_context_data(**kwargs)
        data = self.build_view()
        context.update({
        #'client': data[0],
        'notes_formset': data[1],
        'old_notes': data[2],
        })
        return context

    def post(self, request, **kwargs):
        instance = get_object_or_404(Client, pk=kwargs.get('pk'))
        client_form = CreateClientForm(self.request.POST or None, instance=instance)
        notes_formset = CreateNotesFormSet(self.request.POST)

        if notes_formset.is_valid() and client_form.is_valid():
            for form in notes_formset:
                if form.is_valid():
                    form.save()
                else:
                    print ('invalid note form', form)
            client_form.save()
        else:
            print ('invalid formset', notes_formset)

        data = self.build_view()

        return render(request, 'ss_app/notes_form.html',
                    {'notes_formset': data[1],
                     'old_notes': data[2],
                     'client': data[0],
                     #'appts': appts,
            #         'message':message
            })


    def build_view(self, **kwargs):
        client = Client.objects.get(pk=self.kwargs.get('pk'))
        notes_formset = CreateNotesFormSet(queryset=Notes.objects.filter\
        (appointment__client=client, items_discussed__isnull=True, \
         appointment__date__lte=datetime.datetime.now(), \
         appointment__time__available="B") \
         .order_by('-appointment__date'))

        old_notes = Notes.objects.filter(appointment__client=client).exclude(items_discussed__isnull=True)

        return (client, notes_formset, old_notes)


class ClientDeleteView(LoginRequiredMixin, DeleteView):
    login_url='/ss_app/login'
    model = Client

class ClientListView(LoginRequiredMixin, ListView):
    login_url='/ss_app/login'
    model = Client

class NotesCreateView(LoginRequiredMixin, CreateView):
    login_url='/ss_app/login'
    model = Notes
    form_class = CreateNotesForm
    success_url=reverse_lazy('ss_app:client_list')

    def get_context_data(self, *args, **kwargs):
        context = super(NotesCreateView, self).get_context_data(*args, **kwargs)
        client = Client.objects.get(pk=self.kwargs.get('pk'))
        appts = Appointment.objects.filter(client=client, date__lte=datetime.datetime.now().date())
        notes =  Notes.objects.filter(appointment__in=appts).order_by('-appointment__date')
        formset = CreateNotesFormSet(queryset=notes)

        context.update({
        'client': client,
        'appts': appts,
        'formset': formset
        })

        return context


    def post(self, request, **kwargs):
        print (request.POST)
        print (kwargs)
        formset = CreateNotesFormSet(request.POST)
        print (Notes.objects.filter(appointment__client__pk=kwargs.get('pk')))

        if formset.is_valid():
            for form in formset:
                if form.is_valid():
                    print ('save')
                    form.save()
            return HttpResponseRedirect(self.success_url)

        else:
            print ('form issue', formset.errors)
            client = Client.objects.get(pk=self.kwargs.get('pk'))
            appts = Appointment.objects.filter(client=client, date__lte=datetime.datetime.now().date())
            message = "Form errors"
            return render(request, 'ss_app/notes_form.html',
             {'formset': formset,
             'client': client,
             'appts': appts,
             'message':message})
