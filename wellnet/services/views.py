from __future__ import absolute_import, unicode_literals

import logging
import re
from decimal import *
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.core import signing
from django.core.mail import EmailMessage
from django.core.signing import BadSignature
from django.http import Http404
from django.http import JsonResponse
from django.http.response import HttpResponseForbidden
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.encoding import smart_text
from django.views.generic.list import BaseListView
from django_select2.cache import cache
from django_select2.conf import settings
# from wellnet.settings import BACTAKLEEN_SERVICE_BOOKING_TEMPLATE_NAME_TO_CUSTOMER1 as dealer_network_temp_cust
# from wellnet.settings import BACTAKLEEN_SERVICE_BOOKING_TEMPLATE_NAME_TO_CUSTOMER2 as home_service_for_cust
# from wellnet.settings import BACTAKLEEN_SERVICE_BOOKING_TEMPLATE_NAME_TO_DEALER1 as dealer_network_temp_for_delaer
# from wellnet.settings import BACTAKLEEN_SERVICE_BOOKING_TEMPLATE_NAME_TO_DEALER2  as home_service_for_dealer
# from wellnet.settings import DEFAULT_FROM_EMAIL as from_email
from wkhtmltopdf.views import PDFTemplateResponse

from .common import get_msg_template_var_from_tmpl
from .common import send_message
from .forms import BookingServiceForm
from .reports import *

from_email = 'kishan@forktechnologies.com'
dealer_network_temp_cust = ''
home_service_for_cust = ''
dealer_network_temp_for_delaer = ''
home_service_for_dealer = ''

logger = logging.getLogger(__name__)


def get_model_list():

    from django.apps import apps
    myapp = apps.get_app_config('services')
    for index, model in enumerate(myapp.models):
        print(model)
    return []


class CascadAutoResponseView(BaseListView):
    filter_val = None
    filter_model = None

    def get(self, request, *args, **kwargs):
        self.widget = self.get_widget_or_404()
        self.term = kwargs.get('term', request.GET.get('term', ''))
        self.filter_val = kwargs.get('filter_val', request.GET.get('filter_val', ''))
        self.filter_model = kwargs.get('filter_model', request.GET.get('filter_model', ''))
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        return JsonResponse({
            'results': [
                {
                    'text': smart_text(obj),
                    'id': obj.pk,
                }
                for obj in context['object_list']
                ],
            'more': context['page_obj'].has_next()
        })

    def get_queryset(self):
        """Get queryset from cached widget."""
        return self.widget.filter_queryset(self.term, self.filter_model, self.filter_val, self.queryset)

    def get_paginate_by(self, queryset):
        return self.widget.max_results

    def get_widget_or_404(self):
        field_id = self.kwargs.get('field_id', self.request.GET.get('field_id', None))
        if not field_id:
            raise Http404('No "field_id" provided.')
        try:
            key = signing.loads(field_id)
        except BadSignature:
            raise Http404('Invalid "field_id".')
        else:
            cache_key = '%s%s' % (settings.SELECT2_CACHE_PREFIX, key)
            widget_dict = cache.get(cache_key)
            if widget_dict is None:
                raise Http404('field_id not found')
        qs, qs.query = widget_dict.pop('queryset')
        self.queryset = qs.all()
        widget_dict['queryset'] = self.queryset
        widget_cls = widget_dict.pop('cls')
        return widget_cls(**widget_dict)


@login_required
def totalAmountForProduct(request):
    data = {'amount': 0}
    amt = Decimal(0)
    total_amt = Decimal(0)
    igst_total_amt = Decimal(0)
    service_tax = Decimal(0)
    service_tax_total = Decimal(0)
    vat = Decimal(0)
    vat_total = Decimal(0)
    igst_total = Decimal(0)
    gross = Decimal(0)
    amount_array = []
    tax_ids_array = []
    part = None
    if 'products[]' in request.GET:
        products = request.GET.getlist('products[]')
        quantities = request.GET.getlist('quantities[]')
        base_prices = request.GET.getlist('base_prices[]')
        ids = request.GET.getlist('ids[]')
        tax_ids = request.GET.getlist('tax_ids[]')
        createdFor = request.GET.getlist('createdFor')
        for index, product in enumerate(products):
            tax = Tax.objects.filter(active=True, product__pk=product)[0]
            # price = ProductPrice.objects.filter(product__pk=product, active=True)
            # if createdFor[0] != '0':
            #     partner = BaseUser.objects.filter(pk=createdFor[0])[0]
            #     part = partner.groups.values_list('id', flat=True)
            # else:
            #     part = request.user.groups.values_list('id', flat=True)
            # price = price.filter(user_group=part[0])[0]

            amt = int(quantities[index]) * Decimal(base_prices[index] if base_prices else 0)
            amount_array.append({ids[index]: amt})

            for taxid in tax_ids:
                if str(index) in taxid:
                    if "CGST" in taxid or "SGST" in taxid:
                        tax_ids_array.append({taxid: tax.CGST_percentage})
                    elif "IGST" in taxid:
                        tax_ids_array.append({taxid: tax.IGST_percentage})
            service_tax = tax.SGST_percentage * amt / 100
            service_tax_total += service_tax
            vat = tax.CGST_percentage * amt / 100
            vat_total += vat
            igst = tax.IGST_percentage * amt / 100
            igst_total += igst
            gross += amt
            total_amt = total_amt + amt + service_tax + vat
            igst_total_amt = igst_total_amt + amt + igst
        data = {'gross': Decimal(gross).quantize(Decimal('0.01'), rounding=ROUND_DOWN),
                'amount': Decimal(total_amt).quantize(Decimal('.01'), rounding=ROUND_DOWN),
                'igst_total_amt': Decimal(igst_total_amt).quantize(Decimal('.01'), rounding=ROUND_DOWN),
                'sgst': Decimal(tax.SGST_percentage).quantize(Decimal('.01'), rounding=ROUND_DOWN),
                'cgst': Decimal(tax.CGST_percentage).quantize(Decimal('.01'), rounding=ROUND_DOWN),
                'igst': Decimal(tax.SGST_percentage + tax.CGST_percentage).quantize(Decimal('.01'),
                                                                                    rounding=ROUND_DOWN),
                'SGST_amount': Decimal(service_tax_total).quantize(Decimal('.01'), rounding=ROUND_DOWN),
                'CGST_amount': Decimal(vat_total).quantize(Decimal('.01'), rounding=ROUND_DOWN),
                'IGST_amount': Decimal(igst_total).quantize(Decimal('.01'), rounding=ROUND_DOWN),
                'product_amounts': amount_array, 'tax_amt_array': tax_ids_array}
    return JsonResponse(data)


def getProductsAmount(products, quantities):
    data = {'amount': 0}
    amt = Decimal(0)
    total_amt = Decimal(0)
    c = Decimal(0)
    service_tax_total = Decimal(0)
    vat = Decimal(0)
    vat_total = Decimal(0)
    for index, product in enumerate(products):
        tax = Tax.objects.filter(active=True, product__pk=product)[0]
        price = ProductPrice.objects.filter(product__pk=product, active=True)[0]
        amt = int(quantities[index]) * price.base_price
        service_tax = tax.SGST_percentage * amt / 100
        service_tax_total = service_tax_total + service_tax
        vat = tax.CGST_percentage * amt / 100
        vat_total = vat_total + vat
        total_amt = total_amt + amt + service_tax + vat
    data = {'amount': Decimal(total_amt).quantize(Decimal('.01'), rounding=ROUND_DOWN),
            'SGST_amount': Decimal(service_tax_total).quantize(Decimal('.01'), rounding=ROUND_DOWN),
            'CGST_amount': Decimal(vat_total).quantize(Decimal('.01'), rounding=ROUND_DOWN)}
    return data


