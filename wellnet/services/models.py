import datetime

import django
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from django.db import models
from django.db.models import signals
from django.utils import timezone
from django.utils.deconstruct import deconstructible
from django.utils.translation import ugettext_lazy as _
from smart_selects.db_fields import ChainedForeignKey


@deconstructible
class IntegerValidator(object):
    compare = lambda self, a: not a.isdigit()
    clean = lambda self, x: x
    message = _('Ensure this value is numeric.')
    code = 'int_value'

    def __init__(self, message=None):
        if message:
            self.message = message

    def __call__(self, value):
        cleaned = self.clean(value)
        params = {'show_value': cleaned, 'value': value}
        if self.compare(cleaned):
            raise ValidationError(self.message, code=self.code, params=params)

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__)
            and (self.message == other.message)
            and (self.code == other.code)
        )


int_validator = IntegerValidator()

# Create your models here.
SEX = (
    ('M', 'Male'),
    ('F', 'Female'),
)
UNITS = (
    (1, 'none'),
    (2, 'sq ft'),
    (3, 'cubic ft')
)


def get_model_list():
    from django.apps import apps

    app_models = apps.get_app_config('my_app').get_models()
    for model in app_models:
        print(model)

    return []


# 1- ORDER RECEIVED  2- Packaging Done 3-In Transit 4- Out for Delivery 5- Delivered
BOOKING_STATUS = (
    (1, 'In Progress'),
    (2, 'Packaging Done'),
    (3, 'In Transit'),
    (4, 'Out for Delivery'),
    (5, 'Delivered'),
    (6, 'Cancelled')
)
ORDER_DELIVERY_TYPE = (
    (1, 'Courier'),
    (2, 'Hand Deliver'),
    (3, 'Dealer Pickup')
)
CALL_SOURCE = (
    (1, 'Database'),
    (2, 'Reference Lead'),
    (3, 'Cold Calling'),
    (4, 'Website')
)

VEHICLE_CATEGORY = (
    (1, 'Hatchback'),
    (2, 'Sedan'),
    (3, 'SUV'),
    (4, 'Tempo Traveller'),
    (5, 'Bus')
)

MORE_DETAILS_OPTIONS = (
    (1, 'Product Demo'),
    (2, 'Product info'),
    (3, 'Company info'),
    (4, 'Pricing'),
    (5, 'Competitors info')
)
CHOICES = (
    ('Y', 'Yes'),
    ('N', 'No')
)
PRODUCT_TYPES = (
    (1, 'Product'),
    (2, 'Service')
)
MODEL_LIST = (
    (1, 'Invoices'),
    (2, 'Pro-forma-Invoices'),
    (3, 'Inventory'),
    (4, 'Supplier'),
    (5, 'Daily Sales Report'),
    (6, 'Partners'),
    (7, 'Products'),
)
CALL_TYPES = (
    (1, 'Presentation call'),
    (2, 'Presentation & Demo call'),
    (3, 'Follow up'),
    (4, 'Closure'),
    (5, 'Relationship Call'),
    (6, 'Training'),
)

YEAR_CHOICES = []
for r in range(1950, (timezone.now().year + 1)):
    YEAR_CHOICES.append((r, r))


class MoreInfo(models.Model):
    info = models.IntegerField(choices=MORE_DETAILS_OPTIONS)

    def __str__(self):
        return '{}'.format(dict(MORE_DETAILS_OPTIONS).get(self.info))


class State(models.Model):
    name = models.CharField(max_length=255, blank=False, unique=True)

    def __str__(self):
        return '{}'.format(self.name)


class City(models.Model):
    name = models.CharField(max_length=255, blank=False, unique=True)
    state = models.ForeignKey('State', null=False, blank=False)

    def __str__(self):
        return '{}'.format(self.name)

    class Meta:
        verbose_name = "City"
        verbose_name_plural = "Cities"


class ChannelPartnerSegment(models.Model):
    description = models.CharField(max_length=255, blank=False)

    def __str__(self):
        return '{}'.format(self.description)

    class Meta:
        verbose_name = "Partner Segment"
        verbose_name_plural = "Partner Segments"


class CustomerCategory(models.Model):
    description = models.CharField(max_length=255, blank=False)

    def __str__(self):
        return '{}'.format(self.description)


class BaseUser(AbstractUser):
    phone_number = models.CharField(max_length=10, blank=False)
    force_password_change = models.BooleanField(default=True)
    USERNAME_FIELD = AbstractUser.USERNAME_FIELD
    REQUIRED_FIELDS = ['email', 'phone_number']

    def save(self, *args, **kwargs):
        # self.email = self.username
        super(BaseUser, self).save(*args, **kwargs)


class Employee(BaseUser):
    name = models.CharField(max_length=255, blank=False)
    current_address = models.CharField(max_length=255, blank=False)
    permanent_address = models.CharField(max_length=255, blank=False)
    pan_number = models.CharField(max_length=10, blank=False)
    aadhar_number = models.CharField(max_length=12, blank=False)
    date_of_birth = models.DateField(blank=False)
    hire_date = models.DateField(default=timezone.now)
    date_of_resignation = models.DateField(blank=True)
    reason_for_resignation = models.CharField(max_length=555, blank=True)
    emergency_contact_name = models.CharField('Name', max_length=255, blank=False)
    emergency_contact_phone = models.CharField('Mobile Number', max_length=10,
                                               validators=[MinLengthValidator(10), int_validator])
    emergency_contact_relation = models.CharField('Relation', max_length=30, blank=False)
    is_admin = models.BooleanField(default=False)
    createdBy = models.ForeignKey('BaseUser', null=False, blank=False, related_name='createdByUser')

    class Meta:
        verbose_name = "Employee"
        verbose_name_plural = "Employees"

    def __str__(self):
        return '{} ({})'.format(self.name, self.username)


