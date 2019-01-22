from django.conf.urls import url
from django.urls import path
from ss_app import views
from django.contrib.auth import views as auth_views

app_name = 'ss_app'

urlpatterns = [
    url(r'^about/$',views.about,name='about'),
    url(r'^team/$',views.team,name='team'),
    url(r'^appt/$',views.AppointmentCreateView.as_view(),name='appt'),
    url(r'^update_appt/(?P<pk>\d+)$',views.AppointmentUpdateView.as_view(),name='update_appt'),
    url(r'^delete_appt/(?P<pk>\d+)$',views.AppointmentDeleteView.as_view(),name='delete_appt'),
    url(r'^services/$',views.services,name='services'),
    url(r'^calendar$',views.CalView.as_view(),name='calendar'),
    url(r'^calendar/(?P<pk>\d+)$',views.SlotsDetail.as_view(),name='detail'),
    url(r"^thanks/(?P<pk>\d+)/$", views.ThanksPageView.as_view(), name="thanks"),
    url(r"^payment/$", views.PaymentPageView.as_view(), name="payment"),
    url(r'^login/$',auth_views.LoginView.as_view(template_name='ss_app/login.html'),name='login'),
    url(r'^logout/$',auth_views.LogoutView.as_view(),name='logout'),
    url(r'^signup/$',views.SignUp.as_view(),name='signup'),
    url(r'^add_client/$',views.ClientCreateView.as_view(),name='add_client'),
    url(r'^update_client/(?P<pk>\d+)/$',views.ClientUpdateView.as_view(),name='update_client'),
    url(r'^delete_client/(?P<pk>\d+)/$',views.ClientDeleteView.as_view(),name='delete_client'),
    url(r'^client_list/$', views.ClientListView.as_view(),name='client_list'),
    url(r'^add_notes/(?P<pk>\d+)/$',views.NotesCreateView.as_view(),name='add_notes'),
    url(r'^invoice_list/$', views.InvoiceListView.as_view(), name='invoice_list'),
    #url(r'^add_invoice/(?P<pk>\d+)/$', views.InvoiceCreateView.as_view(), name='add_invoice'),
    url(r'^add_invoice//$',views.InvoiceCreateView.as_view(), name='add_invoice' ),
    url(r'^add_invoice/(?P<pk>\d+)/$',views.InvoiceCreateView.as_view(), name='add_invoice' ),
    url(r'^update_invoice/(?P<pk>\d+)/$',views.InvoiceUpdateView.as_view(),name='update_invoice'),
    url(r'^delete_invoice/(?P<pk>\d+)/$',views.InvoiceDeleteView.as_view(),name='delete_invoice'),
    #url(r'^review_invoice/(?P<pk>\d+)/$',views.InvoiceReviewView.as_view(),name='review_invoice'),
    url(r'^package_list/$', views.PackageListView.as_view(), name='package_list'),
    url(r'^add_package/$',views.PackageCreateView.as_view(),name='add_package'),
    url(r'^update_package/(?P<pk>\d+)/$',views.PackageUpdateView.as_view(),name='update_package'),
    url(r'^delete_package/(?P<pk>\d+)/$',views.PackageDeleteView.as_view(),name='delete_package'),
    url(r'^ajax/get_client/$', views.get_client, name='get_client'),
    url(r'^ajax/appt_get_client/$', views.appt_get_client, name='appt_get_client'),
    url(r'^ajax/cal_get_mtg_cnt/$', views.cal_get_mtg_cnt, name='cal_get_mtg_cnt'),
    url(r'^ajax/refresh_cal/$', views.refresh_cal, name='refresh_cal'),


]