@login_required
def totalAmountForCustomerProduct(request):
    data = {'amount': 0}
    amt = Decimal(0)
    SGST_amount = Decimal(0)
    CGST_amount = Decimal(0)
    gross = Decimal(0)
    amount_array = []
    if 'products[]' in request.GET and 'segment' in request.GET:
        segment = request.GET.getlist('segment')
        vehicle_category = request.GET.getlist('vehicle_category')
        products = request.GET.getlist('products[]')
        quantities = request.GET.getlist('quantities[]')
        # Totals count be sent, if sent (means user override) use it, else calculate using base price
        totals = request.GET.getlist('totals[]')
        ids = request.GET.getlist('ids[]')
        for index, product in enumerate(products):
            tax = Tax.objects.filter(active=True, product__pk=product)
            if tax:
                price = None
                if int(segment[0]) == 0 or product == '2':
                    price = ProductSegmentPrice.objects.filter(product__pk=product, active=True)
                elif int(segment[0]) != 5:
                    price = ProductSegmentPrice.objects.filter(product__pk=product, segment__pk=segment[0], active=True)
                elif int(segment[0]) == 5 and int(vehicle_category[0]) != 0:
                    price = ProductSegmentPrice.objects.filter(product__pk=product, segment__pk=segment[0],
                                                               vehicle_category=vehicle_category[0], active=True)
                if price:
                    # if we have a valid total, use it, else calculate it
                    gross_amt = -1
                    try:
                        if totals and index < len(totals) and eval(totals[index]) > 0:
                            gross_amt = Decimal(totals[index])
                    except Exception as ec:
                        # In case we run into any number conversion, just ignore what came and re-calculate
                        pass
                    if gross_amt == -1:
                        gross_amt = int(quantities[index]) * price[0].base_price

                    amount_array.append({ids[index]: gross_amt})
                    gross += gross_amt
                    amt += gross_amt
                    gross_service_tax = tax[0].SGST_percentage * gross_amt / 100
                    SGST_amount += gross_service_tax
                    gross_vat = tax[0].CGST_percentage * gross_amt / 100
                    CGST_amount += gross_vat
                    # amt = amt + gross_service_tax + gross_vat
                else:
                    data[
                        'error'] = "Price for this product and segment combination is not available. Contact Sales Team."
            else:
                data['error'] = "Tax for this product is not available. Contact Sales Team."
        data = {'gross': Decimal(gross).quantize(Decimal('0.01'), rounding=ROUND_DOWN),
                'amount': Decimal(amt).quantize(Decimal('.01'), rounding=ROUND_DOWN),
                'service_tax': Decimal(SGST_amount).quantize(Decimal('.01'), rounding=ROUND_DOWN),
                'vat': Decimal(CGST_amount).quantize(Decimal('.01'), rounding=ROUND_DOWN),
                'product_amounts': amount_array}
    return JsonResponse(data)


def pdf_view(request):
    templateVars = {
        'title': 'Invoice',
        'company_name': 'CP1',
        'owner_name': 'CP1',
        'company_address': 'ABC Road',
        'invoice_number': '000001',
        'invoice_date': '18/12/2015',
        'invoice_amount': '17970.00',
        'invoice_products': [
            {
                'description': 'Bactakleen',
                'unit_cost': 10,
                'quantity': 1500,
                'CGST_percentage': '4.00',
                'vat': '620.00',
                'total_amount': '17720.00',
            }
        ],
        'total_amount': '17720.00',
        'service_tax': '14.50',
        'service_taxable': '15000.00',
        'service_tax_total': '250.00',
        'grand_total': '17970.00',
    }
    # daily_reporting()
    return render_to_response('admin/inventory_invoice.html', templateVars, context_instance=RequestContext(request))


def savePDF(request):
    templateVars = {
        'title': 'Invoice',
        'company_name': 'CP1',
        'owner_name': 'CP1',
        'company_address': 'ABC Road',
        'invoice_number': '000001',
        'invoice_date': '18/12/2015',
        'invoice_amount': '17970.00',
        'invoice_products': [
            {
                'description': 'Bactakleen',
                'unit_cost': 10,
                'quantity': 1500,
                'CGST_percentage': '4.00',
                'vat': '620.00',
                'total_amount': '17720.00',
            }
        ],
        'total_amount': '17720.00',
        'service_tax': '14.50',
        'service_taxable': '15000.00',
        'service_tax_total': '250.00',
        'grand_total': '17970.00',
    }
    response = PDFTemplateResponse(
        request=request,
        template='admin/invoice.html',
        filename='invoice.pdf',
        context=templateVars,
        cmd_options={'load-error-handling': 'ignore'})
    mail = EmailMessage("Test", "Content", from_email, ['prakash2kool@gmail.com'])
    mail.attach('invoice.pdf', response.rendered_content, 'application/pdf')
    mail.send()
    return JsonResponse({'success': 'Yeyyy!!'})