class PartnerBranch(models.Model):
    branch_address = models.CharField(max_length=255, null=False, blank=False)
    pin_code = models.CharField(max_length=6, validators=[MinLengthValidator(6), int_validator])
    state = models.ForeignKey('State', null=False, blank=False, )
    city = models.ForeignKey('City', null=False, blank=False, default='Bengaluru')
    landline = models.CharField(max_length=11, validators=[MinLengthValidator(10), int_validator])
    authorized_person_name = models.CharField('Name', max_length=255, null=False, blank=False)
    authorized_person_gender = models.CharField('Gender', max_length=1, choices=SEX, default='M')
    authorized_person_landline = models.CharField('Landline', max_length=11,
                                                  validators=[MinLengthValidator(10), int_validator])
    authorized_person_date_of_birth = models.DateField('Date of birth', blank=False, default=django.utils.timezone.now)
    authorized_person_mobile_number = models.CharField('Mobile Number', max_length=10,
                                                       validators=[MinLengthValidator(10), int_validator])
    authorized_person_address = models.CharField('Address', max_length=255, null=False, blank=False)
    authorized_person_email = models.EmailField('Email', max_length=255, null=False, blank=False)
    same_as_owner = models.BooleanField(default=False)
    partner = models.ForeignKey('ChannelPartner', null=False, blank=False)

    def __str__(self):
        return 'Branch'

    class Meta:
        verbose_name = "Dealership/Branch"
        verbose_name_plural = "Dealerships/Branches"


class PartnerAsOwner(models.Model):
    name = models.CharField(max_length=255, blank=False)
    date_of_birth = models.DateField(blank=False,default=django.utils.timezone.now)
    gender = models.CharField(max_length=1, choices=SEX, default='M')
    landline = models.CharField(max_length=11, validators=[MinLengthValidator(10), int_validator])
    mobile_number = models.CharField(max_length=10, validators=[MinLengthValidator(10), int_validator])
    address = models.CharField(max_length=255, null=False, blank=False)
    email = models.EmailField(max_length=255, null=False, blank=False)
    partner = models.ForeignKey('ChannelPartner', null=False, blank=False)

    def __str__(self):
        return 'Owner'

    class Meta:
        verbose_name = "Owner"
        verbose_name_plural = "Owner"


class ChannelPartner(BaseUser):
    company_name = models.CharField(max_length=255, blank=False)
    dealer_code = models.CharField(max_length=255, default=0, blank=False)
    dealership_category = models.ForeignKey('DealersType', null=False, blank=False, default=4)
    company_name_invoice = models.CharField("Company Name For Invoice", max_length=255, blank=False, default="wellnet")
    hire_date = models.DateField(default=timezone.now)
    segments = models.ManyToManyField(ChannelPartnerSegment)
    company_address = models.CharField(max_length=255)
    number_of_staff = models.IntegerField(default=1)
    number_of_branches = models.IntegerField(default=1)
    number_of_products = models.IntegerField(default=1)
    year_of_establishment = models.IntegerField(choices=YEAR_CHOICES, default=timezone.now().year)
    pin_code = models.CharField(max_length=6, validators=[MinLengthValidator(6), int_validator])
    state = models.ForeignKey('State', null=False, blank=False, )
    city = models.ForeignKey('City', null=False, blank=False, default='Bengaluru')
    master_dealership = models.CharField('MasterDealership', max_length=255, null=True, blank=True, default="Retails")
    landline = models.CharField(max_length=11, validators=[MinLengthValidator(10), int_validator])
    GSTIN = models.CharField(max_length=255)
    parts_department_name = models.CharField('Name', max_length=255, null=True, blank=True, )
    parts_department_phone = models.CharField("Phone", max_length=10, null=True, blank=True,
                                              validators=[MinLengthValidator(10), int_validator])
    parts_department_email = models.EmailField("Email", null=True, blank=True, )
    finance_department_name = models.CharField('Name', max_length=255, null=True, blank=True, )
    finance_department_phone = models.CharField("Phone", max_length=10, null=True, blank=True,
                                                validators=[MinLengthValidator(10), int_validator])
    finance_department_email = models.EmailField("Email", null=True, blank=True)
    company_pan_number = models.CharField(max_length=10, validators=[MinLengthValidator(10)])
    manager = models.ForeignKey('Employee', null=False, blank=False, related_name='managerEmployee')
    is_sub_dealer = models.BooleanField(default=False)
    createdBy = models.ForeignKey('BaseUser', null=False, blank=False, related_name='cpCreatedByUser')

    def __str__(self):
        return '%s' % (self.first_name + " " + self.last_name + "( " + self.username + ") ")

    class Meta:
        verbose_name = "Partner"
        verbose_name_plural = "Partners"


