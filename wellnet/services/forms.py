import datetime
from functools import reduce

from datetimewidget.widgets import DateTimeWidget, DateWidget
from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField, UserChangeForm, UserCreationForm
from django.contrib.auth.models import Group
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django_select2.forms import ModelSelect2MultipleWidget, ModelSelect2Widget, Select2Widget

from .models import ChannelPartner, Booking, CustomerInvoice, Product, Customer, CustomerCategory, PaymentType, \
    ChannelPartnerSegment, Employee, LeadStatus, StatusReason, Lead, City, ProductQuantity, CustomerProductQuantity, \
    MoreInfo, PartnerBranch, PartnerAsOwner, ProductSegmentPrice, ProductPrice, \
    InventoryInvoice, Machine, BookingService, Dealers, DealersType, SupplierManagement, State, InventoryManagement, \
    FieldEmployeesActivityReport, ExportXls, Reports, ProFormaBooking, ProFormaProductQuantity

dateTimeOptions = {
    'format': 'dd/mm/yyyy',
    'autoclose': True,
        'todayBtn': 'true',
    'showMeridian': True
}

dateformatoptions = {
    'format': 'yyyy/mm/dd',
    'autoclose': True,
    'showMeridian': True
}

dobOptions = {
    'format': 'dd/mm/yyyy',
    'autoclose': True,
    'showMeridian': True,
    'startView': 4
}

scheduleTimeOptions = {
    'format': 'dd/mm/yyyy HH:ii:00',
    'todayHighlight': True,
    'autoclose': True,
    'todayBtn': 'true',
    'showMeridian': True
}
serviceDateTimeOptions = {
    'format': 'dd/mm/yyyy HH:ii:00',
    'todayHighlight': True,
    'autoclose': True,
    'todayBtn': 'true',
    'showMeridian': True
}
Time_Option = {
    'format': 'HH:ii P',
}


class CascadeModelSelect2Widget(ModelSelect2Widget):
    filter_field = None
    filter_value = None

    def __init__(self, *args, **kwargs):
        self.filter_field = kwargs.pop('filter_field', self.filter_field)
        self.filter_value = kwargs.pop('filter_val', self.filter_value)
        defaults = {'data_view': 'cascade_model_select2_widget'}
        defaults.update(kwargs)
        super(CascadeModelSelect2Widget, self).__init__(*args, **defaults)

    def build_attrs(self, extra_attrs=None, **kwargs):
        model_id = "id_{}".format(self.filter_field)
        attrs = super(CascadeModelSelect2Widget, self).build_attrs(extra_attrs=extra_attrs, **kwargs)
        attrs.setdefault('data-filter_model_id', model_id)
        if self.filter_value != None:
            attrs.setdefault('data-filter_val', self.filter_value)
        return attrs

    def filter_queryset(self, term, filter_model=None, filter_val=None, queryset=None):
        """
		Return queryset filtered by search_fields matching the passed term.
		:param term: Search term
		:type term: str
		:return: Filtered queryset
		:rtype: :class:`.django.db.models.QuerySet`
		"""

        if queryset is None:
            queryset = self.get_queryset()
        search_fields = self.get_search_fields()
        select = Q()
        term = term.replace('\t', ' ')
        term = term.replace('\n', ' ')
        for t in [t for t in term.split(' ') if not t == '']:
            select &= reduce(lambda x, y: x | Q(**{y: t}), search_fields,
                             Q(**{search_fields[0]: t}))

        if filter_model and filter_val:
            if filter_model.startswith('self'):
                model = filter_model.split('.')[1]
                if model == 'channelpartner':
                    primaryKey = 'pk__in'
                    try:
                        partner = ChannelPartner.objects.filter(pk=filter_val)[0]
                        primaryKey = 'pk__in'
                        keys = [segment.id for segment in partner.segments.all()]
                        anotherSelect = Q(**{primaryKey: keys})
                    except:
                        primaryKey = 'pk__in'
                        keys = [segment.id for segment in ChannelPartnerSegment.objects.all()]
                        anotherSelect = Q(**{primaryKey: keys})
                elif model == 'subdealer':
                    primaryKey = 'pk__in'
                    try:
                        partner = ChannelPartner.objects.filter(createdBy__pk=filter_val)
                        keys = [cp.pk for cp in partner]
                        anotherSelect = Q(**{primaryKey: keys})
                    except:
                        pass
                elif model == 'machine':
                    primaryKey = 'pk__in'
                    try:
                        machines = Machine.objects.filter(is_assigned=False)
                        keys = [machine.pk for machine in machines]
                        anotherSelect = Q(**{primaryKey: keys})
                    except:
                        pass
                else:
                    return queryset.none()
            else:
                primaryKey = filter_model + '__pk'
                anotherSelect = Q(**{primaryKey: filter_val})
            return queryset.filter(select | anotherSelect).distinct()
        else:
            return queryset.none()


