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
from django.conf import settings


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

def index1(request):
    return render(request, 'index1.html')


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


    def get_context_data(self, **kwargs):
        context = super(CalView, self).get_context_data(**kwargs)

        data = self.get_data()

        context.update({
        'requests': data[1],
        'appointments': data[0],
        'formset': data[2],
        'coverage_list': data[3],
        })

        return context


    def get_data(self):
        appointment_list = []

        for appt in Appointment.objects.filter(date__lte=datetime.datetime.now().date(), \
           time__available="B"):
            if Notes.objects.filter(appointment=appt,\
            items_discussed__isnull=False).exists():
                pass
            else:
                appointment_list.append(appt)

        requests = Appointment.objects.filter\
        (Q(time__available="R") | Q(time__available="B", time__assigned_to=None))

        start_date = datetime.datetime.now().date()

        formset = CalUpdateFormSet(queryset=Days.objects.filter\
        (day__gte=start_date))


        coverage_list = []
        for client in Client.objects.all():
            if client.coverage == None:
                coverage_list.append(client)

        return appointment_list, requests, formset, coverage_list


    def post(self, request, **kwargs):
        formset = CalUpdateFormSet(request.POST)

        if formset.is_valid():
            for form in formset:
                cd = form.cleaned_data
                key = cd.get('id')
                day = Days.objects.filter(pk=key.pk).update(closed=cd.get('closed'), note=cd.get('note'))
                message = 'Updates Successful'
        else:
            print ("CalView error", formset.errors)
            message = formset.errors

        data = self.get_data()

        return render (request, 'ss_app/days_list.html', {'requests': data[1],
                                                          'appointments': data[0],
                                                          'formset': data[2],
                                                          'coverage_list': data[3],
                                                          'message': message,
                                                            })


def refresh_cal(request):
    if request.is_ajax():
        start_day = datetime.datetime.strptime(request.GET.get('day')[:-40], "%a %b %d %Y")

        end_day = start_day + datetime.timedelta(weeks=2)
        days_list = []

        days = Days.objects.filter(day__gte=start_day, day__lte=end_day).values('pk', 'str__day', 'closed', 'note')
        days_list.append(list(days))
        print(days_list)
        data = json.dumps(list(days_list))
        return HttpResponse(data, content_type="application/json")

    else:
        print ('not ajax')
        raise Http404
    print ('bad call', request)
    return


def cal_get_mtg_cnt(request):
        if request.is_ajax():
            day = request.GET.get('day')

            count_list = []
            if TimeSlots.objects.filter(day__day=day, available__in=['B', 'R']).exists():
                slot  = TimeSlots.objects.filter(day__day=day, available__in=['B', 'R']).values('day__day', 'day_id').annotate(count=Count('available'))

            #date = slot['day__day']
                print ('slot', slot)
                print ('count', slot[0].get('count'))
                print ('date', slot[0].get('day__day'))
                print ('date', slot[0].get('day_id'))
            #print (date.strftime('%Y-%M-%D'))

            #count_list.append(date)
                count_list.append(str(slot[0].get('day__day')))
                count_list.append(str(slot[0].get('day_id')))
                count_list.append(slot[0].get('count'))
            else:
                count_list.append(day)
                day = Days.objects.get(day=day)
                count_list.append(day.pk)
                count_list.append(0)
            data = json.dumps(count_list)
            return HttpResponse(data, content_type="application/json")

        else:
            print ('not ajax')
            raise Http404
        print ('bad call', request)
        return



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
        message = None
        if formset.is_valid():
            for form in formset:
                cd = form.cleaned_data
                key = cd.get('id')
                slot = TimeSlots.objects.get(pk=key.pk)
                if slot.available == cd.get('available') and \
                   slot.assigned_to == cd.get('assigned_to') and \
                   slot.comments == cd.get('comments'):
                   pass
                else:
                   if slot.available != cd.get('available') and \
                      cd.get('available') == "B":
                      #slot.available = cd.get('available')
                      #slot.assigned_to = cd.get('assigned_to')
                      #slot.comments = cd.get('comments')
                      slot.update(available=cd.get('available'), comments=cd.get('comments'))
                      add_to_cal(slot)
                      send_client_email(slot)
                   else:
                      slot.available = cd.get('available')
                      #slot.assigned_to = cd.get('assigned_to')
                      slot_assigned_to = slot.assigned_to
                      slot.comments = cd.get('comments')
                      #slot.update(available=cd.get('available'), comments=cd.get('comments'))
                      slot.save()
                      add_to_cal(slot)

                 #  if TimeSlots.objects.filter(day=cd['day'], start_time=cd['start_time'], available="O").count() > 1:
                #       TimeSlots.objects.filter(day=cd['day'], start_time=cd['start_time'], available="O").latest('created').delete()

                   message = 'Updates Successful'
        else:
            print ('slotsdetail formset errors',formset.errors)
            message = None

        day = Days.objects.get(pk=kwargs.get('pk'))
        formset  = SlotsFormSet(queryset=TimeSlots.objects.filter(day=day).order_by('start_time'))

        return render (request, 'ss_app/days_detail.html', {'day': day,
                                                            'formset': formset,
                                                            'message': message,
                                                            })