class Machine(models.Model):
    machine_number = models.CharField(max_length=255, blank=False, null=False, unique=True)
    year_of_manufacture = models.CharField(max_length=4, validators=[MinLengthValidator(4), int_validator])
    manufacturer_company = models.CharField(max_length=100)
    warranty_start_date = models.DateField()
    warranty_end_date = models.DateField()
    is_assigned = models.BooleanField(default=False)

    def __str__(self):
        return '{} ({}), {}'.format(self.machine_number, self.year_of_manufacture, self.manufacturer_company)


class InventoryInvoice(models.Model):
    machine = models.ForeignKey(Machine, null=False, blank=False)
    delivery_date = models.DateField(default=timezone.now)
    partner = models.ForeignKey('ChannelPartner', null=False, blank=False)
    security_deposite_amount = models.DecimalField(max_digits=30, decimal_places=2, null=False, blank=False)
    payment_type = models.ForeignKey('PaymentType', null=False, blank=False)
    cheque_dd_number = models.CharField('Cheque/DD Number', max_length=15, null=True, blank=True)
    cheque_dd_date = models.DateField('Date on Cheque/DD', default=timezone.now, blank=True)
    utr_number = models.CharField('UTR Number', max_length=30, null=True, blank=True)
    transfer_date = models.DateField('Payment Date', null=True, default=timezone.now, blank=True)
    bank_name = models.CharField(max_length=255, null=True, blank=True)
    bank_branch = models.CharField(max_length=255, null=True, blank=True)
    realisation_date = models.DateField('Date of payment realisation', null=True, default=timezone.now, blank=True)
    settlement_amount = models.DecimalField('Retained Amount', max_digits=30, decimal_places=2, null=True, blank=True)
    settlement_date = models.DateField(null=True, blank=True)
    goods_sold = models.BooleanField(default=False)
    difference_amount = models.DecimalField('Amount', max_digits=30, decimal_places=2, null=True, blank=True)
    difference_payment_type = models.ForeignKey('PaymentType', null=True, blank=True, related_name="diff_payment")
    difference_cheque_dd_number = models.CharField('Cheque/DD Number', max_length=15, null=True, blank=True)
    difference_cheque_dd_date = models.DateField('Date on Cheque/DD', null=True, blank=True)
    difference_utr_number = models.CharField('UTR Number', max_length=30, null=True, blank=True)
    difference_transfer_date = models.DateField('Payment Date', null=True, blank=True)
    difference_bank_name = models.CharField('Bank Name', max_length=255, null=True, blank=True)
    difference_bank_branch = models.CharField('Branch Name', max_length=255, null=True, blank=True)
    difference_realisation_date = models.DateField('Date of payment realisation', null=True, blank=True)
    goods_price = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)
    send_receipt = models.BooleanField(default=False)
    created_date = models.DateField(default=timezone.now)
    updated = models.DateField(default=timezone.now)
    createdBy = models.ForeignKey('Employee', null=False, blank=False, related_name="invCreatedBy")
    updatedBy = models.ForeignKey('Employee', null=False, blank=False, related_name="invUpdatedBy")

    def __str__(self):
        return '{}'.format(self.partner)

    # def __repr__(self):
    #     return f'{{"created_date": {self.created_date}, "utr_number": {self.utr_number}}}'

    def get_json(self):
        body = {
            "created_date": self.created_date.strftime("%d-%m-%Y") if self.created_date else "",
            "utr_number": self.utr_number if self.utr_number else "",
            # "machine": self.machine if self.machine else None,
            "delivery_date": self.delivery_date.strftime("%d-%m-%Y") if self.delivery_date else None,
            "payment_type": self.payment_type.description if self.payment_type.description else "",
            "bank_name": self.bank_name if self.bank_name else "",
            "bank_branch": self.bank_branch if self.bank_branch else "",
            "cheque_dd_date": self.cheque_dd_date.strftime("%d-%m-%Y") if self.cheque_dd_date else None,
            "cheque_dd_number": self.cheque_dd_number if self.cheque_dd_number else "",
            "transfer_date": self.transfer_date.strftime("%d-%m-%Y") if self.transfer_date else None,
            "settlement_amt": self.settlement_amount if self.settlement_amount else None,
            "settlement_date": self.settlement_date if self.settlement_date else None,
            "goods_sold": self.goods_sold if self.goods_sold else None,
            "goods_price": self.goods_price if self.goods_price else None,
            "difference_amount": self.difference_amount if self.difference_amount else None,
            "difference_bank_branch": self.difference_bank_branch if self.difference_bank_branch else "",
            "difference_bank_name": self.difference_bank_name if self.difference_bank_name else "",
            "difference_cheque_dd_date": self.difference_cheque_dd_date if self.difference_cheque_dd_date else None,
            "difference_cheque_dd_number": self.difference_cheque_dd_number if self.difference_cheque_dd_number else "",
            "difference_payment_type": self.difference_payment_type if self.difference_payment_type else None,
            "difference_realisation_date": self.difference_realisation_date if self.difference_realisation_date else None,
            "difference_transfer_date": self.difference_transfer_date if self.difference_transfer_date else None,
            "difference_utr_number": self.difference_utr_number if self.difference_utr_number else ""
        }
        return body


    def clean(self):
        from django.core.exceptions import ValidationError
        if self.realisation_date is not None and self.cheque_dd_date is not None:
            if self.realisation_date != '' and self.cheque_dd_date != '':
                if self.realisation_date < self.cheque_dd_date:
                    raise ValidationError('Payment realization date should be after cheque/dd date')
                elif self.realisation_date > datetime.date.today():
                    raise ValidationError('Payment realization date cannot be future day')