class PartnerBranchForm(forms.ModelForm):
    class Meta(object):
        model = PartnerBranch
        fields = "__all__"
        widgets = {
            'branch_address': forms.Textarea(attrs={'cols': 25, 'rows': 3}),
            'authorized_person_gender': Select2Widget,
            'authorized_person_address': forms.Textarea(attrs={'cols': 25, 'rows': 3}),
            'state': ModelSelect2Widget(
                model=State,
                search_fields=['state__name__icontains'],
            ),
            'city': ModelSelect2Widget(
                model=City,
                search_fields=['name__icontains', 'state__name__icontains'],
            ),
        }

    # validate city with respect to state
    def clean_city(self):
        city = self.cleaned_data.get("city")
        state1 = self.cleaned_data.get("state")
        if not state1:
            raise forms.ValidationError("Please select the state first.")
        else:
            if state1.id != city.state.id:
                raise forms.ValidationError("Please select the city maching to state!")
        return city


class PartnerAsOwnerForm(forms.ModelForm):
    class Meta(object):
        model = PartnerAsOwner
        fields = "__all__"
        widgets = {
            'gender': Select2Widget,
            'address': forms.Textarea(attrs={'cols': 25, 'rows': 3}),
        }


class ProductQuantityForm(forms.ModelForm):
    class Meta(object):
        model = ProductQuantity
        fields = ['product', 'quantity', 'IGST_percentage', 'CGST_percentage', 'SGST_percentage', 'base_price',
                  'gross_amount']
        widgets = {
            'product': ModelSelect2Widget(
                model=Product,
                search_fields=['description__icontains'],
            ),
            'gross_amount': forms.TextInput(
                attrs={'readonly': 'readonly'}
            ), 'CGST_percentage': forms.TextInput(
                attrs={'readonly': 'readonly'}
            ), 'SGST_percentage': forms.TextInput(
                attrs={'readonly': 'readonly'}
            ), 'IGST_percentage': forms.TextInput(
                attrs={'readonly': 'readonly'}
            ),
        }
        labels = {
            "IGST_percentage": "IGST In %",
            "CGST_percentage": "CGST In %",
            "SGST_percentage": "SGST In %"
        }

class ProFormaProductQuantityForm(forms.ModelForm):
    class Meta(object):
        model = ProFormaProductQuantity
        fields = ['product', 'quantity', 'IGST_percentage', 'CGST_percentage', 'SGST_percentage', 'base_price',
                  'gross_amount']
        widgets = {
            'product': ModelSelect2Widget(
                model=Product,
                search_fields=['description__icontains'],
            ),
            'gross_amount': forms.TextInput(
                attrs={'readonly': 'readonly'}
            ), 'CGST_percentage': forms.TextInput(
                attrs={'readonly': 'readonly'}
            ), 'SGST_percentage': forms.TextInput(
                attrs={'readonly': 'readonly'}
            ), 'IGST_percentage': forms.TextInput(
                attrs={'readonly': 'readonly'}
            ),
        }
        labels = {
            "IGST_percentage": "IGST In %",
            "CGST_percentage": "CGST In %",
            "SGST_percentage": "SGST In %"
        }


class CustomerProductQuantityForm(forms.ModelForm):
    class Meta(object):
        model = CustomerProductQuantity
        fields = ['product', 'quantity', 'gross_amount']
        widgets = {
            'product': ModelSelect2Widget(
                model=Product,
                search_fields=['description__icontains'],
            ),
            'quantity': forms.TextInput(),
            'gross_amount': forms.TextInput(),
        }


class EmployeeCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Employee
        fields = "__all__"

        widgets = {
            'current_address': forms.Textarea(attrs={'cols': 25, 'rows': 3}),
            'permanent_address': forms.Textarea(attrs={'cols': 25, 'rows': 3}),
            'date_of_birth': DateWidget(options=dobOptions, bootstrap_version=3),
            'hire_date': DateWidget(options=dateTimeOptions, bootstrap_version=3),
        }

    def __init__(self, *args, **kwargs):
        super(EmployeeCreationForm, self).__init__(*args, **kwargs)
        if not self.instance or not self.instance.pk:
            self.fields['password1'].required = False
            self.fields['password2'].required = False

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = super(EmployeeCreationForm, self).clean_password2()
        if bool(password1) ^ bool(password2):
            raise forms.ValidationError("Fill out both fields")
        return password2


class EmployeeChangeForm(UserChangeForm):
    password = ReadOnlyPasswordHashField(label=_("Password"),
                                         help_text=_("Raw passwords are not stored, so there is no way to see "
                                                     "this user's password, but you can change the password "
                                                     "using <a href=\"password/\">this form</a>."))

    def save(self, commit=True):
        user = super(EmployeeChangeForm, self).save(commit=False)
        if commit:
            user.save()
        return user

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]

    class Meta(UserChangeForm.Meta):
        model = Employee
        fields = "__all__"
        widgets = {
            'current_address': forms.Textarea(attrs={'cols': 25, 'rows': 3}),
            'permanent_address': forms.Textarea(attrs={'cols': 25, 'rows': 3}),
            'date_of_birth': DateWidget(options=dobOptions, bootstrap_version=3),
            'hire_date': DateWidget(options=dateTimeOptions, bootstrap_version=3),
        }


class ChannelPartnerForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = ChannelPartner
        widgets = {
            'segments': ModelSelect2MultipleWidget(
                model=ChannelPartnerSegment,
                search_fields=['description__icontains'],
            ),
            'manager': ModelSelect2Widget(
                model=Employee,
                search_fields=[
                    'username__icontains',
                    'email__icontains',
                    'phone_number__icontains', ],
            ),
            'dealership_category': ModelSelect2Widget(
                model=DealersType,
                search_fields=[''],
            ),
            'state': ModelSelect2Widget(
                model=State,
                search_fields=['state__name__icontains'],
            ),
            'city': ModelSelect2Widget(
                model=City,
                search_fields=['name__icontains', 'state__name__icontains'],
            ),
            'company_address': forms.Textarea(attrs={'cols': 25, 'rows': 3}),
            'year_of_establishment': Select2Widget,
        }
        labels = {
            "manager": "Wellnet Manager"
        }
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(ChannelPartnerForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.manager:
            self.initial['manager'] = self.instance.manager.pk
        self.fields['segments'].help_text = ''
        if not self.instance or not self.instance.pk:
            self.fields['password1'].required = False
            self.fields['password2'].required = False

    # validate city with respect to state
    def clean_city(self):
        city = self.cleaned_data.get("city")
        state1 = self.cleaned_data.get("state")
        if not state1:
            raise forms.ValidationError("Please select the state first.")
        else:
            if state1.id != city.state.id:
                raise forms.ValidationError("Please select the city maching to state!")
        return city

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = super(ChannelPartnerForm, self).clean_password2()
        if bool(password1) ^ bool(password2):
            raise forms.ValidationError("Fill out both fields")
        return password2

    def save(self, commit=True):
        owner = self.cleaned_data['manager']
        if owner and not owner.pk:
            raise forms.ValidationError("Invalid manager")
        self.instance.manager = owner
        user = super(ChannelPartnerForm, self).save(commit=False)
        user.set_password("guest")
        if commit:
            user.save()
        return user

    class Media:
        js = ('services/js/partner.js',)


class ChannelPartnerChangeForm(UserChangeForm):
    password = ReadOnlyPasswordHashField(label=_("Password"),
                                         help_text=_("Raw passwords are not stored, so there is no way to see "
                                                     "this user's password, but you can change the password "
                                                     "using <a href=\"password/\">this form</a>."))

    def __init__(self, *args, **kwargs):
        super(ChannelPartnerChangeForm, self).__init__(*args, **kwargs)
        self.fields['segments'].help_text = ''

    def save(self, commit=True):
        user = super(ChannelPartnerChangeForm, self).save(commit=False)
        if commit:
            user.save()
        return user

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value

        # return is commenting because client had asked to remove the password field from partners
        # return self.initial["password"]
        pass

    def clean_city(self):
        city = self.cleaned_data.get("city")
        state1 = self.cleaned_data.get("state")
        if not state1:
            raise forms.ValidationError("Please select the state first.")
        else:
            if state1.id != city.state.id:
                raise forms.ValidationError("Please select the city maching to state!")
        return city

    class Meta(UserChangeForm.Meta):
        model = ChannelPartner
        widgets = {
            'segments': ModelSelect2MultipleWidget(
                model=ChannelPartnerSegment,
                search_fields=['description__icontains'],
            ),
            'manager': ModelSelect2Widget(
                model=Employee,
                search_fields=[
                    'username__icontains',
                    'email__icontains',
                    'phone_number__icontains', ],
            ),
            # 'state': ModelSelect2Widget(
            #     model=State,
            #     search_fields=['state__name__icontains'],
            # ) ,
            # 'city': ModelSelect2Widget(
            #     model=City,
            #     search_fields=['name__icontains', 'state__name__icontains'],
            # ),
            'company_address': forms.Textarea(attrs={'cols': 25, 'rows': 3}),
            'year_of_establishment': Select2Widget,
        }
        labels = {
            "manager": "Wellnet Manager"
        }
        fields = "__all__"

    class Media:
        js = ('services/js/partner.js',)


class BookingForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(BookingForm, self).__init__(*args, **kwargs)
        self.fields['SGST_amount'].initial = 0
        self.fields['CGST_amount'].initial = 0
        self.fields['amount'].initial = 0
        self.fields['SGST_amount'].widget.attrs['readonly'] = True
        self.fields['CGST_amount'].widget.attrs['readonly'] = True
        self.fields['IGST_amount'].widget.attrs['readonly'] = True
        self.fields['amount'].widget.attrs['readonly'] = True
        self.fields['gross_amount'].widget.attrs['readonly'] = True
        try:
            self.fields['expected_delivery_date'].initial = timezone.now() + timezone.timedelta(days=3)
        except:
            pass  # ignore keyerror
        l = self.request.user.groups.values_list('name', flat=True)
        if 'SubDealer' in l:
            self.fields['createdFor'].widget.widget = ModelSelect2Widget(
                model=ChannelPartner,
                search_fields=['username__icontains',
                               'first_name__icontains',
                               'phone_number__icontains',
                               'company_name__icontains',
                               'email__icontains',
                              # 'authorized_person_name__icontains',
                              # 'authorized_person_mobile_number__icontains',
                              # 'authorized_person_email__icontains'
                              ],
                filter_field='self.subdealer',
                filter_val=self.request.user.pk,
            )

    def clean(self):
        data = None
        try:
            data = super(BookingForm, self).clean()
            payment_type = data.get('payment_type', None)
            is_immediate = data.get('is_immediate', False)
            is_cancelled = data.get('is_cancelled', False)
            if is_cancelled:
                if len(data.get('cancel_reason', '')) < 20:
                    self.add_error('cancel_reason', _("Enter minimum 30 characters"))
            if not is_immediate:
                expected_delivery_date = data.get('expected_delivery_date', timezone.now())
            send_receipt = data.get('send_receipt', False)
            if send_receipt:
                if data.get('contact_number', '') != '' and not data.get('contact_number', '').isdigit():
                    self.add_error('contact_number', _("This field can take only numeric values"))
                if payment_type.id == 1 or payment_type.id == 2:
                    if data.get('cheque_dd_number', '') == '':
                        self.add_error('cheque_dd_number', _("This field is required"))
                    elif not data.get('cheque_dd_number', '').isdigit():
                        self.add_error('cheque_dd_number', _("This field can take only numeric values"))
                    if data.get('cheque_dd_date', '') == '':
                        self.add_error('cheque_dd_date', _("This field is required"))
                    if data.get('bank_name', '') == '':
                        self.add_error('bank_name', _("This field is required"))
                    if data.get('bank_branch', '') == '':
                        self.add_error('bank_branch', _("This field is required"))
                    if data.get('realisation_date', '') == '':
                        self.add_error('realisation_date', _("This field is required"))
                elif payment_type.id == 3:
                    if data.get('utr_number', '') == '':
                        self.add_error('utr_number', _("This field is required"))
                    if data.get('transfer_date', '') == '':
                        self.add_error('transfer_date', _("This field is required"))
                    if data.get('bank_name', '') == '':
                        self.add_error('bank_name', _("This field is required"))
                    if data.get('bank_branch', '') == '':
                        self.add_error('bank_branch', _("This field is required"))
                    if data.get('realisation_date', '') == '':
                        self.add_error('realisation_date', _("This field is required"))
                if data.get('order_delivery_date', '') == '':
                    self.add_error('order_delivery_date', _("This field is required"))
        except AttributeError:
            raise forms.ValidationError(_(
                'Some required fields are missing from the form, make sure you have right permission to book an order.'),
                code='required')
        return data

    class Meta(object):
        model = Booking
        fields = "__all__"
        widgets = {
            'payment_type': ModelSelect2Widget(
                model=PaymentType,
                search_fields=['description__icontains'],
            ),
            'order_delivery_type': Select2Widget,
            'createdFor': ModelSelect2Widget(
                model=ChannelPartner,
                search_fields=['username__icontains',
                               'first_name__icontains',
                               'phone_number__icontains',
                               'company_name__icontains',
                               'email__icontains',
                              # 'authorized_person_name__icontains',
                              # 'authorized_person_mobile_number__icontains',
                              # 'authorized_person_email__icontains'
                              ],
            ),
            'expected_delivery_date': DateWidget(options=dateTimeOptions, bootstrap_version=3),
            'order_delivery_date': DateWidget(options=dateTimeOptions, bootstrap_version=3),
            'realisation_date': DateWidget(options=dateTimeOptions, bootstrap_version=3),
            'cheque_dd_date': DateWidget(options=dateTimeOptions, bootstrap_version=3),
            'transfer_date': DateWidget(options=dateTimeOptions, bootstrap_version=3),
            'cancel_reason': forms.Textarea(attrs={'cols': 25, 'rows': 3}),
        }

    class Media:
        js = ('services/js/invoice.js',)


class ProFormaBookingForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProFormaBookingForm, self).__init__(*args, **kwargs)
        self.fields['SGST_amount'].initial = 0
        self.fields['CGST_amount'].initial = 0
        self.fields['amount'].initial = 0
        self.fields['SGST_amount'].widget.attrs['readonly'] = True
        self.fields['CGST_amount'].widget.attrs['readonly'] = True
        self.fields['IGST_amount'].widget.attrs['readonly'] = True
        self.fields['amount'].widget.attrs['readonly'] = True
        self.fields['gross_amount'].widget.attrs['readonly'] = True
        l = self.request.user.groups.values_list('name', flat=True)
        if 'SubDealer' in l:
            self.fields['createdFor'].widget.widget = ModelSelect2Widget(
                model=ChannelPartner,
                search_fields=['username__icontains',
                               'first_name__icontains',
                               'phone_number__icontains',
                               'company_name__icontains',
                               'email__icontains',
                              # 'authorized_person_name__icontains',
                              # 'authorized_person_mobile_number__icontains',
                              # 'authorized_person_email__icontains'
                              ],
                filter_field='self.subdealer',
                filter_val=self.request.user.pk,
            )


    class Meta(object):
        model = ProFormaBooking
        fields = "__all__"
        widgets = {
            'created_For': ModelSelect2Widget(
                model=ChannelPartner,
                search_fields=['username__icontains',
                               'first_name__icontains',
                               'phone_number__icontains',
                               'company_name__icontains',
                               'email__icontains',
                             #  'authorized_person_name__icontains',
                             #  'authorized_person_mobile_number__icontains',
                             #  'authorized_person_email__icontains'
                             ],
            ),
        }

    class Media:
        js = ('services/js/pro_forma_invoice.js',)