def send_client_email(slot):
    print ('slot pk =', slot.pk)
    appt = Appointment.objects.get(time__pk=slot.pk)
    print ('assigned to = ', appt.time)
    dir = settings.BASE_DIR + '/ss_app/templates/ss_app/'
    msg_plain = render_to_string(dir + 'email.txt', {'appt': appt})
    msg_html = render_to_string(dir + 'email.html', {'appt': appt})
    print(msg_html)
    send_mail("Your Appointment on " + str(appt.date) +" is Confirmed",
    msg_plain,
    "steppingstonetk.gmail.com",
    [appt.client.email],
    html_message=msg_html,
     )

    return

def add_to_cal(slot):


    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('calendar', 'v3', http=creds.authorize(Http()))

    # Insert test events
    page_token = None

    if slot.available == "B":
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
            slot.cal_event_id = event.get('id')
            slot.save()

        except Exception as e:
            print ('exception', e)
    elif slot.cal_event_id:
        service.events().delete(calendarId='primary', eventId=slot.cal_event_id).execute()


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

        data = json.dumps(client_list)
        return HttpResponse(data, content_type="application/json")

    else:
        print ('not ajax')
        raise Http404

    return


def get_client(request):
    if request.is_ajax():
       slots = TimeSlots.objects.filter(day__pk=request.GET.get('activity')).order_by('start_time')
       appt_list = []
       for slot in slots:
           appt = Appointment.objects.filter(time__pk=slot.pk).values('client__name', 'client__pk', 'pk')
           appt_list.append(list(appt))

       data = json.dumps(appt_list)
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
        print ('in form valid')
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


            if appt_form.cleaned_data['date'] != None and \
               Appointment.objects.filter(client=client, date=appt_form.cleaned_data['date']).exists():
                appt_form.add_error('date', 'You already have an appointment for that date, please send an email via the link below if you have any questions.')
                return super(AppointmentCreateView, self).form_invalid(appt_form)


            if form.instance.time != None:
                slot = TimeSlots.objects.get(pk=form.instance.time.pk)
                if slot.available == "O":
                    appt = appt_form.save(commit=False)
                    appt.client=client
                    appt.save()

                    slot.available = "R"
                    #slot.assigned_to = client.coverage
                    slot.save()
                    notes = Notes()
                    notes.appointment = appt
                    notes.save()
            else:
                appt = appt_form.save(commit=False)
                appt.client=client
                appt.save()


            #subject = "SS web form submitted" + form.instance.pk

            mail_sub = "SS web form submitted: " + str(form.instance.date) + str(client.name)
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
            if settings.DEBUG == False:
                send_mail(mail_sub, mail_content, 'steppingstonetk.gmail.com', mail_recipients)  #add fail silently

            print (appt.pk)

            return HttpResponseRedirect(reverse_lazy('ss_app:thanks', args=[appt.pk]))

        else:
            print ('these form errors', client_form.errors, appt_form.errors)
            return render (self.request, 'ss_app/appointment_form.html', {'days': Days.objects.filter(closed=True),
                                                                'client': client_form,
                                                                'form': appt_form,
                                                                'errors': appt_form.errors
                                                                        })


