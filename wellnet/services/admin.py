import datetime
import logging

from django import forms
from django.contrib import admin
from django.contrib import messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.core.mail import send_mail
from django.db.models import Q
from django.db.models import Sum
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.translation import ugettext_lazy as _
from wellnet.settings import DEFAULT_FROM_EMAIL as from_email
# from ..wellnet.settings import DEFAULT_FROM_EMAIL as mail

from .common import send_customer_invoice_confirmation, send_partner_onboarding_confirmation
from .forms import ChannelPartnerForm, BookingForm, CustomerInvoiceForm, LeadForm, ProductQuantityForm, \
    CustomerProductQuantityForm, ChannelPartnerChangeForm, EmployeeChangeForm, EmployeeCreationForm, PartnerBranchForm, \
    PartnerAsOwnerForm, ProductSegmentPriceForm, ProductPriceForm, InventoryInvoiceForm, MachineForm, \
    BookingServiceForm, InventoryManagementForm, ProductForm, FieldEmployeesActivityReportForm, ExportXlsForm, \
    ReportsForm, CustomerForm, ProFormaBookingForm, ProFormaProductQuantityForm
from .forms import SupplierManagementForm
from .models import Employee, ChannelPartner, Customer, ChannelPartnerSegment, Lead, LeadStatus, \
    CustomerInvoice, Booking, ProductSegmentPrice, ProductQuantity, ProductPrice, CustomerProductQuantity, Tax, \
    MoreInfo, PartnerBranch, PartnerAsOwner, InventoryInvoice, Machine, BookingService, Dealers, DealersType, \
    SupplierManagement, \
    InventoryManagement, FieldEmployeesActivityReport, Product, State, City, PaymentType, ExportXls, Reports, \
    ProFormaBooking, ProFormaProductQuantity, BaseUser
from .reports import export_xls
from .views import sendCPInvoice, sendCPReceipt, sendInventoryInvoice, sendInventoryReceipt, sendPODDetails

logger = logging.getLogger(__name__)


# Register your models here.