class CustomerForm(forms.ModelForm):
    class Meta(object):
        model = Customer
        fields = ['first_name', 'last_name', 'gender', 'mobile_number', 'email', 'address',
                  'pin_code']


class CustomerInvoiceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CustomerInvoiceForm, self).__init__(*args, **kwargs)
        self.fields['service_tax'].initial = 0
        self.fields['vat'].initial = 0
        self.fields['amount'].initial = 0
        self.fields['gross_amount'].initial = 0
        self.fields['service_tax'].widget.attrs['readonly'] = True
        self.fields['gross_amount'].widget.attrs['readonly'] = True
        self.fields['vat'].widget.attrs['readonly'] = True
        self.fields['amount'].widget.attrs['readonly'] = True
        self.fields['service_tax'].widget = forms.HiddenInput()
        self.fields['vat'].widget = forms.HiddenInput()
        self.fields['gross_amount'].widget = forms.HiddenInput()

        self.fields['partner_segment'].widget.widget = CascadeModelSelect2Widget(
            model=ChannelPartnerSegment,
            search_fields=['description__icontains'],
            filter_field='self.channelpartner',
            filter_val=self.request.user.pk
        )
        partner_segment = ChannelPartnerSegment.objects.filter(channelpartner__pk=self.request.user.pk)[0]
        self.fields['partner_segment'].initial = int(partner_segment.id)

    def clean(self):
        data = None
        try:
            data = super(CustomerInvoiceForm, self).clean()
            if data and data.get('segment', None):
                segments = data.get('segment', None)
                if segments.id == 1:
                    if data.get('building_name', None) is None or len(data.get('building_name', '')) == 0:
                        self.add_error('building_name', _("This field is required"))
                    if data.get('pin_code', '') == '':
                        self.add_error('pin_code', _("This field is required"))
                    elif not data.get('pin_code', '').isdigit():
                        self.add_error('pin_code', _("This field can take only numeric values"))
                elif segments.id == 2 or segments.id == 3 or segments.id == 4:
                    if data.get('company_name', None) is None or len(data.get('company_name', '')) == 0:
                        self.add_error('company_name', _("This field is required"))
                    if data.get('building_name', None) is None or len(data.get('building_name', '')) == 0:
                        self.add_error('building_name', _("This field is required"))
                    if data.get('pin_code', '') == '' or not data.get('pin_code', ''):
                        self.add_error('pin_code', _("This field is required"))
                    elif not data.get('pin_code', '').isdigit():
                        self.add_error('pin_code', _("This field can take only numeric values"))
                elif segments.id == 5:
                    if data.get('vehicle_category', None) is None:
                        self.add_error('vehicle_category', _("This field is required"))
                    if data.get('vehicle_name', None) is None or len(data.get('vehicle_name', '')) == 0:
                        self.add_error('vehicle_name', _("This field is required"))
                    if data.get('vehicle_registration_no', None) is None or len(
                            data.get('vehicle_registration_no', '')) == 0:
                        self.add_error('vehicle_registration_no', _("This field is required"))
            payment_type = data.get('payment_type', None)
            send_receipt = data.get('send_receipt', False)
            if send_receipt:
                if payment_type.id == 1 or payment_type.id == 2:
                    if data.get('cheque_dd_number', '') == '':
                        self.add_error('cheque_dd_number', _("This field is required"))
                    elif not data.get('cheque_dd_number', '').isdigit():
                        self.add_error('cheque_dd_number', _("This field can take only numeric values"))
                    if data.get('cheque_dd_date', '') == '':
                        self.add_error('cheque_dd_date', _("This field is required"))
                    if data.get('bank_name', '') == '':
                        self.add_error('bank_name', _("This field is required"))
                    if data.get('bank_branch', '') == '':
                        self.add_error('bank_branch', _("This field is required"))
                    if data.get('realisation_date', '') == '':
                        self.add_error('realisation_date', _("This field is required"))
                elif payment_type.id == 3:
                    if data.get('utr_number', '') == '':
                        self.add_error('utr_number', _("This field is required"))
                    if data.get('transfer_date', '') == '':
                        self.add_error('transfer_date', _("This field is required"))
                    if data.get('bank_name', '') == '':
                        self.add_error('bank_name', _("This field is required"))
                    if data.get('bank_branch', '') == '':
                        self.add_error('bank_branch', _("This field is required"))
                    if data.get('realisation_date', '') == '':
                        self.add_error('realisation_date', _("This field is required"))
        except AttributeError:
            # raise forms.ValidationError(_('Some required fields are missing from the form, make sure you have right permission to add invoice.'), code='required')
            pass
        return data

    class Meta(object):
        model = CustomerInvoice
        fields = ['user', 'payment_type', 'segment', 'same_address_as_user', 'address', 'vehicle_category',
                  'send_receipt', 'gross_amount']
        widgets = {
            'user': ModelSelect2Widget(
                model=Customer,
                search_fields=[
                    'first_name__icontains',
                    'last_name__icontains',
                    'mobile_number__icontains',
                    'email__icontains'
                ],
            ),
            'address': forms.Textarea(attrs={'cols': 25, 'rows': 3}),
            'segment': ModelSelect2Widget(
                model=CustomerCategory,
                search_fields=['description__icontains'],
            ),
            'payment_type': ModelSelect2Widget(
                model=PaymentType,
                search_fields=['description__icontains'],
            ),
            'vehicle_category': Select2Widget,
            'realisation_date': DateWidget(options=dateTimeOptions, bootstrap_version=3),
            'cheque_dd_date': DateWidget(options=dateTimeOptions, bootstrap_version=3),
            'transfer_date': DateWidget(options=dateTimeOptions, bootstrap_version=3),
        }

    class Media:
        js = ('services/js/customer_invoice.js',)


class LeadForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(LeadForm, self).__init__(*args, **kwargs)
        self.fields['segments'].help_text = ''

    def clean(self):
        data = None
        try:
            data = super(LeadForm, self).clean()
            reason = data.get('reason', None)
            status = data.get('status', None)
            comments = data.get('comments', '')
            mobile_number = data.get('mobile_number', '')
            landline_number = data.get('landline_number', '')
            pin_code = data.get('pin_code', '')
            if not reason:
                self.add_error('reason', _("This field is required"))
            else:
                if reason.id == 9:
                    more_details = data.get('more_details', None)
                    if not more_details:
                        self.add_error('more_details', _("This field is required"))
                    nxt_apt_date = data.get('next_appointment', None)
                    if not nxt_apt_date:
                        self.add_error('next_appointment', _("This field is required"))
                    elif nxt_apt_date < timezone.now():
                        self.add_error('next_appointment', _("Appointment cannot be set to previous date or time"))
                elif reason.id == 8 or reason.id == 1:
                    nxt_apt_date = data.get('next_appointment', None)
                    if not nxt_apt_date:
                        self.add_error('next_appointment', _("This field is required"))
                    elif nxt_apt_date < timezone.now():
                        self.add_error('next_appointment', _("Appointment cannot be set to previous date or time"))
                if reason.id >= 1 and reason.id <= 6 or reason.id == 9 or reason.id == 8:
                    if comments == '':
                        self.add_error('comments', _("This field is required"))
            if mobile_number != '' and not mobile_number.isdigit():
                self.add_error('mobile_number', _("This field can take only numeric values"))
            if landline_number != '' and not landline_number.isdigit():
                self.add_error('landline_number', _("This field can take only numeric values"))
            if pin_code != '' and not pin_code.isdigit():
                self.add_error('pin_code', _("This field can take only numeric values"))
        except AttributeError:
            pass
        return data

    class Meta(object):
        model = Lead
        widgets = {
            'status': ModelSelect2Widget(
                model=LeadStatus,
                search_fields=['description__icontains'],
            ),
            'reason': CascadeModelSelect2Widget(
                model=StatusReason,
                search_fields=['description__icontains'],
                filter_field='status',
            ),
            'segments': ModelSelect2MultipleWidget(
                model=ChannelPartnerSegment,
                search_fields=['description__icontains'],
            ),
            'city': ModelSelect2Widget(
                model=City,
                search_fields=['name__icontains', 'state__name__icontains'],
            ),
            'address': forms.Textarea(attrs={'cols': 25, 'rows': 3}),
            'call_source': Select2Widget,
            'product_demo': Select2Widget,
            'channelpartner': ModelSelect2Widget(
                model=ChannelPartner,
                search_fields=['username__icontains',
                              # 'owners_name__icontains',
                               'phone_number__icontains',
                               'company_name__icontains',
                               'mobile_number__icontains',
                               'authorized_person_name__icontains',
                               'authorized_person_mobile_number__icontains',
                               'authorized_person_email__icontains'],
            ),
            'more_details': ModelSelect2MultipleWidget(
                model=MoreInfo,
                search_fields=['info__icontains'],
            ),
            'registration_form': Select2Widget,
            'payment_collected': Select2Widget,
            'goods_delivered': Select2Widget,
            'comments': forms.Textarea(attrs={'cols': 25, 'rows': 3}),
        }
        exclude = ('updated',)

    class Media:
        js = ('services/js/leads.js',)


