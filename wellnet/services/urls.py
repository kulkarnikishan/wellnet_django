from django.conf.urls import url
from django.contrib import admin

from .views import CascadAutoResponseView

urlpatterns = [
    url(r'^services/getPDF$', 'services.views.pdf_view', name='pdf_view'),
    url(r'^services/savePDF$', 'services.views.savePDF', name='savePDF'),
    url(r'^services/booking/invoice/(?P<id>\d+)/$', 'services.views.download_pdf', name='DownlaodPDF'),
    url(r'^services/booking/receipt/(?P<id>\d+)/$', 'services.views.download_receipt_pdf', name='DownlaodPDF'),
    url(r'^services/booking/invoice/(?P<id>\d+)/proforma/$', 'services.views.download_ProForma_pdf', name='DownlaodPDF'),
    url(r'^services/getAmount$', 'services.views.totalAmountForProduct', name='totalAmountForProduct'),
    url(r'^services/getAmountForCustomer$', 'services.views.totalAmountForCustomerProduct',
        name='totalAmountForCustomerProduct'),
    url(r'^cascade_model_select2_widget/$', CascadAutoResponseView.as_view(), name='cascade_model_select2_widget'),

]
admin.site.site_header = 'WellNet Sales'
admin.site.site_title = 'Sales Portal'
admin.site.index_title = 'Sales administration'