class RequiredFormSet(forms.models.BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super(RequiredFormSet, self).__init__(*args, **kwargs)
        self.forms[0].empty_permitted = False

    def clean(self):
        super(RequiredFormSet, self).clean()
        count = 0
        product_types = []
        for form in self.forms:
            try:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    count += 1
                product = form.cleaned_data.get('product', None)
                if product:
                    if product in product_types:
                        raise forms.ValidationError(_('Change quantity instead of adding same product twice.'),
                                                    code='duplicate')
                    product_types.append(product)
                    if product.id == 1 and self.instance.segments == None:
                        raise forms.ValidationError(_('Segments is mandatory field.'), code='required')
            except AttributeError:
                pass
        if count < 1:
            raise forms.ValidationError(_('You must have at least one Product'), code='required')


class LeadAdmin(admin.ModelAdmin):
    form = LeadForm
    fieldsets = [
        (None, {'fields': ['customer_name', 'company_name', 'call_source', ]}),
        ('Contact info', {'fields': ['mobile_number', 'landline_number', 'city', 'address', 'pin_code']}),
        ('Status', {'fields': ['status', 'reason', 'more_details', 'next_appointment', 'comments']}),
        ('Other Details', {'fields': ['segments', 'product_demo']}),
        ('Onboarding Details', {
            'fields': ['channelpartner', 'registration_form', 'payment_collected', 'goods_delivered',
                       'cheque_dd_number']})
    ]
    list_display = ('customer_name', 'company_name', 'status')
    list_filter = ['updated']

    def get_queryset(self, request):
        qs = super(LeadAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        qs = qs.filter(createdBy=request.user)
        return qs

    def save_model(self, request, obj, form, change):
        if not change:
            obj.createdBy = request.user
        obj.updatedBy = request.user
        super(LeadAdmin, self).save_model(request, obj, form, change)


class PartnerBranchInline(admin.StackedInline):
    model = PartnerBranch
    form = PartnerBranchForm
    fieldsets = [(None, {'fields': ['branch_address', 'pin_code', 'state', 'city', 'landline']}),
                 ('Authorized Person', {
                     'fields': ['same_as_owner', 'authorized_person_name',
                                'authorized_person_gender',
                                'authorized_person_date_of_birth',
                                'authorized_person_landline', 'authorized_person_mobile_number',
                                'authorized_person_address', 'authorized_person_email']}),
                 ]
    min_num = 1
    extra = 0


class PartnerAsOwnerInline(admin.StackedInline):
    model = PartnerAsOwner
    form = PartnerAsOwnerForm
    min_num = 1
    max_num = 1


class ChannelPartnerAdmin(BaseUserAdmin):
    model = ChannelPartner
    form = ChannelPartnerChangeForm
    add_form = ChannelPartnerForm
    inlines = [PartnerAsOwnerInline, PartnerBranchInline]

    fieldsets = [
        ('Dealer Category', {'fields': ['dealership_category', 'dealer_code']}),
        # ('Create Dealer', {'fields': ['username', 'email', 'password', 'is_staff', 'is_active']}),
        ('Company Info', {
            'fields': ['company_name', 'company_name_invoice', 'segments', 'state', 'city', 'company_address',
                       'pin_code', 'landline']}),
        ('Other Details', {'fields': ['GSTIN', 'company_pan_number', 'number_of_staff', 'number_of_branches',
                                      'number_of_products', 'year_of_establishment', 'manager']}),
        ('Parts department', {'fields': ['parts_department_name', 'parts_department_phone', 'parts_department_email']}),
        ('Finance department',
         {'fields': ['finance_department_name', 'finance_department_phone', 'finance_department_email']})
    ]
    add_fieldsets = [
        ('Dealer Category', {'fields': ['dealership_category', 'dealer_code']}),
        # ('Create Dealer', {'fields': ['username', 'email', 'password1', 'password2', 'is_staff', 'is_active']}),
        ('Company Info', {
            'fields': ['company_name', 'company_name_invoice', 'segments', 'state', 'city', 'company_address',
                       'pin_code', 'landline']}),
        ('Other Details', {'fields': ['GSTIN', 'company_pan_number', 'number_of_staff', 'number_of_branches',
                                      'number_of_products', 'year_of_establishment', 'manager']}),
        ('Purchase department', {'fields': ['parts_department_name', 'parts_department_phone', 'parts_department_email']}),
        ('Finance department',
         {'fields': ['finance_department_name', 'finance_department_phone', 'finance_department_email']})
    ]
    list_display = ('id', 'company_name', 'dealer_code', 'landline', 'is_active')

    def get_queryset(self, request):
        qs = super(ChannelPartnerAdmin, self).get_queryset(request)
        l = request.user.groups.values_list('name', flat=True)
        if request.user.is_superuser or 'SuperAdmin' in l:
            return qs
        elif 'SubDealer' in l:
            emps = Employee.objects.filter(createdBy=request.user)
            qs = qs.filter(Q(createdBy=request.user) | Q(createdBy__in=emps))
        else:
            qs = qs.filter(createdBy=request.user)
        return qs

    def get_fieldsets(self, request, obj=None):
        fs = super(ChannelPartnerAdmin, self).get_fieldsets(request, obj)
        l = request.user.groups.values_list('name', flat=True)
        if (request.user.is_superuser or 'SuperAdmin' in l) and len(fs) == 3:
            fs += ('Permission', {'fields': ['is_sub_dealer']}),
        return fs

    def save_model(self, request, obj, form, change):
        reset = False
        password = get_random_string()
        if not change:
            obj.set_password(password)
            reset = True
            obj.createdBy = request.user
        super(ChannelPartnerAdmin, self).save_model(request, obj, form, change)
        if obj.is_sub_dealer:
            g = Group.objects.get(name='SubDealer')
        else:
            g = Group.objects.get(name='ChannelPartnerGroup')
        g.user_set.add(obj)
        # if reset:
        #     if obj.dealership_category.description != "OEs" or obj.dealership_category.description != "Service Provider":
        #         subject = 'Welcome to WellNet Services'
        #         message = """You are only a couple of steps away from completing your registration.
        #         Please note that this is a one-time password and you are requested to change the password and
        #         access your account with the below User ID and the new password in future.\n\nYour
        #         username: %s""" % obj.username
        #         message += """\nYour Password: %s""" % password
        #         message += """\nWe\'re glad you are here,\nWellnet Team"""
        #         from_addr = from_email
        #         recipient_list = (obj.email,)
        #         logger.info(message)
        #         try:
        #             send_mail(subject, message, from_addr, recipient_list)
        #         except:
        #             logger.error('Error sending email to {}'.format(obj.email))
        #             pass

    def save_related(self, request, form, formset, change):
        super(ChannelPartnerAdmin, self).save_related(request, form, formset, change)
        if not change:
            send_partner_onboarding_confirmation(form.instance)


class EmployeeAdmin(BaseUserAdmin):
    model = Employee
    form = EmployeeChangeForm
    add_form = EmployeeCreationForm
    add_fieldsets = [(None, {
        'fields': ['username', 'email', 'password1', 'password2', 'name', 'current_address', 'permanent_address',
                   'pan_number', 'aadhar_number', 'date_of_birth', 'hire_date', 'date_of_resignation', 'reason_for_resignation', 'is_active', 'is_staff']}),
                     ('Emergency Contact Person', {'fields': ['emergency_contact_name', 'emergency_contact_phone',
                                                              'emergency_contact_relation']}), ]
    fieldsets = [(None, {
        'fields': ['username', 'email', 'password', 'name', 'current_address', 'permanent_address', 'pan_number',
                   'aadhar_number', 'date_of_birth', 'hire_date', 'date_of_resignation', 'reason_for_resignation', 'is_active', 'is_staff']}),
                 ('Emergency Contact Person',
                  {'fields': ['emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relation']}), ]
    list_display = ('id', 'username', 'name', 'is_active')

    def get_queryset(self, request):
        qs = super(EmployeeAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        l = request.user.groups.values_list('name', flat=True)
        if 'SubDealer' in l:
            qs = qs.filter(createdBy=request.user)
        return qs

    def get_fieldsets(self, request, obj=None):
        fs = super(EmployeeAdmin, self).get_fieldsets(request, obj)
        l = request.user.groups.values_list('name', flat=True)
        if request.user.is_superuser and len(fs) == 2:
            fs += ('Permission', {'fields': ['is_admin']}),
        return fs

    def save_model(self, request, obj, form, change):
        reset = False
        password = get_random_string()
        if not change:
            obj.set_password(password)
            # obj.set_email(obj.username)
            reset = True
        if not change:
            obj.createdBy = request.user
        super(EmployeeAdmin, self).save_model(request, obj, form, change)
        if obj.is_admin:
            g = Group.objects.get(name='SuperAdmin')
        else:
            g = Group.objects.get(name='EmployeeGroup')
        g.user_set.add(obj)
        if reset:
            subject = 'Welcome to WellNet'
            message = 'Dear %s,' % obj.name
            message += '\nYou are only a couple of steps away from completing your \
            registration. Please note, this is a onetime password and your requested to change \
            the password and access your account with the below User ID and the new password in \
            future.\n\nYour username: %s' % obj.username
            message += '\nYour Password: %s' % password
            message += '\nWe\'re glad you are here,\nWellNet Team'
            from_addr = from_email
            recipient_list = (obj.email,)
            logger.info(message)
            try:
                send_mail(subject, message, from_addr, recipient_list)
            except:
                logger.error('Error sending email to {}'.format(obj.email))
                pass


class ProductQuantityInline(admin.TabularInline):
    model = ProductQuantity
    form = ProductQuantityForm
    formset = RequiredFormSet
    min_num = 1
    max_num = 10
    extra = 10


class CustomerProductQuantityInline(admin.TabularInline):
    model = CustomerProductQuantity
    form = CustomerProductQuantityForm
    formset = RequiredFormSet
    min_num = 1
    max_num = 3
    extra = 3


class BookingAdmin(admin.ModelAdmin):
    model = Booking
    form = BookingForm
    fieldsets = [
        (
            None,
            {'fields': ['is_IGST', 'is_immediate', 'purchase_order_number', 'expected_delivery_date',
                        'order_delivery_type', 'payment_type']}),
        ('Payment Details', {
            'fields': ['cheque_dd_number', 'cheque_dd_date', 'utr_number', 'transfer_date', 'bank_name', 'bank_branch',
                       'realisation_date']}),
        ('Delivery Info', {
            'fields': ['order_delivery_date', 'courier_company_name', 'pod_number', 'person_name', 'contact_number']}),
        ('Amount', {'fields': ['gross_amount', 'IGST_amount', 'SGST_amount', 'CGST_amount', 'amount']}),
        ('Cancellation Request', {'classes': ('collapse',), 'fields': ['is_cancelled', 'cancel_reason']}),

    ]
    inlines = [ProductQuantityInline, ]
    list_display = ('id', 'products', 'createdFor', 'payment_type', 'created_date', 'amount',
                    'download_invoice', 'download_receipt')
    search_fields = ['id', 'createdFor__username']

    def download_invoice(self, instance):
        return "<a href='/custom/services/booking/invoice/{}/'>Download Invoice</a>".format(instance.id)

    def download_receipt(self, instance):
        return "<a href='/custom/services/booking/receipt/%s/'>Download Receipt</a>" % (instance.id)

    download_invoice.allow_tags = True
    download_invoice.short_description = 'Invoice'
    download_receipt.allow_tags = True
    download_receipt.short_description = 'Receipt'

    def products(self, instance):
        pq = ProductQuantity.objects.filter(booking__pk=instance.pk)
        products = ""
        if pq:
            for p in pq:
                products = products + p.product.description + "({}),".format(p.quantity)
        return products

    products.short_description = 'Products'

    def get_form(self, request, *args, **kwargs):
        form = super(BookingAdmin, self).get_form(request, *args, **kwargs)
        form.request = request
        return form

    def get_fieldsets(self, request, obj=None):
        fs = super(BookingAdmin, self).get_fieldsets(request, obj)
        if request.user.is_superuser:
            self.readonly_fields = (
                'order_delivery_date', 'courier_company_name', 'pod_number', 'person_name', 'contact_number',
                'is_immediate', 'expected_delivery_date', 'order_delivery_type', 'payment_type', 'cheque_dd_number',
                'cheque_dd_date', 'utr_number', 'transfer_date', 'bank_name', 'bank_branch')
            self.inlines = []
            messages.warning(request, "You do not have permission to add Booking")
        else:
            self.inlines = [ProductQuantityInline, ]
            l = request.user.groups.values_list('name', flat=True)
            if obj is not None and obj.created_date > datetime.date.today() - datetime.timedelta(days=3):
                pass
            elif fs.__contains__(
                    ('Cancellation Request', {'classes': ('collapse',), 'fields': ['is_cancelled', 'cancel_reason']})):
                fs.remove(
                    ('Cancellation Request', {'classes': ('collapse',), 'fields': ['is_cancelled', 'cancel_reason']}))
            if obj is not None and 'SuperAdmin' in l:
                if fs.__contains__(('Cancellation Request',
                                    {'classes': ('collapse',), 'fields': ['is_cancelled', 'cancel_reason']})):
                    pass
                else:
                    fs.append(
                        ('Cancellation Request',
                         {'classes': ('collapse',), 'fields': ['is_cancelled', 'cancel_reason']}))

            if 'SubDealer' in l or 'EmployeeGroup' in l or 'SuperAdmin' in l:
                self.readonly_fields = []
                if not fs.__contains__(('Partner', {'fields': ['createdFor']})):
                    fs.append(('Partner', {'fields': ['createdFor']}))
            else:
                self.readonly_fields = ('order_delivery_date', 'courier_company_name', 'pod_number', 'send_receipt')
                if fs.__contains__(('Partner', {'fields': ['createdFor']})):
                    ## remove Parnter field
                    fs.remove(('Partner', {'fields': ['createdFor']}))
            if 'EmployeeGroup' in l or 'SuperAdmin' in l:
                if not fs.__contains__(('Receipt', {'fields': ['send_receipt', 'send_pod']})):
                    fs.append(('Receipt', {'fields': ['send_receipt', 'send_pod']}))
            elif fs.__contains__(('Receipt', {'fields': ['send_receipt', 'send_pod']})):
                fs.remove(('Receipt', {'fields': ['send_receipt', 'send_pod']}))

        return fs

    def get_queryset(self, request):
        qs = super(BookingAdmin, self).get_queryset(request)
        l = request.user.groups.values_list('name', flat=True)
        if request.user.is_superuser or 'SuperAdmin' in l:
            return qs
        if 'SubDealer' in l:
            emps = Employee.objects.filter(createdBy=request.user.pk)
            cps = ChannelPartner.objects.filter(Q(manager__in=emps) | Q(createdBy=request.user))
            qs = qs.filter(Q(createdFor__in=cps) | Q(createdBy=request.user))
        elif 'EmployeeGroup' in l or 'SuperAdmin' in l:
            emp = Employee.objects.get(pk=request.user.pk)
            cp = ChannelPartner.objects.filter(manager=emp)
            qs = qs.filter(Q(createdFor__in=cp) | Q(createdBy__in=cp) | Q(createdBy=request.user))
        else:
            qs = qs.filter(createdFor=request.user)
        return qs

    def save_model(self, request, obj, form, change):
        if not change:
            obj.createdBy = request.user
        obj.updatedBy = request.user
        l = request.user.groups.values_list('name', flat=True)
        if 'ChannelPartnerGroup' in l:
            obj.createdFor = ChannelPartner.objects.get(pk=request.user.pk)
        obj.updated = timezone.now()
        super(BookingAdmin, self).save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        super(BookingAdmin, self).save_formset(request, form, formset, change)
        l = request.user.groups.values_list('name', flat=True)
        if 'ChannelPartnerGroup' in l:
            channelpartner = ChannelPartner.objects.get(pk=request.user.pk)
        else:
            channelpartner = form.instance.createdFor
        if not change:
            sendCPInvoice(request, form.instance, channelpartner, send_email=True)
        else:
            if form.instance.send_receipt:
                sendCPReceipt(request, form.instance, channelpartner, send_email=True)
            if form.instance.send_pod:
                sendPODDetails(request, form.instance, channelpartner, send_email=True)
        form.instance.gross_amount = ProductQuantity.objects \
            .filter(booking=form.instance).aggregate(Sum('gross_amount'))['gross_amount__sum']
        form.instance.save()

    def save_related(self, request, form, formset, change):
        super(BookingAdmin, self).save_related(request, form, formset, change)
        if not change:
            ""
            # send_booking_confirmation(form.instance)
            pass


# pro forma
class ProFormaProductQuantityInline(admin.TabularInline):
    model = ProFormaProductQuantity
    form = ProFormaProductQuantityForm
    formset = RequiredFormSet
    min_num = 1
    max_num = 10
    extra = 10


class ProFormaBookingAdmin(admin.ModelAdmin):
    model = ProFormaBooking
    form = ProFormaBookingForm
    fieldsets = [
        (None, {'fields': ['is_IGST', ]}),
        ('Amount', {
            'fields': ['gross_amount', 'IGST_amount', 'SGST_amount', 'CGST_amount', 'amount']}),
        ('Cancellation Request', {'classes': ('collapse',), 'fields': ['is_cancelled', 'cancel_reason']}),
    ]
    inlines = [ProFormaProductQuantityInline, ]
    list_display = ('id', 'products', 'created_For', 'created_date', 'amount',
                    'download_invoice')
    search_fields = ['id', 'createdFor__username']

    def download_invoice(self, instance):
        return "<a href='/custom/services/booking/invoice/{}/proforma'>Download Pro Forma Invoice</a>".format(
            instance.id)

    download_invoice.allow_tags = True
    download_invoice.short_description = 'Invoice'

    def products(self, instance):
        pq = ProFormaProductQuantity.objects.filter(booking__pk=instance.pk)
        products = ""
        if pq:
            for p in pq:
                products = products + p.product.description + "({}),".format(p.quantity)
        return products

    products.short_description = 'Products'

    def get_form(self, request, *args, **kwargs):
        form = super(ProFormaBookingAdmin, self).get_form(request, *args, **kwargs)
        form.request = request
        return form

    def get_fieldsets(self, request, obj=None):
        fs = super(ProFormaBookingAdmin, self).get_fieldsets(request, obj)
        if request.user.is_superuser:
            self.inlines = []
            messages.warning(request, "You do not have permission to add Booking")
        else:
            self.inlines = [ProFormaProductQuantityInline, ]
            l = request.user.groups.values_list('name', flat=True)
            if obj is not None and obj.created_date > datetime.date.today() - datetime.timedelta(days=3):
                pass
            if 'EmployeeGroup' in l or 'SuperAdmin' in l:
                self.readonly_fields = []
                if not fs.__contains__(('Partner', {'fields': ['created_For']})):
                    fs.append(('Partner', {'fields': ['created_For']}))
            if obj is not None and 'SuperAdmin' in l:
                if fs.__contains__(('Cancellation Request',
                                    {'classes': ('collapse',), 'fields': ['is_cancelled', 'cancel_reason']})):
                    pass
                else:
                    fs.append(
                        ('Cancellation Request',
                         {'classes': ('collapse',), 'fields': ['is_cancelled', 'cancel_reason']}))
            else:
                if fs.__contains__(('Cancellation Request',
                                    {'classes': ('collapse',), 'fields': ['is_cancelled', 'cancel_reason']})):
                    fs.remove(
                        ('Cancellation Request',
                         {'classes': ('collapse',), 'fields': ['is_cancelled', 'cancel_reason']}))

                    # else:
                    #     if fs.__contains__(('Partner', {'fields': ['created_For']})):
                    #         ## remove Parnter field
                    #         fs.remove(('Partner', {'fields': ['created_For']}))
        return fs

    def get_queryset(self, request):
        qs = super(ProFormaBookingAdmin, self).get_queryset(request)
        l = request.user.groups.values_list('name', flat=True)
        if request.user.is_superuser or 'SuperAdmin' in l:
            return qs
        if 'SubDealer' in l:
            emps = Employee.objects.filter(createdBy=request.user.pk)
            cps = ChannelPartner.objects.filter(Q(manager__in=emps) | Q(createdBy=request.user))
            qs = qs.filter(Q(created_For__in=cps) | Q(createdBy=request.user))
        elif 'EmployeeGroup' in l or 'SuperAdmin' in l:
            emp = Employee.objects.get(pk=request.user.pk)
            cp = ChannelPartner.objects.filter(manager=emp)
            qs = qs.filter(Q(created_For__in=cp) | Q(createdBy__in=cp) | Q(createdBy=request.user))
        else:
            qs = qs.filter(created_For=request.user)
        return qs

    def save_model(self, request, obj, form, change):
        if not change:
            obj.createdBy = request.user
        obj.updated_By = request.user
        l = request.user.groups.values_list('name', flat=True)
        if 'ChannelPartnerGroup' in l:
            obj.created_For = ChannelPartner.objects.get(pk=request.user.pk)
        obj.updated = timezone.now()
        super(ProFormaBookingAdmin, self).save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        super(ProFormaBookingAdmin, self).save_formset(request, form, formset, change)
        l = request.user.groups.values_list('name', flat=True)
        if 'ChannelPartnerGroup' in l:
            channelpartner = ChannelPartner.objects.get(pk=request.user.pk)
        else:
            channelpartner = form.instance.created_For

        sendCPInvoice(request, form.instance, channelpartner, send_email=True, pro_form=True)
        form.instance.gross_amount = ProFormaProductQuantity.objects \
            .filter(booking=form.instance).aggregate(Sum('gross_amount'))['gross_amount__sum']
        form.instance.save()

    def save_related(self, request, form, formset, change):
        super(ProFormaBookingAdmin, self).save_related(request, form, formset, change)
        if not change:
            ""
            # send_booking_confirmation(form.instance)
            pass


class CustomerAdmin(admin.ModelAdmin):
    model = Customer
    form = CustomerForm
    list_display = ['id', 'first_name', ]
    user_fields = ['first_name', 'last_name', 'gender', 'mobile_number', 'email', 'address',
                   'pin_code']
    super_admin_field = ['createdBy']

    def get_form(self, request, *args, **kwargs):
        l = request.user.groups.values_list('name', flat=True)

        if request.user.is_superuser or 'SuperAdmin' in l:
            self.fields = self.user_fields + self.super_admin_field
        else:
            self.fields = self.user_fields
        return super(CustomerAdmin, self).get_form(request, *args, **kwargs)

    def get_queryset(self, request):
        qs = super(CustomerAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        l = request.user.groups.values_list('name', flat=True)
        if 'SubDealer' in l:
            qs = qs.filter(createdBy=request.user.pk)
        if 'ChannelPartnerGroup' in l:
            qs = qs.filter(createdBy=request.user.pk)
        return qs

    def save_model(self, request, obj, form, change):
        l = request.user.groups.values_list('name', flat=True)
        if not change:
            if 'ChannelPartnerGroup' in l:
                obj.createdBy = ChannelPartner.objects.filter(pk=request.user.pk)[0]
        super(CustomerAdmin, self).save_model(request, obj, form, change)


class CustomerInvoiceAdmin(admin.ModelAdmin):
    model = CustomerInvoice
    form = CustomerInvoiceForm
    fieldsets = [
        (None, {'fields': ['user']}),
        ('Payment Details', {
            'fields': ['cheque_dd_number', 'cheque_dd_date', 'utr_number', 'transfer_date', 'bank_name', 'bank_branch',
                       'realisation_date']}),
        ('Category Details', {
            'fields': ['partner_segment', 'segment', 'company_name', 'building_name', 'pin_code', 'vehicle_category',
                       'vehicle_name', 'vehicle_registration_no']}),
        ('Amount', {'fields': ['gross_amount', 'service_tax', 'vat', 'amount']}),
    ]
    inlines = [CustomerProductQuantityInline, ]
    list_display = ('id', 'user', 'payment_type', 'amount', 'payment_date')

    def get_form(self, request, *args, **kwargs):
        form = super(CustomerInvoiceAdmin, self).get_form(request, *args, **kwargs)
        form.request = request
        return form

    def get_queryset(self, request):
        qs = super(CustomerInvoiceAdmin, self).get_queryset(request)
        l = request.user.groups.values_list('name', flat=True)
        if request.user.is_superuser or 'SuperAdmin' in l:
            return qs
        if 'SubDealer' in l:
            emps = Employee.objects.filter(createdBy=request.user.pk)
            cps = ChannelPartner.objects.filter(Q(manager__in=emps) | Q(createdBy=request.user))
            qs = qs.filter(Q(createdBy__in=cps) | Q(createdBy=request.user))
        elif 'EmployeeGroup' in l:
            emp = Employee.objects.get(pk=request.user.pk)
            cp = ChannelPartner.objects.filter(manager=emp)
            qs = qs.filter(createdBy__in=cp)
        else:
            qs = qs.filter(createdBy=request.user)
        return qs

    def save_model(self, request, obj, form, change):
        if not change:
            obj.createdBy = request.user
        obj.updatedBy = request.user
        super(CustomerInvoiceAdmin, self).save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        super(CustomerInvoiceAdmin, self).save_formset(request, form, formset, change)
        form.instance.gross_amount = CustomerProductQuantity.objects \
            .filter(invoice=form.instance).aggregate(Sum('gross_amount'))['gross_amount__sum']
        form.instance.save()
        if not change:
            myproduct = [i['product'] for i in formset.cleaned_data if 'product' in i]
            products = ''
            for product in myproduct:
                if product.type == 2:
                    products += product.description + ' service'
                else:
                    products += product.description + ' product'
                products += ' and '
            if products.endswith('and '):
                products = products[:-4]
            cp = ChannelPartner.objects.get(pk=request.user.pk)
            subject = 'Welcome to WellNet'
            message = 'Dear ' + form.instance.user.first_name + ' ' + form.instance.user.last_name + ','
            message += '\nThank you for buying ' + products + ' from our trusted dealer ' + cp.company_name \
                       + '.\nIt was our pleasure to serve you and looking forward to see you again.'
            message += '\nRegards,'
            message += '\nWellNet Team'
            from_addr = from_email
            recipient_list = (form.instance.user.email,)
            try:
                send_mail(subject, message, from_addr, recipient_list)
            except:
                logger.error('Error sending email to {}'.format(form.instance.user.email))
                pass

    def save_related(self, request, form, formset, change):
        super(CustomerInvoiceAdmin, self).save_related(request, form, formset, change)
        if not change:
            send_customer_invoice_confirmation(form.instance)


class TaxAdmin(admin.ModelAdmin):
    model = Tax
    list_display = ('product', 'SGST_percentage', 'CGST_percentage', 'IGST_percentage', 'active')

    def product(self, instance):
        return instance.description


class ProductSegmentPriceAdmin(admin.ModelAdmin):
    model = ProductSegmentPrice
    form = ProductSegmentPriceForm
    list_display = ('product', 'segment', 'vehicle_category', 'base_price', 'active')

    def product(self, instance):
        return instance.description

    def segment(self, instance):
        return instance.description


class ProductPriceAdmin(admin.ModelAdmin):
    model = ProductPrice
    form = ProductPriceForm
    list_display = ('product', 'base_price', 'user_group', 'active')

    def product(self, instance):
        return instance.description

    def user_group(self, instance):
        return instance.name


class InventoryInvoiceAdmin(admin.ModelAdmin):
    model = InventoryInvoice
    form = InventoryInvoiceForm
    list_display = ('machine', 'delivery_date', 'partner', 'is_settled')

    def is_settled(self, instance):
        return instance.goods_sold or instance.settlement_date is not None

    is_settled.boolean = True

    def machine(self, instance):
        return instance.machine_number

    def partner(self, instance):
        return instance.company_name

    fieldsets = [
        (None, {'fields': ['machine', 'delivery_date', 'partner']}),
        ('Payment', {'fields': ['security_deposite_amount', 'payment_type']}),
        ('Payment Details', {
            'fields': ['cheque_dd_number', 'cheque_dd_date', 'utr_number', 'transfer_date', 'bank_name', 'bank_branch',
                       'realisation_date']}),
        ('Settlement', {'fields': ['goods_sold', 'settlement_date', 'settlement_amount', 'goods_price']}),
        ('Difference', {'fields': ['difference_amount', 'difference_payment_type']}),
        ('Difference Payment Details', {
            'fields': ['difference_cheque_dd_number', 'difference_cheque_dd_date', 'difference_utr_number',
                       'difference_transfer_date', 'difference_bank_name', 'difference_bank_branch',
                       'difference_realisation_date']}),
        ('Receipt', {'fields': ['send_receipt']}),
    ]
    add_fieldsets = [
        (None, {'fields': ['machine', 'delivery_date', 'partner']}),
        ('Payment', {'fields': ['security_deposite_amount', 'payment_type']}),
        ('Payment Details', {
            'fields': ['cheque_dd_number', 'cheque_dd_date', 'utr_number', 'transfer_date', 'bank_name', 'bank_branch',
                       'realisation_date']}),
    ]

    def get_fieldsets(self, request, obj=None):
        if obj:
            return self.fieldsets
        else:
            return self.add_fieldsets

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return list(set(
                [field.name for field in self.opts.local_fields] +
                [field.name for field in self.opts.local_many_to_many]
            ))
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        if not change:
            obj.createdBy = Employee.objects.get(pk=request.user.pk)
        obj.updatedBy = Employee.objects.get(pk=request.user.pk)
        obj.updated = timezone.now()
        super(InventoryInvoiceAdmin, self).save_model(request, obj, form, change)
        if not change:
            form.instance.machine.is_assigned = True
            form.instance.machine.save()
            sendInventoryInvoice(request, form.instance)
        else:
            if form.instance.settlement_date:
                form.instance.machine.is_assigned = False
                form.instance.machine.save()

            if form.instance.send_receipt:
                sendInventoryReceipt(request, form.instance)


class MachineAdmin(admin.ModelAdmin):
    model = Machine
    form = MachineForm
    list_display = ('machine_number', 'year_of_manufacture', 'warranty_start_date', 'warranty_end_date', 'is_assigned')
    readonly_fields = ('is_assigned',)


class BookingServiceAdmin(admin.ModelAdmin):
    model = BookingService
    form = BookingServiceForm
    list_display = ['booking_service_id', 'firstname', 'phone', 'dealer', 'total_amount',
                    'booking_date']


class DealersAdmin(admin.ModelAdmin):
    model = BookingService
    form = BookingServiceForm
    list_display = ['authorised_person', 'category', 'company', 'service_area', 'email', 'city', 'phone', 'area',
                    'is_active']


class InventoryManagementAdmin(admin.ModelAdmin):
    model = InventoryManagement
    form = InventoryManagementForm
    fieldsets = [
        (None, {'fields': ('packaging_number', 'product_name', 'current_ownership', 'size',
                           'date_of_receipt', 'expiry_date', 'dispatch_date')}),
    ]
    list_display = ('packaging_number', 'product_name', 'current_ownership')


class ReportsInline(admin.StackedInline):
    model = Reports
    form = ReportsForm
    fieldsets = [(None, {'fields': ['time_from', 'time_to', 'state', 'city', 'company']}),
                 ('Authorized Person', {
                     'fields': ['designation', 'name', 'contact_number','call_type',
                                'discussion_point']}),
                 ]
    min_num = 1
    max_num = 5
    extra = 0


class FieldEmployeesActivityReportAdmin(admin.ModelAdmin):
    model = FieldEmployeesActivityReport
    form = FieldEmployeesActivityReportForm
    fieldsets = [(None, {'fields': ['date']})]

    inlines = [ReportsInline, ]
    list_display = ['id', 'date', 'createdBy']

    def save_model(self, request, obj, form, change):
        obj.createdBy = request.user
        super(FieldEmployeesActivityReportAdmin, self).save_model(request, obj, form, change)


class SupplierManagementAdmin(admin.ModelAdmin):
    model = SupplierManagement
    form = SupplierManagementForm
    list_display = ['id', 'company_name', 'agreement_date']


class ProductAdmin(admin.ModelAdmin):
    model = Product
    form = ProductForm
    fieldsets = [
        (None, {'fields': (('description', 'type', 'HSN_code', 'active',),)}),
    ]
    list_display = ['id', "description"]


class ExportXlsAdmin(admin.ModelAdmin):
    model = ExportXls
    form = ExportXlsForm
    list_display = ['id', 'model_type', 'from_date', 'to_date']

    def save_model(self, request, obj, form, change):
        super(ExportXlsAdmin, self).save_model(request, obj, form, change)

    def response_add(self, request, obj, post_url_continue=None):
        return export_xls(obj, request)

    def response_change(self, request, obj):
        return export_xls(obj, request)


admin.site.register(Employee, EmployeeAdmin)
admin.site.register(ChannelPartner, ChannelPartnerAdmin)

admin.site.register(Customer, CustomerAdmin)
admin.site.register(DealersType)
admin.site.register(ChannelPartnerSegment)
admin.site.register(Lead, LeadAdmin)
admin.site.register(LeadStatus)
admin.site.register(CustomerInvoice, CustomerInvoiceAdmin)
admin.site.register(Booking, BookingAdmin)
admin.site.register(ProFormaBooking, ProFormaBookingAdmin)
admin.site.register(ProductSegmentPrice, ProductSegmentPriceAdmin)
admin.site.register(ProductPrice, ProductPriceAdmin)
admin.site.register(Tax, TaxAdmin)
admin.site.register(MoreInfo)
admin.site.register(Machine, MachineAdmin)
admin.site.register(InventoryInvoice, InventoryInvoiceAdmin)
admin.site.register(BookingService, BookingServiceAdmin)
admin.site.register(Dealers, DealersAdmin)
admin.site.register(SupplierManagement, SupplierManagementAdmin)
admin.site.register(State)
admin.site.register(City)
admin.site.register(PaymentType)
admin.site.register(ExportXls, ExportXlsAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(InventoryManagement, InventoryManagementAdmin)
admin.site.register(FieldEmployeesActivityReport, FieldEmployeesActivityReportAdmin)