class AppointmentUpdateView(LoginRequiredMixin, UpdateView):
      login_url='/ss_app/login'
      model = Appointment
      form_class = AppointmentForm
      template_name = "ss_app/update_appt_form.html"
      success_url = reverse_lazy("ss_app:calendar")

      def get_context_data(self, **kwargs):

          context = super(AppointmentUpdateView, self).get_context_data(**kwargs)
          appt = Appointment.objects.get(pk=self.kwargs.get('pk'))
          client = Client.objects.get(pk=appt.client.pk)
          context.update( {
           'appt': appt,
           'days': Days.objects.filter(closed=True),
           'client': client
           })

          return context


      def form_valid(self, request, **kwargs):
           appt_form = AppointmentForm(self.request.POST)
           if appt_form.is_valid():
               cd = appt_form.cleaned_data

               appt = Appointment.objects.get(pk=self.kwargs.get('pk'))
               orig_slot = TimeSlots.objects.get(pk=appt.time.pk)
               day = Days.objects.get(day=cd['date'])
               slot = TimeSlots.objects.get(pk=cd['time'].pk)

               appt.date = cd['date']
               appt.time= slot
               appt.location=cd['location']
               appt.comments=cd['comments']
               appt.save()
               #auto book new slot
               slot.available = "B"
               print ('slot save', slot)
               slot.save()
               send_client_email(slot)
               add_to_cal(slot)

               #reset original time slot to open if changed
               if orig_slot.pk != slot.pk:
                   orig_slot.available = "O"
                   orig_slot.save()
                   add_to_cal(orig_slot)

               return HttpResponseRedirect(reverse('ss_app:detail', kwargs={'pk':day.pk}))
           else:
               ## does this make sense?  When can form be invalid and what should i do?
               print (appt_form)
               raise forms.ValidationError("Invalid update")
               return HttpResponseRedirect(reverse('ss_app:detail', kwargs={'pk':day.pk}))


class AppointmentDeleteView(LoginRequiredMixin, DeleteView):
      login_url='/ss_app/login'
      model = Appointment
      #form_class = AppointmentForm
      #template_name = "ss_app/appointment_confirm_delete.html"
      success_url = reverse_lazy("ss_app:calendar")

      def get_context_data(self, **kwargs):
          context = super(AppointmentDeleteView, self).get_context_data(**kwargs)
          appt = Appointment.objects.get(pk=self.kwargs.get('pk'))
          day = Days.objects.get(day=appt.date)
          context.update({
          'day': day
          })

          return context


      def post(self, request, **kwargs):

          appt = Appointment.objects.get(pk=self.kwargs.get('pk'))
          orig_slot = TimeSlots.objects.get(pk=appt.time.pk)
          #reset attached slot
          orig_slot.available = "O"
          #orig_slot.assigned_to = None
          orig_slot.save()
          add_to_cal(orig_slot)

          return super(AppointmentDeleteView, self).post(self, request, **kwargs)


def load_slots(request):
    print ('loadings slots')
    print (request)
    date = request.GET.get('day')
    mode = request.GET.get('mode')
    slot_list = []
    try:
        client = Client.objects.get(email=request.GET.get('client'))
        print (client.coverage)
        # for existing client with coverage assigned
        if client.coverage:
            print ('in client coverage')
            time_slots = TimeSlots.objects.filter(day=Days.objects.get(day=date), assigned_to=client.coverage).order_by('start_time')
            for slot in time_slots:
                if slot.available == "O":
                    slot_list.append(slot)
        else:
            # for existing client with no coverage assigned
            time_slots = TimeSlots.objects.filter(day=Days.objects.get(day=date)).order_by('start_time')
            for slot in time_slots:
                if slot.available == "O":
                    slot_list.append(slot)
                else:
                    slots = ''

    except Exception as e:
            # for new client or from meeting update page
            print ('in exception', e)
            staff_cnt = len(Staff.objects.all())

            time_slots = TimeSlots.objects.filter(day=Days.objects.get(day=date)).order_by('start_time')
            for slot in time_slots:
                if Appointment.objects.filter(time__pk=slot.pk).exists() and mode == "update":
                    slot_list.append(slot)
                elif slot.available == "O":
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
    #success_url = reverse_lazy("ss_app:client_list")

    def get_context_data(self, **kwargs):
        context = super(ClientUpdateView, self).get_context_data(**kwargs)
        data = self.build_view()
        context.update({
        #'client': data[0],
        'notes_formset': data[1],
        'old_notes': data[2],
        'upcoming_meetings': data[3]
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

            return
            print ('invalid formset', notes_formset)

        data = self.build_view()
        print (data)

        return HttpResponseRedirect(reverse_lazy('ss_app:update_client', args=[instance.pk]))


    def build_view(self, **kwargs):
        client = Client.objects.get(pk=self.kwargs.get('pk'))
        notes_formset = CreateNotesFormSet(queryset=Notes.objects.filter\
        (appointment__client=client, items_discussed__isnull=True, \
         appointment__date__lte=datetime.datetime.now(), \
         appointment__time__available="B") \
         .order_by('-appointment__date'))

        old_notes = Notes.objects.filter(appointment__client=client).exclude(items_discussed__isnull=True)

        upcoming_meetings = Appointment.objects.filter(client=client, date__gte=datetime.datetime.now())

        return (client, notes_formset, old_notes, upcoming_meetings)


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