def sendCPInvoice(request, invoice, toUser, send_email=False, pro_form=False):
    owner = PartnerAsOwner.objects.filter(partner__id=toUser.pk)[0]
    templateVars = {
        'title': 'Invoice',
        'company_name': toUser.company_name,
        'company_name_for_invoice': toUser.company_name_invoice,
        'dealer_code': toUser.dealer_code,
        'pin_code': toUser.pin_code,
        'city': "Bangalore",
        'u_state': toUser.state.name,
        'u_city': toUser.city.name,
        'owner_name': owner.name,
        'company_address': toUser.company_address,
        'invoice_number': invoice.id,
        'registration_number': toUser.GSTIN.upper(),
        'is_pro_forma': pro_form,
        'invoice_date': invoice.created_date,
        'IGST_amount_total': invoice.IGST_amount,
        'CGST_amount_total': invoice.CGST_amount,
        'SGST_amount_total': invoice.SGST_amount,
        'invoice_amount': invoice.amount,
        'total_amount': invoice.amount,
        'purchase_order_no': invoice.purchase_order_number if hasattr(invoice, 'purchase_order_number') else None
    }
    if not pro_form:
        prods = ProductQuantity.objects.filter(booking_id=invoice.pk)
        invoice_products = []
        for pq in prods:
            prod = {}
            prod['description'] = pq.product.description
            prod['HSN_code'] = pq.product.HSN_code
            prod['unit_cost'] = pq.base_price
            prod['quantity'] = pq.quantity
            prod['CGST_percentage'] = pq.CGST_percentage
            prod['CGST_amount'] = pq.CGST_amount
            prod['SGST_percentage'] = pq.SGST_percentage
            prod['SGST_amount'] = pq.SGST_amount
            prod['IGST_percentage'] = pq.IGST_percentage
            prod['IGST_amount'] = pq.IGST_amount
            prod['total_amount'] = pq.amount
            prod['total_amount_igst'] = pq.amount_igst
            invoice_products.append(prod)
        templateVars['invoice_products'] = invoice_products
        templateVars['grand_total'] = invoice.amount
    else:
        prods = ProFormaProductQuantity.objects.filter(booking_id=invoice.pk)
        invoice_products = []
        for pq in prods:
            prod = {}
            prod['description'] = pq.product.description
            prod['HSN_code'] = pq.product.HSN_code
            prod['unit_cost'] = pq.base_price
            prod['quantity'] = pq.quantity
            prod['CGST_percentage'] = pq.CGST_percentage
            prod['CGST_amount'] = pq.CGST_amount
            prod['SGST_percentage'] = pq.SGST_percentage
            prod['SGST_amount'] = pq.SGST_amount
            prod['IGST_percentage'] = pq.IGST_percentage
            prod['IGST_amount'] = pq.IGST_amount
            prod['total_amount'] = pq.amount
            prod['total_amount_igst'] = pq.amount_igst
            invoice_products.append(prod)
        templateVars['invoice_products'] = invoice_products
        templateVars['grand_total'] = invoice.amount
    if not pro_form:
        file_name = 'invoice_{}_{}.pdf'.format(invoice.id, invoice.updated)
    else:
        file_name = 'pro_forma_invoice_{}_{}.pdf'.format(invoice.id, invoice.updated)
    if invoice.is_IGST:
        pdf_response = PDFTemplateResponse(
            request=request,
            template='admin/invoiceIGST.html',
            filename=file_name,
            context=templateVars,
            cmd_options={'load-error-handling': 'ignore'})
    else:
        pdf_response = PDFTemplateResponse(
            request=request,
            template='admin/invoiceGST.html',
            filename=file_name,
            context=templateVars,
            cmd_options={'load-error-handling': 'ignore'})

    partner = PartnerBranch.objects.filter(partner=toUser.pk)
    email_id = None
    name = None
    to_emails = []
    if partner:
        email_id = partner[0].authorized_person_email
        name = partner[0].authorized_person_name
    else:
        email_id = toUser.email
        name = owner.name
    to_emails.append(email_id)
    if toUser.finance_department_email:
        to_emails.append(toUser.finance_department_email)
    if toUser.parts_department_email:
        to_emails.append(toUser.parts_department_email)
    if send_email:
        if not pro_form:
            ## TODO: Use text template to fit in data, this is ugly patch
            subject = "Invoice of your Booking in WellNet"
            content = 'Dear %s,\n' % name
            content = content + 'We are pleased to inform you that following items in your Order# %s' % invoice.id
            content = content + ' have been Confirmed and will be delivered to you on or before %s.' % invoice.expected_delivery_date.strftime(
                "%d-%m-%Y")
            content = content + '\n\nAs a part of go-green initiative we will not be sending the invoice to you with the shipment. \
            For your reference find soft copy of the invoice attached along with this mail.\n\nRegards,\nWellnet Team'
        else:
            ## TODO: Use text template to fit in data, this is ugly patch
            ## For Proform invoice email body
            subject = "Pro-Forma Invoice of your Booking in WellNet"
            content = 'Dear %s,\n' % name
            content = content + "We are pleased to provide you a pro forma Invoice for your enquiry."
            content = content + ' Please note that this is a pro forma invoice only, meant to provide you an estimate. The final invoice will be generated based on your actual purchase order.'
            content = content + '\n\nAs a part of go-green initiative we will not be sending the hard copy of the pro forma invoice. \
            For your reference find soft copy of the pro forma invoice attached along with this mail.\n\nRegards,\nWellnet Team'

        cc = ["sridhar@wellnetservices.com", "anil@wellnetservices.com", "udayabhaskar@wellnetservices.com"]
        if toUser.manager.email not in cc:
            cc.append(toUser.manager.email)
        mail = EmailMessage(subject, content, from_email, to_emails, cc=cc)
        mail.attach(file_name, pdf_response.rendered_content, 'application/pdf')
        try:
            mail.send()
        except:
            logger.error("Error sending mail to {} for order {}".format(toUser.email, invoice.id))
    response = HttpResponse(pdf_response.rendered_content, content_type="application/pdf")
    response['Content-Disposition'] = 'attachment; filename={}'.format(file_name)
    return response


@login_required
def download_pdf(request, id):
    channelpartner = None
    invoice = Booking.objects.filter(pk=id)[0] if Booking.objects.filter(pk=id) else  None
    l = request.user.groups.values_list('name', flat=True)
    if 'SuperAdmin' in l or 'EmployeeGroup' in l:
        if invoice:
            l = request.user.groups.values_list('name', flat=True)
            if 'ChannelPartnerGroup' in l:
                channelpartner = ChannelPartner.objects.get(pk=request.user.pk)
            else:
                channelpartner = invoice.createdFor

            owner = PartnerAsOwner.objects.filter(partner__id=channelpartner.pk)[0]
            templateVars = {
                'title': 'Invoice',
                'company_name': channelpartner.company_name,
                'company_name_for_invoice': channelpartner.company_name_invoice,
                'city': "Bangalore",
                'u_state': channelpartner.state.name,
                'u_city': channelpartner.city.name,
                'pin_code': channelpartner.pin_code,
                'dealer_code': channelpartner.dealer_code,
                'owner_name': owner.name,
                'company_address': channelpartner.company_address,
                'registration_number': channelpartner.GSTIN.upper(),
                'invoice_number': invoice.id,
                'invoice_date': invoice.created_date,
                'IGST_amount_total': invoice.IGST_amount,
                'CGST_amount_total': invoice.CGST_amount,
                'SGST_amount_total': invoice.SGST_amount,
                'invoice_amount': invoice.amount,
                'total_amount': invoice.amount,
                'purchase_order_no': invoice.purchase_order_number if hasattr(invoice,
                                                                              'purchase_order_number') else None

            }
            prods = ProductQuantity.objects.filter(booking_id=invoice.pk)
            invoice_products = []
            for pq in prods:
                prod = {}
                prod['description'] = pq.product.description
                prod['HSN_code'] = pq.product.HSN_code
                prod['unit_cost'] = pq.base_price
                prod['quantity'] = pq.quantity
                prod['CGST_percentage'] = pq.CGST_percentage
                prod['CGST_amount'] = pq.CGST_amount
                prod['SGST_percentage'] = pq.SGST_percentage
                prod['SGST_amount'] = pq.SGST_amount
                prod['IGST_percentage'] = pq.IGST_percentage
                prod['IGST_amount'] = pq.IGST_amount
                prod['total_amount'] = pq.amount
                prod['total_amount_igst'] = pq.amount_igst

                invoice_products.append(prod)
            templateVars['invoice_products'] = invoice_products
            templateVars['grand_total'] = invoice.amount
            file_name = 'invoice_{}_{}.pdf'.format(invoice.id, invoice.updated)
            if invoice.is_IGST:
                pdf_response = PDFTemplateResponse(
                    request=request,
                    template='admin/invoiceIGST.html',
                    filename=file_name,
                    context=templateVars,
                    cmd_options={'load-error-handling': 'ignore'})
            else:
                pdf_response = PDFTemplateResponse(
                    request=request,
                    template='admin/invoiceGST.html',
                    filename=file_name,
                    context=templateVars,
                    cmd_options={'load-error-handling': 'ignore'})
            response = HttpResponse(pdf_response.rendered_content, content_type="application/pdf")
            response['Content-Disposition'] = 'attachment; filename={}'.format(file_name)
            return response
    else:
        return HttpResponseForbidden('<h1>403 Forbidden</h1>', content_type='text/html')