class ProductSegmentPriceForm(forms.ModelForm):
    class Meta(object):
        model = ProductSegmentPrice
        fields = "__all__"
        widgets = {
            'user_group': ModelSelect2Widget(
                model=Group,
                search_fields=['name__icontains'],
            ),
            'product': ModelSelect2Widget(
                model=Product,
                search_fields=['description__icontains'],
            ),
            'segment': ModelSelect2Widget(
                model=CustomerCategory,
                search_fields=['description__icontains'],
            ),
            'vehicle_category': Select2Widget,
        }

    def clean(self):
        data = None
        try:
            data = super(ProductSegmentPriceForm, self).clean()
            segment = data.get('segment', None)
            vehicle_category = data.get('vehicle_category', None)
            if segment and segment.id == 5:
                if not vehicle_category:
                    self.add_error('vehicle_category', _("This field is required when segment is Vehicles."))
        except AttributeError:
            pass
        return data

    class Media:
        js = ('services/js/product_segment_price.js',)


class ProductPriceForm(forms.ModelForm):
    class Meta(object):
        model = ProductPrice
        fields = "__all__"
        widgets = {
            'user_group': ModelSelect2Widget(
                model=Group,
                search_fields=['name__icontains'],
            ),
        }

    class Media:
        js = ('services/js/remove_extra_save_button.js',)