class Customer(models.Model):
    first_name = models.CharField(max_length=100, blank=False)
    last_name = models.CharField(max_length=100, blank=False)
    gender = models.CharField(max_length=1, choices=SEX, default='M')
    mobile_number = models.CharField(max_length=10, validators=[MinLengthValidator(10), int_validator])
    # landline = models.CharField(null=True, blank=True, max_length=11, validators=[MinLengthValidator(10), int_validator])
    email = models.EmailField()
    address = models.TextField(max_length=255, blank=True, default="", )
    pin_code = models.CharField(max_length=6, validators=[MinLengthValidator(6), int_validator])
    createdBy = models.ForeignKey('ChannelPartner', null=False, blank=False, default='BaseUser')

    def __str__(self):
        return '{} {}, {}'.format(self.first_name, self.last_name, self.mobile_number)


class LeadStatus(models.Model):
    description = models.CharField(max_length=100, blank=False)

    class Meta:
        verbose_name = "Lead Status"
        verbose_name_plural = "Lead Statuses"

    def __str__(self):
        return '{}'.format(self.description)


class StatusReason(models.Model):
    description = models.CharField(max_length=100, blank=False)
    status = models.ForeignKey('LeadStatus', null=False, blank=False)

    class Meta:
        verbose_name = "Status Reason"
        verbose_name_plural = "Status Reasons"

    def __str__(self):
        return '{}'.format(self.description)


class Lead(models.Model):
    customer_name = models.CharField(max_length=100, blank=False)
    company_name = models.CharField(max_length=255, blank=False)
    mobile_number = models.CharField(max_length=10, validators=[MinLengthValidator(10), int_validator])
    landline_number = models.CharField(max_length=11, validators=[MinLengthValidator(10), int_validator])
    city = models.ForeignKey('City', null=False, blank=False)
    address = models.CharField(max_length=255, blank=True)
    pin_code = models.CharField(max_length=6, validators=[MinLengthValidator(6), int_validator])
    segments = models.ManyToManyField(ChannelPartnerSegment)
    call_source = models.IntegerField(choices=CALL_SOURCE)
    product_demo = models.CharField(default='N', max_length=1, choices=CHOICES)
    status = models.ForeignKey('LeadStatus', null=False, blank=False)
    reason = models.ForeignKey('StatusReason', null=True, blank=True)
    more_details = models.ManyToManyField(MoreInfo, null=False, blank=True)
    next_appointment = models.DateTimeField('Next Appointment On', null=True, blank=True)
    comments = models.TextField(blank=True)
    channelpartner = models.ForeignKey('ChannelPartner', null=True, blank=True, verbose_name="Partner")
    registration_form = models.CharField(default='N', max_length=1, choices=CHOICES)
    payment_collected = models.CharField(default='N', max_length=1, choices=CHOICES)
    goods_delivered = models.CharField(default='N', max_length=1, choices=CHOICES)
    cheque_dd_number = models.CharField('Cheque/DD Number', max_length=15, null=True, blank=True)
    created_date = models.DateField('Date', default=timezone.now)
    updated = models.DateField('Updated', default=timezone.now)
    createdBy = models.ForeignKey('BaseUser', null=False, blank=False, related_name="leadCreatedBy")
    updatedBy = models.ForeignKey('BaseUser', null=False, blank=False, related_name="leadUpdatedBy")

    def __str__(self):
        return '{}, {}'.format(self.customer_name, self.company_name)