@login_required
def download_ProForma_pdf(request, id):
    channelpartner = None
    invoice = ProFormaBooking.objects.filter(pk=id)[0] if ProFormaBooking.objects.filter(pk=id) else  None
    l = request.user.groups.values_list('name', flat=True)
    if 'SuperAdmin' in l or 'EmployeeGroup' in l:
        if invoice:
            l = request.user.groups.values_list('name', flat=True)
            if 'ChannelPartnerGroup' in l:
                channelpartner = ChannelPartner.objects.get(pk=request.user.pk)
            else:
                channelpartner = invoice.created_For

            owner = PartnerAsOwner.objects.filter(partner__id=channelpartner.pk)[0]
            templateVars = {
                'title': 'Invoice',
                'company_name': channelpartner.company_name,
                'company_name_for_invoice': channelpartner.company_name_invoice,
                'dealer_code': channelpartner.dealer_code,
                'city': "Bangalore",
                'u_state': channelpartner.state.name,
                'u_city': channelpartner.city.name,
                'pin_code': channelpartner.pin_code,
                'owner_name': owner.name,
                'company_address': channelpartner.company_address,
                'is_pro_forma': True,
                'registration_number': channelpartner.GSTIN.upper(),
                'invoice_number': invoice.id,
                'invoice_date': invoice.created_date,
                'IGST_amount_total': invoice.IGST_amount,
                'CGST_amount_total': invoice.CGST_amount,
                'SGST_amount_total': invoice.SGST_amount,
                'invoice_amount': invoice.amount,
                'total_amount': invoice.amount
            }
            prods = ProFormaProductQuantity.objects.filter(booking_id=invoice.pk)
            invoice_products = []
            for pq in prods:
                prod = {}
                prod['description'] = pq.product.description
                prod['HSN_code'] = pq.product.HSN_code
                prod['unit_cost'] = pq.base_price
                prod['quantity'] = pq.quantity
                prod['CGST_percentage'] = pq.CGST_percentage
                prod['CGST_amount'] = pq.CGST_amount
                prod['SGST_percentage'] = pq.SGST_percentage
                prod['SGST_amount'] = pq.SGST_amount
                prod['IGST_percentage'] = pq.IGST_percentage
                prod['IGST_amount'] = pq.IGST_amount
                prod['total_amount'] = pq.amount
                prod['total_amount_igst'] = pq.amount_igst
                invoice_products.append(prod)
            templateVars['invoice_products'] = invoice_products
            templateVars['grand_total'] = invoice.amount
            file_name = 'pro-forma-invoice_{}_{}.pdf'.format(invoice.id, invoice.updated)
            if invoice.is_IGST:
                pdf_response = PDFTemplateResponse(
                    request=request,
                    template='admin/invoiceIGST.html',
                    filename=file_name,
                    context=templateVars,
                    cmd_options={'load-error-handling': 'ignore'})
            else:
                pdf_response = PDFTemplateResponse(
                    request=request,
                    template='admin/invoiceGST.html',
                    filename=file_name,
                    context=templateVars,
                    cmd_options={'load-error-handling': 'ignore'})
            response = HttpResponse(pdf_response.rendered_content, content_type="application/pdf")
            response['Content-Disposition'] = 'attachment; filename={}'.format(file_name)
            return response
    else:
        return HttpResponseForbidden('<h1>403 Forbidden</h1>', content_type='text/html')


@login_required
def download_receipt_pdf(request, id):
    channelpartner = None
    l = request.user.groups.values_list('name', flat=True)
    invoice = Booking.objects.filter(pk=id)[0] if Booking.objects.filter(pk=id) else None
    if "SuperAdmin" in l or 'EmployeeGroup' in l:
        if invoice.payment_type.description == "Credit Period" or (not invoice.realisation_date):
            return HttpResponseForbidden(
                '<h3>Please update the Payment Details(Online Transfer) and Delivery Info</h3>',
                content_type='text/html')
        if invoice:
            if 'ChannelPartnerGroup' in l:
                channelpartner = ChannelPartner.objects.get(pk=request.user.pk)
            else:
                channelpartner = invoice.createdFor
            owner = PartnerAsOwner.objects.filter(partner__id=channelpartner.pk)[0]
            payment_type = invoice.payment_type.description

            templateVars = {
                'title': 'Payment Receipt',
                'company_name': channelpartner.company_name,
                'company_name_for_invoice': channelpartner.company_name_invoice,
                'dealer_code': channelpartner.dealer_code,
                'owner_name': owner.name,
                'company_address': channelpartner.company_address,
                'city': "Bangalore",
                'u_state': channelpartner.state.name,
                'u_city': channelpartner.city.name,
                'pin_code': channelpartner.pin_code,
                'invoice_number': invoice.id,
                'invoice_date': invoice.created_date,
                'invoice_amount': invoice.amount,
                'total_amount': invoice.amount,
                'IGST_amount_total': invoice.IGST_amount,
                'CGST_amount_total': invoice.CGST_amount,
                'SGST_amount_total': invoice.SGST_amount,
                'registration_number': channelpartner.GSTIN.upper(),
                'receipt_date': invoice.updated,
                'payment_date': invoice.transfer_date,
                'payment_type': {'id': invoice.payment_type.id, 'description': invoice.payment_type.description},
                'payment_desc': invoice.utr_number if invoice.utr_number else "NA",
                'bank_name': invoice.bank_name,
                'purchase_order_no': invoice.purchase_order_number if hasattr(invoice,
                                                                              'purchase_order_number') else None

            }
            if payment_type == "Online Transfer":
                templateVars['payment_desc'] = invoice.utr_number if invoice.utr_number else "NA"
                templateVars['receipt_date'] = invoice.realisation_date
            elif payment_type == "Cheque" or payment_type == "DD":
                templateVars['payment_desc'] = invoice.cheque_dd_number if invoice.cheque_dd_number else "NA"
                templateVars['receipt_date'] = invoice.realisation_date
            elif payment_type == "Credit Period":
                pass

            prods = ProductQuantity.objects.filter(booking_id=invoice.pk)
            invoice_products = []
            for pq in prods:
                prod = {}
                prod['description'] = pq.product.description
                prod['HSN_code'] = pq.product.HSN_code
                prod['unit_cost'] = pq.base_price
                prod['quantity'] = pq.quantity
                prod['CGST_percentage'] = pq.CGST_percentage
                prod['CGST_amount'] = pq.CGST_amount
                prod['SGST_percentage'] = pq.SGST_percentage
                prod['SGST_amount'] = pq.SGST_amount
                prod['IGST_percentage'] = pq.IGST_percentage
                prod['IGST_amount'] = pq.IGST_amount
                prod['total_amount'] = pq.amount
                prod['total_amount_igst'] = pq.amount_igst
                invoice_products.append(prod)
            templateVars['invoice_products'] = invoice_products
            templateVars['grand_total'] = invoice.amount
            instrument_number = ""
            if invoice.payment_type.id == 1 or invoice.payment_type.id == 2:  ##cheque or dd payment
                instrument_number = "Number {}, Date {}, Bank {}, Branch {}".format(invoice.cheque_dd_number,
                                                                                    invoice.cheque_dd_date,
                                                                                    invoice.bank_name,
                                                                                    invoice.bank_branch)
            elif invoice.payment_type.id == 3:
                instrument_number = "UTR No {}, Transfer Date {}, Bank {}, Branch {}".format(invoice.utr_number,
                                                                                             invoice.transfer_date,
                                                                                             invoice.bank_name,
                                                                                             invoice.bank_branch)
            templateVars['instrument_number'] = instrument_number
            file_name = 'receipt_{}_{}.pdf'.format(invoice.id, invoice.updated)
            if invoice.is_IGST:
                pdf_response = PDFTemplateResponse(
                    request=request,
                    template='admin/receiptIGST.html',
                    filename=file_name,
                    context=templateVars,
                    cmd_options={'load-error-handling': 'ignore'})
            else:
                pdf_response = PDFTemplateResponse(
                    request=request,
                    template='admin/receiptGST.html',
                    filename=file_name,
                    context=templateVars,
                    cmd_options={'load-error-handling': 'ignore'})

        response = HttpResponse(pdf_response.rendered_content, content_type="application/pdf")
        response['Content-Disposition'] = 'attachment; filename={}'.format(file_name)
        return response
    else:
        return HttpResponseForbidden('<h1>403 Forbidden</h1>', content_type='text/html')