class InventoryInvoiceForm(forms.ModelForm):
    class Meta(object):
        model = InventoryInvoice
        fields = "__all__"
        widgets = {
            'machine': CascadeModelSelect2Widget(
                model=Machine,
                search_fields=['machine_number__icontains'],
                filter_field='self.machine',
                filter_val=False
            ),
            'partner': ModelSelect2Widget(
                model=ChannelPartner,
                search_fields=['username__icontains',
                              # 'owners_name__icontains',
                               'phone_number__icontains',
                               'company_name__icontains',
                               'mobile_number__icontains',
                               'authorized_person_name__icontains',
                               'authorized_person_mobile_number__icontains',
                               'authorized_person_email__icontains'],
            ),
            'payment_type': ModelSelect2Widget(
                model=PaymentType,
                search_fields=['description__icontains'],
            ),
            'difference_payment_type': ModelSelect2Widget(
                model=PaymentType,
                search_fields=['description__icontains'],
            ),
            'settlement_date': DateTimeWidget(options=dateTimeOptions, bootstrap_version=3),
        }
        exclude = ('createdBy', 'updatedBy',)

    class Media:
        js = ('services/js/inventory_invoice.js',)

    def clean(self):
        data = None
        try:
            data = super(InventoryInvoiceForm, self).clean()
            payment_type = data.get('payment_type', None)
            send_receipt = data.get('send_receipt', False)
            goods_sold = data.get('goods_sold', False)
            isSettlement = False
            if goods_sold:
                isSettlement = True
                if data.get('settlement_date', None) is None:
                    self.add_error('settlement_date', _("This field is required"))
                if data.get('goods_price', None) is None:
                    self.add_error('goods_price', _("This field is required"))
            else:
                if data.get('settlement_amount', None) is not None or data.get('settlement_date', None) is not None:
                    isSettlement = True
                    if data.get('settlement_date', None) is None:
                        self.add_error('settlement_date', _("This field is required"))
                    elif data.get('settlement_amount', None) is None:
                        self.add_error('settlement_amount', _("This field is required"))

            if send_receipt:
                if payment_type.id == 1 or payment_type.id == 2:
                    if data.get('cheque_dd_number', '') == '':
                        self.add_error('cheque_dd_number', _("This field is required"))
                    elif not data.get('cheque_dd_number', '').isdigit():
                        self.add_error('cheque_dd_number', _("This field can take only numeric values"))
                    if data.get('cheque_dd_date', '') == '':
                        self.add_error('cheque_dd_date', _("This field is required"))
                    if data.get('bank_name', '') == '':
                        self.add_error('bank_name', _("This field is required"))
                    if data.get('bank_branch', '') == '':
                        self.add_error('bank_branch', _("This field is required"))
                    if data.get('realisation_date', '') == '':
                        self.add_error('realisation_date', _("This field is required"))
                elif payment_type.id == 3:
                    if data.get('utr_number', '') == '':
                        self.add_error('utr_number', _("This field is required"))
                    if data.get('transfer_date', '') == '':
                        self.add_error('transfer_date', _("This field is required"))
                    if data.get('bank_name', '') == '':
                        self.add_error('bank_name', _("This field is required"))
                    if data.get('bank_branch', '') == '':
                        self.add_error('bank_branch', _("This field is required"))
                    if data.get('realisation_date', '') == '':
                        self.add_error('realisation_date', _("This field is required"))
                if isSettlement:
                    security_deposite = data.get('security_deposite_amount', None)
                    settlement_amount = data.get('settlement_amount', None)
                    goods_price = data.get('goods_price', None)
                    diff_amount = data.get('difference_amount', None)
                    if settlement_amount is not None:
                        settlement = settlement_amount
                    elif goods_price is not None:
                        settlement = goods_price
                    else:
                        settlement = 0
                    if security_deposite != settlement:
                        if diff_amount is None:
                            self.add_error('difference_amount', _("This field is required"))
                        else:
                            if diff_amount != abs(security_deposite - settlement):
                                self.add_error('difference_amount', _(
                                    "This field has incorrect value, it should be {}".format(
                                        abs(security_deposite - settlement))))
                        diff_payment_type = data.get('difference_payment_type', None)
                        if diff_payment_type is None:
                            self.add_error('difference_payment_type', _("This field is required"))
                        else:
                            if diff_payment_type.id == 1 or diff_payment_type.id == 2:
                                if data.get('difference_cheque_dd_number', '') == '':
                                    self.add_error('difference_cheque_dd_number', _("This field is required"))
                                elif not data.get('difference_cheque_dd_number', '').isdigit():
                                    self.add_error('difference_cheque_dd_number',
                                                   _("This field can take only numeric values"))
                                if data.get('difference_cheque_dd_date', None) is None:
                                    self.add_error('difference_cheque_dd_date', _("This field is required"))
                                if data.get('difference_bank_name', '') == '':
                                    self.add_error('difference_bank_name', _("This field is required"))
                                if data.get('difference_bank_branch', '') == '':
                                    self.add_error('difference_bank_branch', _("This field is required"))
                                if data.get('difference_realisation_date', None) is None:
                                    self.add_error('difference_realisation_date', _("This field is required"))
                            elif diff_payment_type.id == 3:
                                if data.get('difference_utr_number', '') == '':
                                    self.add_error('difference_utr_number', _("This field is required"))
                                if data.get('difference_transfer_date', None) is None:
                                    self.add_error('difference_transfer_date', _("This field is required"))
                                if data.get('difference_bank_name', '') == '':
                                    self.add_error('difference_bank_name', _("This field is required"))
                                if data.get('difference_bank_branch', '') == '':
                                    self.add_error('difference_bank_branch', _("This field is required"))
                                if data.get('difference_realisation_date', None) is None:
                                    self.add_error('rdifference_ealisation_date', _("This field is required"))
        except AttributeError:
            # raise forms.ValidationError(_('Some required fields are missing from the form, make sure you have right permission to add invoice.'), code='required')
            pass
        return data