class Booking(models.Model):
    payment_type = models.ForeignKey('PaymentType', null=False, blank=False)
    gross_amount = models.DecimalField('Gross Amount', max_digits=30, decimal_places=2)
    amount = models.DecimalField('Total Amount', max_digits=30, decimal_places=2)
    SGST_amount = models.DecimalField(max_digits=30, default=0, decimal_places=2)
    CGST_amount = models.DecimalField(max_digits=30, default=0, decimal_places=2)
    IGST_amount = models.DecimalField(max_digits=30, default=0, decimal_places=2)
    cheque_dd_number = models.CharField('Cheque/DD Number', max_length=15, null=True, blank=True)
    purchase_order_number = models.CharField('Purchase Order Number', max_length=25, default=0, null=False, blank=False)
    cheque_dd_date = models.DateField('Date on Cheque/DD', default=timezone.now, blank=True)
    utr_number = models.CharField('UTR Number', max_length=30, null=True, blank=True)
    transfer_date = models.DateField('Payment Date', null=True, default=timezone.now, blank=True)
    bank_name = models.CharField(max_length=255, null=True, blank=True)
    bank_branch = models.CharField(max_length=255, null=True, blank=True)
    realisation_date = models.DateField('Date of payment realisation', null=True, blank=True)
    is_immediate = models.BooleanField('Immediate Delivery?', default=False)
    is_IGST = models.BooleanField('IGST Format', default=False)
    expected_delivery_date = models.DateField('Expected Delivery Date', null=False, blank=False)
    order_delivery_date = models.DateField('Order Dispatched Date', null=True, blank=True)
    order_delivery_type = models.IntegerField(choices=ORDER_DELIVERY_TYPE, null=False, blank=False)
    courier_company_name = models.CharField(max_length=255, null=True, blank=True)
    pod_number = models.CharField(max_length=255, null=True, blank=True)
    person_name = models.CharField(max_length=255, null=True, blank=True)
    contact_number = models.CharField(max_length=10, validators=[MinLengthValidator(10)], null=True, blank=True)
    is_cancelled = models.BooleanField('Cancel this booking?', default=False)
    cancel_reason = models.CharField(max_length=255, null=True, blank=True)
    created_date = models.DateField(default=timezone.now)
    updated = models.DateField(default=timezone.now)
    send_receipt = models.BooleanField(default=False)
    send_pod = models.BooleanField("Send Delivery Details", default=False)
    createdFor = models.ForeignKey('ChannelPartner', null=False, blank=False, related_name="createdFor")
    createdBy = models.ForeignKey('BaseUser', null=False, blank=False)
    updatedBy = models.ForeignKey('BaseUser', null=False, blank=False, related_name="updatedBy")

    def __str__(self):
        return 'Booking#{}, {}, {}, {}, {}'.format(self.id, self.createdBy.email, self.updated, self.createdFor.GSTIN, self.createdFor.dealership_category.description)

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.realisation_date is not None and self.cheque_dd_date is not None:
            if self.realisation_date != '' and self.cheque_dd_date != '':
                if self.realisation_date < self.cheque_dd_date:
                    raise ValidationError('Payment realization date should be after cheque/dd date')
                elif self.realisation_date > datetime.date.today():
                    raise ValidationError('Payment realization date cannot be future day')

    class Meta:
        verbose_name = "Invoice"
        verbose_name_plural = "Invoices"


class ProFormaBooking(models.Model):
    gross_amount = models.DecimalField('Gross Amount', max_digits=30, decimal_places=2)
    amount = models.DecimalField('Total Amount', max_digits=30, decimal_places=2)
    SGST_amount = models.DecimalField(max_digits=30, decimal_places=2)
    CGST_amount = models.DecimalField(max_digits=30, decimal_places=2)
    IGST_amount = models.DecimalField(max_digits=30, decimal_places=2)
    is_IGST = models.BooleanField('IGST Format', default=False)
    is_cancelled = models.BooleanField('Cancel this booking?', default=False)
    cancel_reason = models.CharField(max_length=255, null=True, blank=True)
    contact_number = models.CharField(max_length=10, validators=[MinLengthValidator(10)], null=True, blank=True)
    created_date = models.DateField(default=timezone.now)
    updated = models.DateField(default=timezone.now)
    created_For = models.ForeignKey('ChannelPartner', null=False, blank=False, related_name="created_For")
    createdBy = models.ForeignKey('BaseUser', null=False, blank=False)
    updated_By = models.ForeignKey('BaseUser', null=False, blank=False, related_name="updated_By")

    def __str__(self):
        return 'Booking#{}, {}, {}'.format(self.id, self.createdBy.email, self.updated)

    class Meta:
        verbose_name = "Pro-Forma Invoice"
        verbose_name_plural = "Pro-Forma Invoices"


class PaymentType(models.Model):
    description = models.CharField(max_length=100, blank=False)

    def __str__(self):
        return '{}'.format(self.description)


class Product(models.Model):
    description = models.CharField(max_length=100, blank=False)
    type = models.IntegerField(choices=PRODUCT_TYPES)
    HSN_code = models.CharField(null=False, blank=False, max_length=256)
    active = models.BooleanField(default=True)

    def __str__(self):
        return '{}'.format(self.description)