def sendPODDetails(request, invoice, toUser, send_email=False):
    owner = PartnerAsOwner.objects.filter(partner__id=toUser.pk)[0]
    delivery_type = invoice.get_order_delivery_type_display()
    partner = PartnerBranch.objects.filter(partner=toUser.pk)
    email_id = None
    name = None
    if invoice.order_delivery_date:
        order_del_date = invoice.order_delivery_date.strftime("%d-%m-%Y")
    else:
        order_del_date = ''
    prods = ProductQuantity.objects.filter(booking_id=invoice.pk)
    invoice_products = []
    prod_details = ""
    for i, pq in enumerate(prods):
        prod_details += "{}. {}({})\n".format(i + 1, pq.product.description, pq.quantity)
    to_emails = []
    if partner:
        email_id = partner[0].authorized_person_email
        name = partner[0].authorized_person_name
    else:
        email_id = toUser.email
        name = owner.name
    to_emails.append(email_id)
    if toUser.finance_department_email:
        to_emails.append(toUser.finance_department_email)
    if toUser.parts_department_email:
        to_emails.append(toUser.parts_department_email)

    if send_email and invoice.transfer_date:
        ## TODO: Use text template to fit in data, this is ugly patch
        content = 'Dear %s,\n' % name

        if delivery_type.lower() == "courier":
            subject = "Dispatch details for booking {}.".format(invoice.id)
            content += "We are pleased to inform you on the dispatch of your booking number {}.".format(invoice.id)
            content = content + ' \n' + prod_details + ' through {} on {} bearing number {}'.format(
                invoice.courier_company_name, order_del_date, invoice.pod_number)
        elif delivery_type.lower() == "hand deliver":
            subject = "Delivery details for booking {}.".format(invoice.id)

            content += "We are pleased to inform you on the hand delivery of your booking number {}.".format(invoice.id)
            content = content + '\n 1. Delivered to:{} \n 2. Phone Number:{}'.format(invoice.person_name,
                                                                                     invoice.contact_number)
        else:
            subject = "Pick up details for booking {}.".format(invoice.id)
            content += "We are pleased to inform you on the successful pickup of your booking number {}.".format(invoice.id)
            content = content + '\n 1. Picked up by:{} \n 2. Phone Number:{}'.format(invoice.person_name,
                                                                                     invoice.contact_number)

        content = content + '\nDo email us on info@wellnetservices.com in case of any disconnect. \n\nRegards,\nWellnet Team'
        cc = ["sridhar@wellnetservices.com", "anil@wellnetservices.com", " udayabhaskar@wellnetservices.com"]
        if toUser.manager.email not in cc:
            cc.append(toUser.manager.email)
        mail = EmailMessage(subject, content, from_email, to_emails)
        try:
            mail.send()
        except:
            logger.error("Error sending mail to {} for order {}".format(toUser.email, invoice.id))
    return


def sendCPReceipt(request, invoice, toUser, send_email=False):
    owner = PartnerAsOwner.objects.filter(partner__id=toUser.pk)[0]
    payment_type = invoice.payment_type.description
    templateVars = {
        'title': 'Payment Receipt',
        'company_name': toUser.company_name,
        'owner_name': owner.name,
        'company_address': toUser.company_address,
        'company_name_for_invoice': toUser.company_name_invoice,
        'dealer_code': toUser.dealer_code,
        'city': "Bangalore",
        'u_state': toUser.state.name,
        'u_city': toUser.city.name,
        'invoice_number': invoice.id,
        'invoice_date': invoice.created_date,
        'invoice_amount': invoice.amount,
        'total_amount': invoice.amount,
        'IGST_amount_total': invoice.IGST_amount,
        'CGST_amount_total': invoice.CGST_amount,
        'SGST_amount_total': invoice.SGST_amount,
        'registration_number': toUser.GSTIN,
        'receipt_date': invoice.updated,
        'payment_date': invoice.transfer_date.strftime("%d-%m-%Y"),
        'payment_type': {'id': invoice.payment_type.id, 'description': invoice.payment_type.description},
        'payment_desc': invoice.utr_number if invoice.utr_number else "NA",
        'bank_name': invoice.bank_name,
        'purchase_order_no': invoice.purchase_order_number if hasattr(invoice, 'purchase_order_number') else None

    }
    if payment_type == "Online Transfer":
        templateVars['receipt_date'] = invoice.realisation_date
        templateVars['payment_desc'] = invoice.utr_number if invoice.utr_number else "NA"
    elif payment_type == "Cheque" or payment_type == "DD":
        templateVars['receipt_date'] = invoice.realisation_date
        templateVars['payment_desc'] = invoice.cheque_dd_number if invoice.cheque_dd_number else "NA"
    elif payment_type == "Credit Period":
        pass
    prods = ProductQuantity.objects.filter(booking_id=invoice.pk)
    invoice_products = []
    for pq in prods:
        prod = {}
        prod['description'] = pq.product.description
        prod['HSN_code'] = pq.product.HSN_code
        prod['unit_cost'] = pq.base_price
        prod['quantity'] = pq.quantity
        prod['CGST_percentage'] = pq.CGST_percentage
        prod['SGST_amount'] = pq.CGST_amount
        prod['SGST_percentage'] = pq.SGST_percentage
        prod['CGST_amount'] = pq.SGST_amount
        prod['total_amount'] = pq.amount
        prod['total_amount_igst'] = pq.amount_igst
        invoice_products.append(prod)
    templateVars['invoice_products'] = invoice_products
    templateVars['grand_total'] = invoice.amount
    instrument_number = ""
    if invoice.payment_type.id == 1 or invoice.payment_type.id == 2:  ##cheque or dd payment
        instrument_number = "Number {}, Date {}, Bank {}, Branch {}".format(invoice.cheque_dd_number,
                                                                            invoice.cheque_dd_date, invoice.bank_name,
                                                                            invoice.bank_branch)
    elif invoice.payment_type.id == 3:
        instrument_number = "UTR No {}, Transfer Date {}, Bank {}, Branch {}".format(invoice.utr_number,
                                                                                     invoice.transfer_date,
                                                                                     invoice.bank_name,
                                                                                     invoice.bank_branch)
    templateVars['instrument_number'] = instrument_number
    file_name = 'receipt_{}_{}.pdf'.format(invoice.id, invoice.updated)
    if invoice.is_IGST:
        pdf_response = PDFTemplateResponse(
            request=request,
            template='admin/receiptIGST.html',
            filename=file_name,
            context=templateVars,
            cmd_options={'load-error-handling': 'ignore'})
    else:
        pdf_response = PDFTemplateResponse(
            request=request,
            template='admin/receiptGST.html',
            filename=file_name,
            context=templateVars,
            cmd_options={'load-error-handling': 'ignore'})
    partner = PartnerBranch.objects.filter(partner=toUser.pk)
    email_id = None
    name = None
    to_emails = []
    if partner:
        email_id = partner[0].authorized_person_email
        name = partner[0].authorized_person_name
    else:
        email_id = toUser.email
        name = owner.name
    to_emails.append(email_id)
    if toUser.finance_department_email:
        to_emails.append(toUser.finance_department_email)
    if toUser.parts_department_email:
        to_emails.append(toUser.parts_department_email)
    if send_email and invoice.transfer_date:
        ## TODO: Use text template to fit in data, this is ugly patch
        subject = "Payment Receipt for Invoice#{} of your Booking in WellNet".format(invoice.id)
        content = 'Dear %s,\n' % name
        content = content + 'We are pleased to acknowledge receipt of your payment for  your Order# %s.' % invoice.id
        content = content + "It was pleasure doing business with you and looking forward for a long term association"
        content = content + '\n\nAs a part of go-green initiative we will not be sending hard copy of the receipt. For your reference, find soft copy of your receipt attached to this email. \n\nRegards,\nWellnet Team'

        cc = ["sridhar@wellnetservices.com", "anil@wellnetservices.com", "info@wellnetservices.com"]
        if toUser.manager.email not in cc:
            cc.append(toUser.manager.email)
        mail = EmailMessage(subject, content, from_email, [email_id], cc=cc)
        mail.attach(file_name, pdf_response.rendered_content, 'application/pdf')
        try:
            mail.send()
        except:
            logger.error("Error sending mail to {} for order {}".format(toUser.email, invoice.id))
    response = HttpResponse(pdf_response.rendered_content, content_type="application/pdf")
    response['Content-Disposition'] = 'attachment; filename={}'.format(file_name)
    return response