class MachineForm(forms.ModelForm):
    class Meta(object):
        model = Machine
        fields = '__all__'
        widgets = {
            'warranty_start_date': DateWidget(options=dateTimeOptions, bootstrap_version=3),
            'warranty_end_date': DateWidget(options=dateTimeOptions, bootstrap_version=3),
        }


class BookingServiceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(BookingServiceForm, self).__init__(*args, **kwargs)
        self.fields['address'].required = False

    class Meta(object):
        model = BookingService
        fields = '__all__'
        widgets = {
            # Use localization and bootstrap 3
            'booking_date': DateTimeWidget(usel10n=True, options=serviceDateTimeOptions, bootstrap_version=3),
        }


class DealersForm(forms.ModelForm):
    class Meta(object):
        model = Dealers
        fields = '__all__'


class SupplierManagementForm(forms.ModelForm):
    class Meta(object):
        model = SupplierManagement
        fields = '__all__'
        widgets = {
            'state': ModelSelect2Widget(
                model=State,
                search_fields=['state__name__icontains'],
            ),
            'city': ModelSelect2Widget(
                model=City,
                search_fields=['name__icontains', 'state__name__icontains'],
            ),
            'agreement_date': DateTimeWidget(usel10n=True, options=serviceDateTimeOptions, bootstrap_version=3),
        }


class InventoryManagementForm(forms.ModelForm):
    class Meta(object):
        model = InventoryManagement
        fields = '__all__'
        widgets = {
            'current_ownership': ModelSelect2Widget(
                model=ChannelPartner,
                search_fields=['username__icontains',
                              # 'owners_name__icontains',
                               'phone_number__icontains',
                               'company_name__icontains',
                               'mobile_number__icontains',
                               'authorized_person_name__icontains',
                               'authorized_person_mobile_number__icontains',
                               'authorized_person_email__icontains'],
            ),
            'date_of_receipt': DateWidget(options=dateTimeOptions, bootstrap_version=3),
            'expiry_date': DateWidget(options=dateTimeOptions, bootstrap_version=3),
            'dispatch_date': DateWidget(options=dateTimeOptions, bootstrap_version=3)
        }

class ReportsForm(forms.ModelForm):
    class Meta(object):
        model = Reports
        fields = "__all__"

        widgets = {
            'state': ModelSelect2Widget(
                model=State,
                search_fields=['state__name__icontains'],
            ),
            'city': ModelSelect2Widget(
                model=City,
                search_fields=['name__icontains', 'state__name__icontains'],
            ),
            #
            # 'time_from':forms.TimeField(input_formats=['%I:%M %p'],widget=TIMEWIDGET),
            # 'time_to':forms.TimeField(input_formats=['%I:%M %p'],widget=TIMEWIDGET),
            # 'time_to':SelectTimeWidget(twelve_hr=True),
            # 'time_from': SelectTimeWidget(twelve_hr=True,minute_step = 5 ,attrs={"Hour":"Hour","Minutes":"Minutes"}),
            # 'time_to': SelectTimeWidget(twelve_hr=True, minute_step = 5)
            #  'time_from': TimeWidget( ),
            # 'time_to': TimeWidget( )

        }




    def clean_city(self):
        city = self.cleaned_data.get("city")

        state1 = self.cleaned_data.get("state")
        if not state1:
            raise forms.ValidationError("Please select the state first.")
        else:
            if state1.id != city.state.id:
                raise forms.ValidationError("Please select the city maching to state!")
        return city


class FieldEmployeesActivityReportForm(forms.ModelForm):
    class Meta(object):
        model = FieldEmployeesActivityReport
        fields = '__all__'
        widgets = {
            'date': DateWidget(options=dateTimeOptions, bootstrap_version=3),

        }

    def clean(self):
        data = super(FieldEmployeesActivityReportForm, self).clean()
        date = data.get('date', None)
        if date:
            if date > datetime.datetime.now().date():
                self.add_error('date', _("You can not select future date"))
        return data
    
    labels = {
            "createdBy": "Wellnet Manager"
        }
    class Media:
        js = ('services/js/field_employee.js',)


class ProductForm(forms.ModelForm):
    class Meta(object):
        model = Product
        fields = '__all__'


class ExportXlsForm(forms.ModelForm):
    class Meta(object):
        model = ExportXls
        fields = '__all__'
        widgets = {
            'to_date': DateTimeWidget(options=dateTimeOptions, bootstrap_version=3),
            'from_date': DateTimeWidget(options=dateTimeOptions, bootstrap_version=3),
        }

    def clean(self):
        data = super(ExportXlsForm, self).clean()
        from_date = data.get('from_date', None)
        model_type = data.get('model_type', None)
        to_date = data.get('to_date', None)
        if model_type < 5:
            if from_date and to_date:
                if not to_date:
                    self.add_error('to_date', _("This field is required"))
                if to_date > datetime.date.today():
                    self.add_error('to_date', _("You can not select future date"))
                if from_date > datetime.date.today():
                    self.add_error('from_date', _("You can not select future date"))
                if from_date > to_date:
                    self.add_error('from_date',
                                   _("Please choose proper from date( From Date should be lesser than To Date"))
            else:
                raise forms.ValidationError("Date fields are required")
        else:
            return data

    class Media:
        js = ('services/js/xls_report.js',)