class ProductSegmentPrice(models.Model):
    product = models.ForeignKey('Product', null=False, blank=False)
    segment = models.ForeignKey('CustomerCategory', null=True, blank=True)
    vehicle_category = models.IntegerField(choices=VEHICLE_CATEGORY, null=True, blank=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Customer Product Price"
        verbose_name_plural = "Customer Product Prices"

    def __str__(self):
        return '{}'.format(self.product.description)


class ProductPrice(models.Model):
    product = models.ForeignKey('Product', null=False, blank=False)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    user_group = models.ForeignKey(Group, null=True, blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Partner Product Price"
        verbose_name_plural = "Partner Product Prices"

    def __str__(self):
        return '{}'.format(self.product.description)


class ProductQuantityUnitDisplay(models.Model):
    product = models.ForeignKey('Product', null=False, blank=False)
    unit = models.IntegerField(choices=UNITS)


class ProductQuantity(models.Model):
    product = models.ForeignKey('Product', null=False, blank=False)
    quantity = models.IntegerField()
    gross_amount = models.DecimalField('Gross Amount', max_digits=30, decimal_places=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount_igst = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    SGST_amount = models.DecimalField(max_digits=30, decimal_places=2, default=0)
    CGST_amount = models.DecimalField(max_digits=30, decimal_places=2, default=0)
    IGST_amount = models.DecimalField(max_digits=30, decimal_places=2, default=0)
    SGST_percentage = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    CGST_percentage = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    IGST_percentage = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    booking = models.ForeignKey('Booking', null=False, blank=False)

    class Meta:
        verbose_name = "Partner Product"
        verbose_name_plural = "Partner Products"

    def __str__(self):
        return 'Partner Product'

    def save(self, *args, **kwargs):
        tax = Tax.objects.filter(active=True, product__pk=self.product_id)[0]
        booking = Booking.objects.filter(pk=self.booking_id)[0]
        partner = BaseUser.objects.filter(pk=booking.createdFor.id)[0]
        # l = partner.groups.values_list('id', flat=True)[0]
        price = ProductPrice.objects.filter(product__pk=self.product_id, active=True, )[0]
        self.base_price = self.base_price
        self.SGST_percentage = tax.SGST_percentage
        self.CGST_percentage = tax.CGST_percentage
        self.IGST_percentage = tax.IGST_percentage
        self.gross_amount = self.base_price * self.quantity
        self.SGST_amount = tax.SGST_percentage * self.gross_amount / 100
        self.CGST_amount = tax.CGST_percentage * self.gross_amount / 100
        self.IGST_amount = tax.IGST_percentage * self.gross_amount / 100
        self.amount = self.gross_amount + self.SGST_amount + self.CGST_amount
        self.amount_igst = self.gross_amount + self.IGST_amount
        super(ProductQuantity, self).save(*args, **kwargs)


class ProFormaProductQuantity(models.Model):
    product = models.ForeignKey('Product', null=False, blank=False)
    quantity = models.IntegerField()
    gross_amount = models.DecimalField('Gross Amount', max_digits=30, decimal_places=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    amount_igst = models.DecimalField(max_digits=10, decimal_places=2)
    SGST_amount = models.DecimalField(max_digits=30, decimal_places=2, default=0)
    CGST_amount = models.DecimalField(max_digits=30, decimal_places=2, default=0)
    IGST_amount = models.DecimalField(max_digits=30, decimal_places=2, default=0)
    SGST_percentage = models.DecimalField(max_digits=4, decimal_places=2)
    CGST_percentage = models.DecimalField(max_digits=4, decimal_places=2)
    IGST_percentage = models.DecimalField(max_digits=4, decimal_places=2)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    booking = models.ForeignKey('ProFormaBooking', null=False, blank=False)

    class Meta:
        verbose_name = "ProForm Partner Product"
        verbose_name_plural = "ProForm Partner Products"

    def __str__(self):
        return 'Partner Product'

    def save(self, *args, **kwargs):
        tax = Tax.objects.filter(active=True, product__pk=self.product_id)[0]
        booking = ProFormaBooking.objects.filter(pk=self.booking_id)[0]
        partner = BaseUser.objects.filter(pk=booking.created_For.id)[0]
        l = partner.groups.values_list('id', flat=True)[0]
        price = ProductPrice.objects.filter(product__pk=self.product_id, active=True)[0]
        self.base_price = self.base_price
        self.SGST_percentage = tax.SGST_percentage
        self.CGST_percentage = tax.CGST_percentage
        self.gross_amount = self.base_price * self.quantity
        self.SGST_amount = tax.SGST_percentage * self.gross_amount / 100
        self.CGST_amount = tax.CGST_percentage * self.gross_amount / 100
        self.IGST_amount = tax.IGST_percentage * self.gross_amount / 100
        self.amount = self.gross_amount + self.SGST_amount + self.CGST_amount
        self.amount_igst = self.gross_amount + self.IGST_amount
        super(ProFormaProductQuantity, self).save(*args, **kwargs)


class CustomerInvoice(models.Model):
    user = models.ForeignKey('Customer', null=False, blank=False, )
    partner_segment = models.ForeignKey('ChannelPartnerSegment', null=False, blank=False,
                                        verbose_name="Previous service provided")
    segment = models.ForeignKey('CustomerCategory', null=True, blank=True, verbose_name="Customer Category")
    company_name = models.CharField('Company Name', max_length=100, null=True, blank=True)
    building_name = models.CharField('Building Name', max_length=50, null=True, blank=True)
    pin_code = models.CharField(null=True, blank=True, max_length=6, validators=[MinLengthValidator(6), int_validator])
    vehicle_category = models.IntegerField(choices=VEHICLE_CATEGORY, null=True, blank=True)
    vehicle_name = models.CharField('Vehicle Name', max_length=30, null=True, blank=True)
    vehicle_registration_no = models.CharField('Vehicle Registration Number', max_length=15, null=True, blank=True)
    year_of_manufacture = models.IntegerField(default=2014, null=True, blank=True)
    same_address_as_user = models.BooleanField(default=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    payment_type = models.ForeignKey('PaymentType', null=False, blank=False, default=4)
    gross_amount = models.DecimalField('Gross Amount', max_digits=30, decimal_places=2)
    amount = models.DecimalField('Total Amount', max_digits=30, decimal_places=2)
    service_tax = models.DecimalField(max_digits=30, decimal_places=2, default=0)
    vat = models.DecimalField('VAT', max_digits=30, decimal_places=2, default=0)
    cheque_dd_number = models.CharField('Cheque/DD Number', max_length=15, null=True, blank=True)
    cheque_dd_date = models.DateField('Date on Cheque/DD', default=timezone.now, blank=True, null=True)
    utr_number = models.CharField('UTR Number', max_length=25, null=True, blank=True)
    transfer_date = models.DateField('Payment Date', null=True, default=timezone.now, blank=True)
    bank_name = models.CharField(max_length=255, null=True, blank=True)
    bank_branch = models.CharField(max_length=255, null=True, blank=True)
    realisation_date = models.DateField('Date of payment realisation', null=True, blank=True)
    payment_date = models.DateField(default=timezone.now)
    updated = models.DateField(default=timezone.now)
    created_date = models.DateField(default=timezone.now)
    send_receipt = models.BooleanField(default=False)
    createdBy = models.ForeignKey('BaseUser', null=False, blank=False, related_name="customerCreatedBy")
    updatedBy = models.ForeignKey('BaseUser', null=False, blank=False, related_name="customerUpdatedBy")

    def __str__(self):
        return 'Invoice#{}, {}, {}'.format(self.id, self.user.first_name, self.amount)

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.realisation_date is not None and self.cheque_dd_date is not None:
            if self.realisation_date != '' and self.cheque_dd_date != '':
                if self.realisation_date < self.cheque_dd_date:
                    raise ValidationError('Payment realization date should be after cheque/dd date')
                elif self.realisation_date > datetime.date.today():
                    raise ValidationError('Payment realization date cannot be future day')


class CustomerProductQuantity(models.Model):
    product = models.ForeignKey('Product', null=False, blank=False)
    quantity = models.IntegerField('Serviced Area')
    gross_amount = models.DecimalField('Total Amount Charged', max_digits=30, decimal_places=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    service_tax = models.DecimalField(max_digits=30, decimal_places=2, default=0)
    vat = models.DecimalField(max_digits=30, decimal_places=2, default=0)
    invoice = models.ForeignKey(CustomerInvoice)

    class Meta:
        verbose_name = "Customer Product"
        verbose_name_plural = "Customer Products"

    def __str__(self):
        return 'Customer Product'

    def save(self, *args, **kwargs):
        tax = Tax.objects.filter(active=True, product__pk=self.product_id)[0]
        invoice = CustomerInvoice.objects.get(pk=self.invoice_id)
        if self.product.type == 1:
            price = \
                ProductSegmentPrice.objects.filter(product__pk=self.product_id, active=True)
        else:
            price = \
                ProductSegmentPrice.objects.filter(product__pk=self.product_id, segment__pk=invoice.segment_id,
                                                   active=True)
            if invoice.vehicle_category:
                price = price.filter(vehicle_category=invoice.vehicle_category)
        price = price[0]
        self.gross_amount = price.base_price * self.quantity
        self.service_tax = tax.SGST_percentage * self.gross_amount / 100
        self.vat = tax.CGST_percentage * self.gross_amount / 100
        self.amount = self.gross_amount + self.service_tax + self.vat
        super(CustomerProductQuantity, self).save(*args, **kwargs)


class Tax(models.Model):
    product = models.ForeignKey('Product', null=False, blank=False)
    SGST_percentage = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    CGST_percentage = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    IGST_percentage = models.DecimalField(max_digits=4, decimal_places=2, default=0)

    active = models.BooleanField(default=True)
    end_date = models.DateField(default=timezone.now)

    class Meta:
        verbose_name = "Tax"
        verbose_name_plural = "Taxes"


class BookingService(models.Model):
    service_type = models.CharField(null=False, blank=False, max_length=256)
    firstname = models.CharField(null=False, blank=False, max_length=256)
    booking_service_id = models.CharField(primary_key=True, unique=True, null=False, blank=False, max_length=50)
    email = models.EmailField(null=False, blank=False)
    city = models.CharField(max_length=256, null=False, blank=False)
    dealer = models.CharField(null=False, blank=False, max_length=50)
    dealer_phone = models.CharField(max_length=256, null=False, blank=False)
    phone = models.CharField(max_length=10, null=False, blank=False)
    area = models.DecimalField(null=False, blank=False, max_digits=10, default=0, decimal_places=4,
                               help_text="Area in SquareFeet")
    total_amount = models.DecimalField(null=False, blank=False, max_digits=10, default=0, decimal_places=4)
    address = models.TextField(default="", blank=True, help_text="Address")
    landmark = models.CharField(default="", blank=True, max_length=256, help_text="Landmark")
    dealer_address = models.TextField(default="", help_text="Address")
    payment_option = models.CharField(max_length=256, null=False, blank=False)
    booking_date = models.DateTimeField(blank=False, default=datetime.datetime.now())

    # type = models.IntegerField(choices=PRODUCT_TYPES)
    def __str__(self):
        return '{} ({}), {}'.format(self.booking_service_id, self.firstname, self.service_type)

    class Meta:
        verbose_name = "BookingService"
        verbose_name_plural = "BookingServices"


class Dealers(models.Model):
    company = models.CharField(null=False, blank=False, max_length=20)
    authorised_person = models.CharField(null=False, blank=False, max_length=20)
    category = models.CharField(null=False, blank=False, max_length=256)
    service_area = models.CharField(null=False, blank=False, max_length=20)
    email = models.EmailField(null=False, blank=False)
    phone = models.CharField(max_length=256, null=False, blank=False)
    city = models.CharField(max_length=256, null=False, blank=False)
    area = models.CharField(null=False, blank=False, default="", max_length=256)
    address = models.TextField(null=False, blank=False, max_length=256, default="", )
    map_link = models.CharField(null=False, blank=False, default="", max_length=256, help_text="map link")
    is_active = models.BooleanField(null=False, blank=False, help_text="", default=True)

    def __str__(self):
        return '{},{}'.format(self.authorised_person, self.category)

    class Meta:
        verbose_name = "Dealer"
        verbose_name_plural = "Dealers"


# PHASE 2
class DealersType(models.Model):
    description = models.CharField(max_length=255, blank=False)

    def __str__(self):
        return '{}'.format(self.description)

    class Meta:
        verbose_name = "DealersType"
        verbose_name_plural = "DealersTypes"

        # PHASE 2


class SupplierManagement(models.Model):
    company_name = models.CharField(null=False, blank=False, max_length=256)
    company_name_for_invoice = models.CharField(null=False, blank=False, max_length=256)
    company_address = models.TextField(null=False, blank=False, max_length=256)
    state = models.ForeignKey('State', null=False, blank=False, )
    city = ChainedForeignKey(City, chained_field="state",
                             chained_model_field="state",
                             show_all=False, auto_choose=True,
                             sort=True)
    country = models.CharField(null=False, blank=False, max_length=256)
    pin_code = models.CharField(max_length=6, null=False, blank=False,
                                validators=[MinLengthValidator(6), int_validator])
    phone_no = models.CharField(null=False, blank=False, max_length=12)
    authorised_person = models.CharField(null=False, blank=False, max_length=256)
    email_id = models.EmailField(null=False, blank=False)
    mobile_no = models.CharField(max_length=10, validators=[MinLengthValidator(10)], null=False, blank=False)
    agreement_date = models.DateTimeField(blank=False)
    agreed_products = models.ForeignKey('Product', blank=False, max_length=256)

    def __str__(self):
        return '{},{}'.format(self.company_name, self.authorised_person)

    class Meta:
        verbose_name = "Supplier"
        verbose_name_plural = "Supplier Management"


def get_deadline():
    return datetime.date.today() + datetime.timedelta(days=1095)


class InventoryManagement(models.Model):
    packaging_number = models.CharField(null=False, blank=False, max_length=256)
    product_name = models.ForeignKey('Product', blank=False)
    size = models.CharField(null=False, blank=False, max_length=256, verbose_name="Size")
    current_ownership = models.ForeignKey('ChannelPartner', null=False, blank=False)
    date_of_receipt = models.DateField(blank=True, null=True)
    expiry_date = models.DateField(blank=False, default=get_deadline())

    dispatch_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return '{} - {} {} ({})'.format(self.product_name, self.packaging_number, self.current_ownership_id,
                                        self.dispatch_date)

    class Meta:
        verbose_name = "Inventory"
        verbose_name_plural = "Inventory Management"


class Reports(models.Model):
    time_from = models.TimeField(null=False, blank=False,
                                 help_text="Time-Format should be HH:mm:ss(24 hour format ex: 13:13:10)")
    time_to = models.TimeField(null=False, blank=False,
                               help_text="Time-Format should be HH:mm:ss (24 hour format ex: 13:13:10)")
    state = models.ForeignKey('State', null=False, blank=False, )
    city = ChainedForeignKey('City', null=False, blank=False, )
    company = models.CharField(max_length=256, null=False, blank=False)
    name = models.CharField(null=False, blank=False, max_length=256)
    designation = models.CharField(null=False, blank=False, max_length=256)
    contact_number = models.CharField(max_length=10, validators=[MinLengthValidator(10)], null=False, blank=False)
    discussion_point = models.TextField(null=False, blank=False, max_length=512)
    call_type = models.IntegerField(choices=CALL_TYPES, null=True, blank=True)
    field_emp = models.ForeignKey('FieldEmployeesActivityReport', null=False, blank=False)

    def __str__(self):
        return 'Reports'

    class Meta:
        verbose_name = "Report"
        verbose_name_plural = "Reports"


class FieldEmployeesActivityReport(models.Model):
    date = models.DateField(null=False, blank=False)
    createdBy = models.ForeignKey('BaseUser', null=False, blank=False)

    def __str__(self):
        return '{}'.format(self.date)

    class Meta:
        verbose_name = "Daily sales report"
        verbose_name_plural = "Daily sales reports"


class ExportXls(models.Model):
    model_type = models.IntegerField(choices=MODEL_LIST, null=False, blank=False)
    from_date = models.DateField('From Date', blank=True, null=True)
    to_date = models.DateField('To Date', blank=True, null=True)

    def __str__(self):
        return '{}'.format(self.model_type)

    class Meta:
        verbose_name = "Export Xls Report"
        verbose_name_plural = "Export Xls Reports"


### Signals  ####
def password_change_signal(sender, instance, **kwargs):
    """This method is used for capturing password change
	and removes force password change on login"""
    try:
        user = BaseUser.objects.get(username=instance.username)
        if not user.password == instance.password:
            instance.force_password_change = False
    except:
        pass


signals.pre_save.connect(password_change_signal, sender=BaseUser, dispatch_uid='services.BaseUser')