def sendInventoryInvoice(request, invoice):
    toUser = invoice.partner
    owner = PartnerAsOwner.objects.filter(partner__id=toUser.pk)[0]
    templateVars = {
        'title': 'Invoice',
        'company_name': toUser.company_name,
        'owner_name': owner.name,
        'company_address': toUser.company_address,
        'invoice_number': invoice.id,
        'invoice_date': invoice.created_date,
        'invoice_amount': invoice.security_deposite_amount,
        'total_amount': invoice.security_deposite_amount
    }
    invoice_products = []
    prod = {}
    prod['description'] = 'Security Deposite'
    prod['total_amount'] = invoice.security_deposite_amount
    invoice_products.append(prod)
    templateVars['invoice_products'] = invoice_products
    templateVars['grand_total'] = invoice.security_deposite_amount
    file_name = 'deposite_invoice_{}_{}.pdf'.format(invoice.id, invoice.updated)
    response = PDFTemplateResponse(
        request=request,
        template='admin/inventory_invoice.html',
        filename=file_name,
        context=templateVars,
        cmd_options={'load-error-handling': 'ignore'})
    ## TODO: Use text template to fit in data, this is ugly patch
    subject = "Invoice of your Deposite in WellNet"
    content = 'Dear %s,\n' % owner.name
    content = content + 'We are pleased to inform you that following items in your Deposite# %s' % invoice.id
    content = content + ' have been Confirmed and machine will be delivered to you on or before %s.' % invoice.delivery_date
    content = content + '\n\nAs a part of go-green initiative we will not be sending the invoice to you with the shipment. \
	For your reference find soft copy of the invoice attached along with this mail.\n\nRegards,\nWellnet Team'
    mail = EmailMessage(subject, content, from_email, [toUser.email])
    mail.attach(file_name, response.rendered_content, 'application/pdf')
    try:
        mail.send()
    except:
        logger.error("Error sending mail to {} for order {}".format(toUser.email, invoice.id))


def sendInventoryReceipt(request, invoice):
    toUser = invoice.partner
    owner = PartnerAsOwner.objects.filter(partner__id=toUser.pk)[0]
    templateVars = {
        'title': 'Payment Receipt',
        'company_name': toUser.company_name,
        'city': toUser.city.name,
        'owner_name': owner.name,
        'company_address': toUser.company_address,
        'invoice_number': invoice.id,
        'invoice_date': invoice.created_date,
        'invoice_amount': invoice.security_deposite_amount,
        'total_amount': invoice.security_deposite_amount,
        'registration_number': toUser.GSTIN,
        'receipt_date': invoice.updated,
        'payment_date': invoice.transfer_date,
        'payment_type': {'id': invoice.payment_type.id, 'description': invoice.payment_type.description}
    }
    prods = ProductQuantity.objects.filter(booking_id=invoice.pk)
    invoice_products = []
    prod = {}
    prod['description'] = "Security Deposite"
    prod['amount_paid'] = invoice.security_deposite_amount
    prod['total_amount'] = invoice.security_deposite_amount
    invoice_products.append(prod)
    templateVars['invoice_products'] = invoice_products
    templateVars['grand_total'] = invoice.security_deposite_amount
    instrument_number = ""
    if invoice.payment_type.id == 1 or invoice.payment_type.id == 2:  ##cheque or dd payment
        instrument_number = "Number {}, Date {}, Bank {}, Branch {}".format(invoice.cheque_dd_number,
                                                                            invoice.cheque_dd_date, invoice.bank_name,
                                                                            invoice.bank_branch)
    elif invoice.payment_type.id == 3:
        instrument_number = "UTR No {}, Transfer Date {}, Bank {}, Branch {}".format(invoice.utr_number,
                                                                                     invoice.transfer_date,
                                                                                     invoice.bank_name,
                                                                                     invoice.bank_branch)
    templateVars['instrument_number'] = instrument_number
    file_name = 'receipt_{}_{}.pdf'.format(invoice.id, invoice.updated)
    response = PDFTemplateResponse(
        request=request,
        template='admin/inventory_receipt.html',
        filename=file_name,
        context=templateVars,
        cmd_options={'load-error-handling': 'ignore'})
    ## TODO: Use text template to fit in data, this is ugly patch
    subject = "Receipt for Invoice#{} of your Booking in WellNet".format(invoice.id)
    content = 'Dear %s,\n' % owner.name
    content = content + 'We are pleased to inform you that payment against your Deposite# %s' % invoice.id
    content = content + ' has been received by us.'
    content = content + '\n\nAs a part of go-green initiative we will not be sending the hard copy of receipt to you with the shipment. For your reference find soft copy of the receipt attached along with this mail.\n\nRegards,\nWellnet Team'
    mail = EmailMessage(subject, content, from_email, [toUser.email])
    mail.attach(file_name, response.rendered_content, 'application/pdf')
    try:
        mail.send()
    except:
        logger.error("Error sending mail to {} for order {}".format(toUser.email, invoice.id))


def sendSettlementReceipt(request, invoice):
    toUser = invoice.partner
    owner = PartnerAsOwner.objects.filter(partner__id=toUser.pk)[0]
    templateVars = {
        'title': 'Payment Receipt',
        'company_name': toUser.company_name,
        'owner_name': owner.name,
        'company_address': toUser.company_address,
        'invoice_number': invoice.id,
        'invoice_date': invoice.created_date,
        'invoice_amount': invoice.security_deposite_amount,
        'total_amount': invoice.security_deposite_amount,
        'registration_number': toUser.GSTIN,
        'receipt_date': invoice.updated,
        'payment_date': invoice.transfer_date,
        'payment_type': {'id': invoice.payment_type.id, 'description': invoice.payment_type.description}
    }

    prods = ProductQuantity.objects.filter(booking_id=invoice.pk)
    invoice_products = []
    prod = {}
    prod['description'] = "Security Deposite"
    prod['amount_paid'] = invoice.security_deposite_amount
    prod['total_amount'] = invoice.security_deposite_amount
    invoice_products.append(prod)
    templateVars['invoice_products'] = invoice_products
    templateVars['grand_total'] = invoice.security_deposite_amount
    instrument_number = ""
    if invoice.payment_type.id == 1 or invoice.payment_type.id == 2:  ##cheque or dd payment
        instrument_number = "Number {}, Date {}, Bank {}, Branch {}".format(invoice.cheque_dd_number,
                                                                            invoice.cheque_dd_date, invoice.bank_name,
                                                                            invoice.bank_branch)
    elif invoice.payment_type.id == 3:
        instrument_number = "UTR No {}, Transfer Date {}, Bank {}, Branch {}".format(invoice.utr_number,
                                                                                     invoice.transfer_date,
                                                                                     invoice.bank_name,
                                                                                     invoice.bank_branch)
    templateVars['instrument_number'] = instrument_number
    file_name = 'receipt_{}_{}.pdf'.format(invoice.id, invoice.updated)
    response = PDFTemplateResponse(
        request=request,
        template='admin/inventory_receipt.html',
        filename=file_name,
        context=templateVars,
        cmd_options={'load-error-handling': 'ignore'})
    ## TODO: Use text template to fit in data, this is ugly patch
    subject = "Receipt for Invoice#{} of your Booking in WellNet".format(invoice.id)
    content = 'Dear %s,\n' % owner.name
    content = content + 'We are pleased to inform you that payment against your Deposite# %s' % invoice.id
    content = content + ' has been received by us.'
    content = content + '\n\nAs a part of go-green initiative we will not be sending the hard copy of receipt to you with the shipment. For your reference find soft copy of the receipt attached along with this mail.\n\nRegards,\nWellnet Team'
    mail = EmailMessage(subject, content, from_email, [toUser.email])
    mail.attach(file_name, response.rendered_content, 'application/pdf')
    try:
        mail.send()
    except:
        logger.error("Error sending mail to {} for order {}".format(toUser.email, invoice.id))


def bookService(request):
    try:
        if request.method == 'GET':
            form = BookingServiceForm()
            dealers = Dealers.objects.all()
            dealers = [{"id": x.id,
                        "company": x.company,
                        "category": x.category,
                        "service_area": x.service_area,
                        "area": x.area,
                        "address": x.address,
                        "authorised_person": x.authorised_person,
                        "phone": x.phone,
                        "email": x.email,
                        "map_link": x.map_link
                        } for x in dealers]

            return render_to_response('admin/booking_service_bactKleen.html', {'dealers': dealers, 'form': form, },
                                      context_instance=RequestContext(request))
        elif request.method == 'POST':
            booking_service_id = 0
            booking_service_id = BookingService.objects.count() + 1;
            area = 0
            total_amount = request.POST.get('total_amount')
            email = request.POST.get('email')
            firstname = request.POST.get('firstname')
            phone = request.POST.get('phone')
            address = ""
            landmark = ""
            city = ""
            payment_option = ""
            if request.POST.get('payment_options') == '1':
                payment_option = "Cash"
            dealer = None
            dealer_id = None
            if request.POST.get('dealer_doorstep') != "0" and request.POST.get('product') == '1':
                total_amount = 1400.000
                dealer_id = request.POST.get('dealer_doorstep')

            elif request.POST.get('dealer_network') != "0" and request.POST.get('product') == '1':
                total_amount = 1200.000
                dealer_id = request.POST.get('dealer_network')

            elif request.POST.get('home_dealer') != "0" and request.POST.get('product') == '2':
                dealer_id = request.POST.get('home_dealer')

            dealer = Dealers.objects.filter(id=dealer_id, is_active=True)[0]
            service_type = "{} ({})".format(dealer.category, dealer.service_area)
            booking_date = str(request.POST.get('booking_date'))
            new_booking = BookingService()
            new_booking.booking_service_id = booking_service_id
            new_booking.city = dealer.city
            new_booking.dealer = dealer.authorised_person
            new_booking.email = email
            new_booking.firstname = firstname
            new_booking.phone = phone
            new_booking.dealer_phone = dealer.phone
            new_booking.payment_option = payment_option
            new_booking.service_type = service_type
            new_booking.address = address
            new_booking.landmark = landmark
            new_booking.area = Decimal(area)
            new_booking.dealer_address = dealer.address
            new_booking.total_amount = Decimal(total_amount)
            new_booking.booking_date = datetime.datetime.strptime(booking_date, '%d/%m/%Y %H:%M:%S')
            #
            try:
                new_booking.save()
                data = {'status': 'SUCCESS',
                        'message': "Congratulations! You have successfully booked a Bactakleen service appointment with " +
                                   "{}.\nAddress: {} \nfor {}. The details of your service booking have been sent to your email address and phone.\n"
                                   "Thank you".format(dealer.authorised_person, new_booking.dealer_address,
                                                      str(new_booking.booking_date))}
            except Exception as e:
                data = {'status': 'Failure', 'message': "server error"}

            content = ""
            dealer_content = ""
            if dealer.category == "Car" and dealer.service_area == 'Dealer Network':
                content = 'Dear %s,\n' % new_booking.firstname
                content += 'We are pleased to inform you that your Bactakleen service for your %s has been successfully scheduled on %s.' % (
                    new_booking.service_type, new_booking.booking_date)
                content += 'Your service number is %s.' % new_booking.booking_service_id
                content += 'Please report to dealer address on %s.\n\n' % new_booking.booking_date
                content += 'Dealers Details:\n' \
                           'Name: {}\n Comapny Name: {} \n Address: {} \n Mobile no. {} \n Google-Map-Link: {}'.format(
                    dealer.authorised_person, dealer.company, dealer.address, dealer.phone,
                    dealer.map_link)

                content += '\n\nIn case of any issues, please feel free to contact\n Email-id:sridhar@wellnetservices.com and Mobile No: 9900544331'
                content += '\n\nRegards,\nWellnet Team'

                dealer_content = 'Dear %s,\n' % dealer.authorised_person
                dealer_content += 'We are pleased to inform you that  %s has booked a Bactakleen service for %s on %s.' % (
                    new_booking.firstname, new_booking.service_type, new_booking.booking_date)
                dealer_content += 'Your service number is %s.' % new_booking.booking_service_id
                dealer_content += 'The customer will report to your address on %s. Please service the request.\n\n' % new_booking.booking_date
                dealer_content += 'Customer Details:\n' \
                                  'Name: %s\n Email-id: %s \nMobile no. %s' % (
                                      new_booking.firstname, new_booking.email, new_booking.phone)
                dealer_content += '\n\nIn case of any issues, please feel free to contact\n Email-id:sridhar@wellnetservices.com and Mobile No: 9900544331'

                dealer_content = dealer_content + '\n\nRegards,\nWellnet Team'
                sms_template_name_cust = dealer_network_temp_cust
                sms_template_name_dealer = dealer_network_temp_for_delaer

                customer_mess_template = get_msg_template_var_from_tmpl(dealer_network_temp_cust)
                dealer_mess_template = get_msg_template_var_from_tmpl(dealer_network_temp_for_delaer)
                cust_kwargs = zip(customer_mess_template,
                                  [new_booking.firstname, str(new_booking.booking_date),
                                   re.sub('[#]', '', dealer.address),
                                   dealer.authorised_person, str(dealer.phone), str(dealer.map_link)])
                cust_kwargs = dict(cust_kwargs)
                dealer_kwargs = zip(dealer_mess_template,
                                    [dealer.authorised_person, new_booking.firstname, new_booking.booking_date, ])
                dealer_kwargs = dict(dealer_kwargs)

            elif dealer.category == "Car" and dealer.service_area == 'Door step service':

                content = 'Dear %s,\n' % new_booking.firstname
                content += 'We are pleased to inform you that your ' \
                           'Bactakleen service for your %s has been successfully scheduled on %s.' % (
                               new_booking.service_type, new_booking.booking_date)
                content += 'Your service number is %s.' % new_booking.booking_service_id
                content += ' Our service representative will report to your address on %s.\n\n' % new_booking.booking_date
                content += 'Your address:\n %s' % new_booking.address
                content += '\nDealers Details:\n' \
                           'Name: %s\n Comapny Name: %s \n Address: %s \n Mobile no. %s' % (
                               dealer.authorised_person, dealer.company, dealer.address,
                               dealer.phone,)
                content += '\n\nIn case of any issues, please feel free to contact\n Email-id:sridhar@wellnetservices.com and Mobile No: 9900544331'
                content += '\n\nRegards,\nWellnet Team'

                dealer_content = 'Dear %s,\n' % dealer.authorised_person
                dealer_content += 'We are pleased to inform you that  %s has booked a Bactakleen service for %s on %s.' % (
                    new_booking.firstname, new_booking.service_type, new_booking.booking_date)
                dealer_content += 'The service number is %s.' % new_booking.booking_service_id
                dealer_content += 'Please service the request at customer address on %s as per the below mentioned address. \n\n' % new_booking.booking_date
                dealer_content += 'Customer Details:\n' \
                                  'Name: %s\n Email-id: %s \n Mobile no. %s\n Address: %s' % (
                                      new_booking.firstname, new_booking.email, new_booking.phone,
                                      re.sub('[#]', '', new_booking.address))
                dealer_content += '\n\nIn case of any issues, please feel free to contact\n Email-id:sridhar@wellnetservices.com and Mobile No: 9900544331'

                dealer_content = dealer_content + '\n\nRegards,\nWellnet Team'
                sms_template_name_cust = home_service_for_cust
                sms_template_name_dealer = home_service_for_dealer
                customer_mess_template = get_msg_template_var_from_tmpl(home_service_for_cust)
                dealer_mess_template = get_msg_template_var_from_tmpl(home_service_for_dealer)
                cust_kwargs = zip(customer_mess_template,
                                  [new_booking.firstname, new_booking.service_type, dealer.authorised_person,
                                   dealer.phone,
                                   new_booking.service_type])
                cust_kwargs = dict(cust_kwargs)
                dealer_kwargs = zip(dealer_mess_template,
                                    [dealer.authorised_person, new_booking.firstname, str(new_booking.booking_date),
                                     re.sub('[#]', '', new_booking.address), str(new_booking.phone)])
                dealer_kwargs = dict(dealer_kwargs)

            else:

                content = 'Dear %s,\n' % new_booking.firstname
                content += 'We are pleased to inform you that your  Bactakleen service for your %s has been successfully scheduled on %s.' % (
                    new_booking.service_type, new_booking.booking_date)
                content += 'Your service number is %s.' % new_booking.booking_service_id
                content += ' Our service representative will report to your address on %s.\n\n' % new_booking.booking_date
                content += 'Your address:\n %s\n\n' % new_booking.address
                content += 'Dealers Details:\n' \
                           'Name: %s\n Comapny Name: %s \n Address: %s \n Mobile no. %s' % (
                               dealer.authorised_person, dealer.company, dealer.address,
                               dealer.phone,)
                content += '\n\nIn case of any issues, please feel free to contact\n Email-id:sridhar@wellnetservices.com and Mobile No: 9900544331'
                content += '\n\nRegards,\nWellnet Team'

                dealer_content = 'Dear %s,\n' % dealer.authorised_person
                dealer_content += 'We are pleased to inform you that  %s has booked a Bactakleen service for %s on %s.' % (
                    new_booking.firstname, new_booking.service_type, new_booking.booking_date)
                dealer_content += 'The service number is %s.' % new_booking.booking_service_id
                dealer_content += 'Please service the request at customer address on %s as per the below mentioned address.\n\n' % new_booking.booking_date
                dealer_content += 'Customer Details:\n\n' \
                                  'Name: %s\n Email-id: %s \n Mobile no. %s\n Address: %s' % (
                                      new_booking.firstname, new_booking.email, new_booking.phone, new_booking.address)
                dealer_content += '\n\nIn case of any issues, please feel free to contact\n Email-id:sridhar@wellnetservices.com and Mobile No: 9900544331'

                dealer_content += '\n\nRegards,\nWellnet Team'
                sms_template_name_cust = home_service_for_cust
                sms_template_name_dealer = home_service_for_dealer
                customer_mess_template = get_msg_template_var_from_tmpl(home_service_for_cust)
                dealer_mess_template = get_msg_template_var_from_tmpl(home_service_for_dealer)
                cust_kwargs = zip(customer_mess_template,
                                  [new_booking.firstname, new_booking.service_type, dealer.authorised_person,
                                   str(dealer.phone),
                                   new_booking.service_type])
                cust_kwargs = dict(cust_kwargs)
                dealer_kwargs = zip(dealer_mess_template,
                                    [dealer.authorised_person, new_booking.firstname, str(new_booking.booking_date),
                                     re.sub('[#]', '', new_booking.address), new_booking.phone])
                dealer_kwargs = dict(dealer_kwargs)

            r_c = send_message(new_booking.phone, msg_tmp_name=sms_template_name_cust, **cust_kwargs)
            r_d = send_message(dealer.phone, msg_tmp_name=sms_template_name_dealer,
                               **dealer_kwargs)
            if r_c != '200 OK':
                logger.error("Error sending sms to customer {} for booking {} date {}".format(new_booking.phone,
                                                                                              new_booking.booking_service_id,
                                                                                              new_booking.booking_date))
            if r_d != '200 OK':
                logger.error("Error sending sms to dealer {} for booking {} date {}".format(new_booking.phone,
                                                                                            new_booking.booking_service_id,
                                                                                            new_booking.booking_date))
            subject = "Service Booking in WellNet"
            mail = EmailMessage(subject, content, from_email, [new_booking.email])
            dealer_mail = EmailMessage(subject, dealer_content, from_email,
                                       ["sridhar@wellnetservices.com", dealer.email], )
            try:
                mail.send()
                dealer_mail.send()
            except:
                logger.error(
                    "Error sending mail to {} for order {}".format(new_booking.email, new_booking.booking_service_id))
                pass

            return JsonResponse(data)
        else:
            data = {'status': 'Failure', 'message': "server error"}
            return JsonResponse(data)
    except Exception as ec:
        data = {'status': 'Failure', 'message': "server error"}
        return JsonResponse(data)
