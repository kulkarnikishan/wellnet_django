import collections

from django.http import HttpResponse
from django.http import HttpResponseNotFound

from .models import *


def customer_invoice_by_segment_monthly():
    categories = CustomerCategory.objects.all()
    segments = ChannelPartnerSegment.objects.all()
    today = datetime.datetime.now()
    customer_invoices = CustomerInvoice.objects.filter(created_date__year=today.year, created_date__month=today.month)
    row = {category.description: 0 for category in categories}
    row = collections.OrderedDict(sorted(row.items()))
    segments_table = {segment.description: row for segment in segments}
    segments_table = collections.OrderedDict(sorted(segments_table.items()))
    for invoice in customer_invoices:
        segments_table[invoice.partner_segment.description][invoice.segment.description] += 1
    print(segments_table)
    return segments_table


def customer_invoice_by_segment_daily():
    categories = CustomerCategory.objects.all()
    segments = ChannelPartnerSegment.objects.all()
    today = datetime.datetime.now()
    customer_invoices = CustomerInvoice.objects.filter(created_date=today)
    row = {category.description: 0 for category in categories}
    row = collections.OrderedDict(sorted(row.items()))
    segments_table = {segment.description: row for segment in segments}
    segments_table = collections.OrderedDict(sorted(segments_table.items()))
    for invoice in customer_invoices:
        segments_table[invoice.partner_segment.description][invoice.segment.description] += 1
    print(segments_table)
    return segments_table


def customer_bill_amt_by_segment_monthly():
    categories = CustomerCategory.objects.all()
    segments = ChannelPartnerSegment.objects.all()
    today = datetime.datetime.now()
    customer_invoices = CustomerInvoice.objects.filter(created_date__year=today.year, created_date__month=today.month)
    row = {category.description: 0 for category in categories}
    row = collections.OrderedDict(sorted(row.items()))
    segments_table = {segment.description: row for segment in segments}
    segments_table = collections.OrderedDict(sorted(segments_table.items()))
    for invoice in customer_invoices:
        segments_table[invoice.partner_segment.description][invoice.segment.description] += invoice.amount
    print(segments_table)
    return segments_table


def customer_bill_amt_by_segment_daily():
    categories = CustomerCategory.objects.all()
    segments = ChannelPartnerSegment.objects.all()
    today = datetime.datetime.now()
    customer_invoices = CustomerInvoice.objects.filter(created_date=today)
    row = {category.description: 0 for category in categories}
    row = collections.OrderedDict(sorted(row.items()))
    segments_table = {segment.description: row for segment in segments}
    segments_table = collections.OrderedDict(sorted(segments_table.items()))
    for invoice in customer_invoices:
        segments_table[invoice.partner_segment.description][invoice.segment.description] += invoice.amount
    print(segments_table)
    return segments_table


def customer_vehicle_type_monthly():
    categories = VEHICLE_CATEGORY
    segments = ChannelPartnerSegment.objects.all()
    today = datetime.datetime.now()
    customer_invoices = CustomerInvoice.objects.filter(created_date__year=today.year, created_date__month=today.month)
    row = {value: 0 for (key, value) in categories}
    row = collections.OrderedDict(sorted(row.items()))
    segments_table = {segment.description: row for segment in segments}
    segments_table = collections.OrderedDict(sorted(segments_table.items()))
    for invoice in customer_invoices:
        if invoice.vehicle_category:
            segments_table[invoice.partner_segment.description][invoice.vehicle_category] += 1
    print(segments_table)
    return segments_table


def customer_vehicle_type_daily():
    categories = VEHICLE_CATEGORY
    segments = ChannelPartnerSegment.objects.all()
    today = datetime.datetime.now()
    customer_invoices = CustomerInvoice.objects.filter(created_date=today)
    row = {value: 0 for (key, value) in categories}
    row = collections.OrderedDict(sorted(row.items()))
    segments_table = {segment.description: row for segment in segments}
    segments_table = collections.OrderedDict(sorted(segments_table.items()))
    for invoice in customer_invoices:
        if invoice.vehicle_category:
            segments_table[invoice.partner_segment.description][invoice.vehicle_category] += 1
    print(segments_table)
    return segments_table


def emp_based_partner_activation_monthly():
    employees = Employee.objects.all()
    segments = ChannelPartnerSegment.objects.all()
    array = ["Total No of Partners", "Active Partners", "Active Partners %", "Inactive Partners", "Inactive Partners %"]
    row = {segment.description: 0 for segment in segments}
    row = collections.OrderedDict(sorted(row.items()))
    table = {item: row for item in array}
    table = collections.OrderedDict(sorted(table.items()))
    emp_list = []
    today = datetime.datetime.now()
    customer_invoices = CustomerInvoice.objects.filter(created_date__year=today.year, created_date__month=today.month)
    cp_ids = [invoice.createdBy.id for invoice in customer_invoices]
    active_cps = ChannelPartner.objects.filter(pk__in=cp_ids)
    emp_table = {}
    for employee in employees:
        emp_table[employee.name] = table
        partners = ChannelPartner.objects.filter(manager=employee)
        num_of_partners = partners.count()
        active_partners = active_cps.filter(manager=employee)
        inactive_partners = partners.exclude(pk__in=cp_ids)
        num_active_partners = active_partners.count()
        num_of_inactive_partners = inactive_partners.count()
        for cp in active_partners:
            for segment in cp.segments.all():
                emp_table[employee.name]["Active Partners"][segment.description] += 1
        for cp in inactive_partners:
            for segment in cp.segments.all():
                emp_table[employee.name]["Inactive Partners"][segment.description] += 1
        for segment, value in emp_table[employee.name]["Active Partners"]:
            total = value + emp_table[employee.name]["Inactive Partners"][segment]
            emp_table[employee.name]["Total No of Partners"][segment] = total
            if total != 0:
                emp_table[employee.name]["Inactive Partners %"][segment] = \
                    emp_table[employee.name]["Inactive Partners"][segment] / total * 100
                emp_table[employee.name]["Active Partners %"][segment] = value / total * 100
            else:
                emp_table[employee.name]["Inactive Partners %"][segment] = 0
                emp_table[employee.name]["Active Partners %"][segment] = 0
    print(emp_table)
    return emp_table


def emp_based_partner_activation_daily():
    employees = Employee.objects.all()
    segments = ChannelPartnerSegment.objects.all()
    array = ["Total No of Partners", "Active Partners", "Active Partners %", "Inactive Partners", "Inactive Partners %"]
    row = {segment.description: 0 for segment in segments}
    row = collections.OrderedDict(sorted(row.items()))
    table = {item: row for item in array}
    table = collections.OrderedDict(sorted(table.items()))
    emp_list = []
    today = datetime.datetime.now()
    customer_invoices = CustomerInvoice.objects.filter(created_date=today)
    cp_ids = [invoice.createdBy.id for invoice in customer_invoices]
    active_cps = ChannelPartner.objects.filter(pk__in=cp_ids)
    emp_table = {}
    for employee in employees:
        emp_table[employee.name] = table
        partners = ChannelPartner.objects.filter(manager=employee)
        num_of_partners = partners.count()
        active_partners = active_cps.filter(manager=employee)
        inactive_partners = partners.exclude(pk__in=cp_ids)
        num_active_partners = active_partners.count()
        num_of_inactive_partners = inactive_partners.count()
        for cp in active_partners:
            for segment in cp.segments.all():
                emp_table[employee.name]["Active Partners"][segment.description] += 1
        for cp in inactive_partners:
            for segment in cp.segments.all():
                emp_table[employee.name]["Inactive Partners"][segment.description] += 1
        for segment, value in emp_table[employee.name]["Active Partners"].items():
            total = value + emp_table[employee.name]["Inactive Partners"][segment]
            emp_table[employee.name]["Total No of Partners"][segment] = total
            if total != 0:
                emp_table[employee.name]["Inactive Partners %"][segment] = \
                    emp_table[employee.name]["Inactive Partners"][segment] / total * 100
                emp_table[employee.name]["Active Partners %"][segment] = value / total * 100
            else:
                emp_table[employee.name]["Inactive Partners %"][segment] = 0
                emp_table[employee.name]["Active Partners %"][segment] = 0
    print(emp_table)
    return emp_table


def order_tracking_monthly():
    partners = ChannelPartner.objects.all()
    partners_table = {}
    today = datetime.datetime.now()
    bookings = Booking.objects.filter(created_date__year=today.year, created_date__month=today.month)
    for partner in partners:
        partner_bookings = bookings.filter(createdFor=partner)
        partners_table[partner.company_name] = []
        for booking in partner_bookings:
            booking_details = {}
            booking_details["segment"] = [segment.description for segment in partner.segments.all()]
            booking_details["order_date"] = booking.expected_delivery_date
            booking_details["receive_date"] = booking.order_delivery_date
            booking_details["turn_around_time"] = booking.order_delivery_date - booking.expected_delivery_date
            partners_table[partner.company_name].append(booking_details)
    print(partners_table)
    return partners_table


def order_tracking_daily():
    partners = ChannelPartner.objects.all()
    partners_table = {}
    today = datetime.datetime.now()
    bookings = Booking.objects.filter(created_date=today)
    for partner in partners:
        partner_bookings = bookings.filter(createdFor=partner)
        partners_table[partner.company_name] = []
        for booking in partner_bookings:
            booking_details = {}
            booking_details["segment"] = [segment.description for segment in partner.segments.all()]
            booking_details["order_date"] = booking.expected_delivery_date
            booking_details["receive_date"] = booking.order_delivery_date
            booking_details["turn_around_time"] = booking.order_delivery_date - booking.expected_delivery_date
            partners_table[partner.company_name].append(booking_details)
    print(partners_table)
    return partners_table


def lead_status_monthly():
    employees = Employee.objects.all()
    today = datetime.datetime.now()
    leads = Lead.objects.filter(created_date__year=today.year, created_date__month=today.month)
    emp_table = []
    for employee in employees:
        row = {}
        emp_leads = leads.filter(createdBy=employee)
        ineffective_leads = emp_leads.filter(status=LeadStatus.objects.filter(pk=2))
        effective_leads = emp_leads.filter(status=LeadStatus.objects.filter(pk=1))
        conversion_leads = emp_leads.filter(status=LeadStatus.objects.filter(pk=3))
        row["name"] = employee.name
        row["total_calls"] = emp_leads.count()
        row["effective_leads"] = effective_leads.count()
        row["ineffective_leads"] = ineffective_leads.count()
        row["conversion"] = conversion_leads.count()
        if row["total_calls"] != 0:
            row["effective_leads_percent"] = row["effective_leads"] / row["total_calls"] * 100
            row["ineffective_leads_percent"] = row["ineffective_leads"] / row["total_calls"] * 100
            row["conversion_percent"] = row["conversion"] / row["total_calls"] * 100
        else:
            row["effective_leads_percent"] = 0
            row["ineffective_leads_percent"] = 0
            row["conversion_percent"] = 0
        emp_table.append(row)
    print(emp_table)
    return emp_table


def lead_status_daily():
    employees = Employee.objects.all()
    today = datetime.datetime.now()
    leads = Lead.objects.filter(created_date=today)
    emp_table = []
    for employee in employees:
        row = {}
        emp_leads = leads.filter(createdBy=employee)
        ineffective_leads = emp_leads.filter(status=LeadStatus.objects.filter(pk=2))
        effective_leads = emp_leads.filter(status=LeadStatus.objects.filter(pk=1))
        conversion_leads = emp_leads.filter(status=LeadStatus.objects.filter(pk=3))
        row["name"] = employee.name
        row["total_calls"] = emp_leads.count()
        row["effective_leads"] = effective_leads.count()
        row["ineffective_leads"] = ineffective_leads.count()
        row["conversion"] = conversion_leads.count()
        if row["total_calls"] != 0:
            row["effective_leads_percent"] = row["effective_leads"] / row["total_calls"] * 100
            row["ineffective_leads_percent"] = row["ineffective_leads"] / row["total_calls"] * 100
            row["conversion_percent"] = row["conversion"] / row["total_calls"] * 100
        else:
            row["effective_leads_percent"] = 0
            row["ineffective_leads_percent"] = 0
            row["conversion_percent"] = 0
        emp_table.append(row)
    print(emp_table)
    return emp_table


def lead_source_monthly():
    employees = Employee.objects.all()
    today = datetime.datetime.now()
    leads = Lead.objects.filter(created_date__year=today.year, created_date__month=today.month)
    emp_table = []
    for employee in employees:
        row = {}
        emp_leads = leads.filter(createdBy=employee)
        database = emp_leads.filter(call_source=1)
        reference = emp_leads.filter(call_source=2)
        cold_call = emp_leads.filter(call_source=3)
        website = emp_leads.filter(call_source=4)
        row["database"] = database.count()
        row["reference"] = reference.count()
        row["cold_call"] = cold_call.count()
        row["website"] = website.count()
        row["total_leads"] = emp_leads.count()
        if row["total_leads"] != 0:
            row["database_percentage"] = row["database"] / row["total_leads"] * 100
            row["reference_percentage"] = row["reference"] / row["total_leads"] * 100
            row["cold_call_percentage"] = row["cold_call"] / row["total_leads"] * 100
            row["website_percentage"] = row["website"] / row["total_leads"] * 100
        else:
            row["database_percentage"] = 0
            row["reference_percentage"] = 0
            row["cold_call_percentage"] = 0
            row["website_percentage"] = 0
        row["name"] = employee.name
        emp_table.append(row)
    print(emp_table)
    return emp_table


def lead_source_daily():
    employees = Employee.objects.all()
    today = datetime.datetime.now()
    leads = Lead.objects.filter(created_date=today)
    emp_table = []
    for employee in employees:
        row = {}
        emp_leads = leads.filter(createdBy=employee)
        database = emp_leads.filter(call_source=1)
        reference = emp_leads.filter(call_source=2)
        cold_call = emp_leads.filter(call_source=3)
        website = emp_leads.filter(call_source=4)
        row["database"] = database.count()
        row["reference"] = reference.count()
        row["cold_call"] = cold_call.count()
        row["website"] = website.count()
        row["total_leads"] = emp_leads.count()
        if row["total_leads"] != 0:
            row["database_percentage"] = row["database"] / row["total_leads"] * 100
            row["reference_percentage"] = row["reference"] / row["total_leads"] * 100
            row["cold_call_percentage"] = row["cold_call"] / row["total_leads"] * 100
            row["website_percentage"] = row["website"] / row["total_leads"] * 100
        else:
            row["database_percentage"] = 0
            row["reference_percentage"] = 0
            row["cold_call_percentage"] = 0
            row["website_percentage"] = 0
        row["name"] = employee.name
        emp_table.append(row)
    print(emp_table)
    return emp_table


def lead_postponed_daily():
    today = datetime.datetime.now()
    employees = Employee.objects.all()
    leads = Lead.objects.filter(created_date=today)
    emp_table = []
    for employee in employees:
        row = {}
        emp_leads = leads.filter(createdBy=employee)
        next_apmnt = emp_leads.filter(reason_id=8)
        require_more = emp_leads.filter(reason_id=9)
        row["name"] = employee.name
        row["total_leads"] = emp_leads.count()
        row["next_apmnt"] = next_apmnt.count()
        row["require_more"] = require_more.count()
        if row["total_leads"] != 0:
            row["next_apmnt_percent"] = row["next_apmnt"] / row["total_leads"] * 100
            row["require_more_percent"] = row["require_more"] / row["total_leads"] * 100
        else:
            row["next_apmnt_percent"] = 0
            row["require_more_percent"] = 0
        emp_table.append(row)
    print(emp_table)
    return emp_table


def lead_postponed_monthly():
    today = datetime.datetime.now()
    employees = Employee.objects.all()
    leads = Lead.objects.filter(created_date__year=today.year, created_date__month=today.month)
    emp_table = []
    for employee in employees:
        row = {}
        emp_leads = leads.filter(createdBy=employee)
        next_apmnt = emp_leads.filter(reason_id=8)
        require_more = emp_leads.filter(reason_id=9)
        row["name"] = employee.name
        row["total_leads"] = emp_leads.count()
        row["next_apmnt"] = next_apmnt.count()
        row["require_more"] = require_more.count()
        if row["total_leads"] != 0:
            row["next_apmnt_percent"] = row["next_apmnt"] / row["total_leads"] * 100
            row["require_more_percent"] = row["require_more"] / row["total_leads"] * 100
        else:
            row["next_apmnt_percent"] = 0
            row["require_more_percent"] = 0
        emp_table.append(row)
    print(emp_table)
    return emp_table


def lead_ineffective_monthly():
    today = datetime.datetime.now()
    employees = Employee.objects.all()
    leads = Lead.objects.filter(created_date__year=today.year, created_date__month=today.month)
    emp_table = []
    for employee in employees:
        row = {}
        emp_leads = leads.filter(createdBy=employee)
        not_interested = emp_leads.filter(reason_id=2)
        cannot_afford = emp_leads.filter(reason_id=3)
        profit_too_low = emp_leads.filter(reason_id=4)
        less_clients = emp_leads.filter(reason_id=5)
        no_manpower = emp_leads.filter(reason_id=6)
        row["name"] = employee.name
        row["total_leads"] = emp_leads.count()
        row["not_interested"] = not_interested.count()
        row["cannot_afford"] = cannot_afford.count()
        row["profit_too_low"] = profit_too_low.count()
        row["less_clients"] = less_clients.count()
        row["no_manpower"] = no_manpower.count()
        if row["total_leads"] != 0:
            row["not_interested_percent"] = row["not_interested"] / row["total_leads"] * 100
            row["cannot_afford_percent"] = row["cannot_afford"] / row["total_leads"] * 100
            row["profit_too_low_percent"] = row["profit_too_low"] / row["total_leads"] * 100
            row["less_clients_percent"] = row["less_clients"] / row["total_leads"] * 100
            row["no_manpower_percent"] = row["no_manpower"] / row["total_leads"] * 100
        else:
            row["not_interested_percent"] = 0
            row["cannot_afford_percent"] = 0
            row["profit_too_low_percent"] = 0
            row["less_clients_percent"] = 0
            row["no_manpower_percent"] = 0
        emp_table.append(row)
    print(emp_table)
    return emp_table


def lead_ineffective_daily():
    today = datetime.datetime.now()
    employees = Employee.objects.all()
    leads = Lead.objects.filter(created_date=today)
    emp_table = []
    for employee in employees:
        row = {}
        emp_leads = leads.filter(createdBy=employee)
        not_interested = emp_leads.filter(reason_id=2)
        cannot_afford = emp_leads.filter(reason_id=3)
        profit_too_low = emp_leads.filter(reason_id=4)
        less_clients = emp_leads.filter(reason_id=5)
        no_manpower = emp_leads.filter(reason_id=6)
        row["name"] = employee.name
        row["total_leads"] = emp_leads.count()
        row["not_interested"] = not_interested.count()
        row["cannot_afford"] = cannot_afford.count()
        row["profit_too_low"] = profit_too_low.count()
        row["less_clients"] = less_clients.count()
        row["no_manpower"] = no_manpower.count()
        if row["total_leads"] != 0:
            row["not_interested_percent"] = row["not_interested"] / row["total_leads"] * 100
            row["cannot_afford_percent"] = row["cannot_afford"] / row["total_leads"] * 100
            row["profit_too_low_percent"] = row["profit_too_low"] / row["total_leads"] * 100
            row["less_clients_percent"] = row["less_clients"] / row["total_leads"] * 100
            row["no_manpower_percent"] = row["no_manpower"] / row["total_leads"] * 100
        else:
            row["not_interested_percent"] = 0
            row["cannot_afford_percent"] = 0
            row["profit_too_low_percent"] = 0
            row["less_clients_percent"] = 0
            row["no_manpower_percent"] = 0
        emp_table.append(row)
    print(emp_table)
    return emp_table


def daily_reporting():
    customer_invoice_by_segment_daily()
    customer_bill_amt_by_segment_daily()
    customer_vehicle_type_daily()
    emp_based_partner_activation_daily()
    order_tracking_daily()
    lead_status_daily()
    lead_source_daily()
    lead_postponed_daily()
    lead_ineffective_daily()


def monthly_reporting():
    customer_invoice_by_segment_monthly()
    customer_bill_amt_by_segment_monthly()
    customer_vehicle_type_monthly()
    emp_based_partner_activation_monthly()
    order_tracking_monthly()
    lead_status_monthly()
    lead_source_monthly()
    lead_postponed_monthly()
    lead_ineffective_monthly()


def export_xls(obj, request):
    import xlwt
    l = request.user.groups.values_list('name', flat=True)
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename={}.xls'.format(
        "{} Report".format(obj.get_model_type_display()))
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet("{}".format(str(obj.get_model_type_display())))
    ws2 = wb.add_sheet("{}-detailed".format(str(obj.get_model_type_display())))
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    font_style_for_data = xlwt.XFStyle()
    font_style_for_data.alignment.wrap = 1
    row_num = 0
    ws2_row_num = 0
    if obj.model_type == 1:
        # Booking
        if 'SuperAdmin' in l:
            model_obj = Booking.objects.filter(created_date__range=[obj.from_date, obj.to_date])
        else:
            # model_obj = [each_booking for each_booking in
            #              Booking.objects.filter(created_date__range=[obj.from_date, obj.to_date]) if
            #              each_booking.createdFor.manager.id == request.user.id]
            """
            comment the below two lines (521,522) before deploying it to production and uncomment the above code
            for model_obj
            """
            model_obj = [each_booking for each_booking in
                         Booking.objects.filter(created_date__range=[obj.from_date, obj.to_date])]
        if model_obj:
            columns = ['Sl No.', 'Invoice Id',
                       'Product', 'payment_type', 'gross_amount', 'amount', 'SGST_amount', 'CGST_amount',
                       'IGST_amount',  # 'cheque_dd_number',# 'cheque_dd_date',# 'utr_number',
                       'transfer_date',  # 'bank_name',# 'bank_branch',
                       'realisation_date',  # 'is_immediate',# 'is_IGST',
                       'expected_delivery_date',
                       'order_dispatch_date',  # 'order_delivery_type',
                       'courier_company_name',
                       'pod_number',
                       'GSTIN',
                       'created_date',
                       'updated',
                       # 'send_receipt',
                       'dealer code',
                       'dealership_category',
                       'createdFor',
                       'city', 'state',
                       'createdBy',
                       'updatedBy',
                       'is Cancelled',
                       'Cancel Reason',
                       'wellnet manager',
                       'cheque_dd_number', 'bank_name', 'utr_number',
                       'requested_by']
            for col_num in range(len(columns)):
                ws.write(row_num, col_num, columns[col_num], font_style)

            # For detailed report, we need quantity as a separate column after product
            columns.insert(3, 'Quantity')
            for col_num in range(len(columns)):
                ws2.write(row_num, col_num, columns[col_num], font_style)

            for objs in model_obj:
                row_num += 1
                prd = ",".join([prod.product.description + "({})".format(prod.quantity) for prod in
                                ProductQuantity.objects.filter(booking=objs.pk)])
                gstin = objs.createdFor.GSTIN if objs.createdFor.GSTIN else ""
                dealership_cat = str(objs.createdFor.dealership_category)
                trans_date = objs.transfer_date.strftime("%d-%m-%Y") if objs.transfer_date else ""
                realisation_date = objs.realisation_date.strftime("%d-%m-%Y") if objs.realisation_date else ""
                expected_delivery_date = objs.expected_delivery_date.strftime(
                    "%d-%m-%Y") if objs.expected_delivery_date else ""
                order_delivery_date = objs.order_delivery_date.strftime("%d-%m-%Y") if objs.order_delivery_date else ""
                courier_company_name = objs.courier_company_name if objs.courier_company_name else ""
                pod_number = objs.purchase_order_number if objs.purchase_order_number else ""
                created_date = objs.created_date.strftime("%d-%m-%Y") if objs.created_date else ""
                updated = objs.updated.strftime("%d-%m-%Y") if objs.updated else ""
                iscancelled = "YES" if objs.is_cancelled else "NO"
                cancel_reason = objs.cancel_reason if objs.cancel_reason else "NA"

                row = [row_num,
                       objs.pk, prd, objs.payment_type.description, objs.gross_amount,
                       objs.amount, objs.SGST_amount, objs.CGST_amount,
                       objs.IGST_amount, trans_date, realisation_date,
                       expected_delivery_date, order_delivery_date, courier_company_name, pod_number, gstin, created_date,
                       updated, objs.createdFor.dealer_code, dealership_cat, objs.createdFor.username, objs.createdFor.city.name,
                       objs.createdFor.state.name, objs.createdBy.username,
                       objs.updatedBy.username,
                       iscancelled,
                       cancel_reason,
                       objs.createdFor.manager.username,
                       objs.cheque_dd_number, objs.bank_name, objs.utr_number,
                       request.user.username
                       ]
                for col_num in range(len(row)):
                    ws.write(row_num, col_num, row[col_num], font_style_for_data)

                # Fill the second sheet where each item in an invoice is broken down into separate rows
                for pq in ProductQuantity.objects.filter(booking=objs.pk):
                    ws2_row_num += 1
                    prd = pq.product.description
                    qty = pq.quantity
                    row = [ws2_row_num,
                           objs.pk, prd, qty, objs.payment_type.description, pq.base_price * pq.quantity,
                           pq.amount, pq.SGST_amount, pq.CGST_amount, pq.IGST_amount, trans_date, realisation_date,
                           expected_delivery_date, order_delivery_date, courier_company_name, pod_number, gstin, created_date,
                           updated, objs.createdFor.dealer_code, dealership_cat, objs.createdFor.username, objs.createdFor.city.name,
                           objs.createdFor.state.name, objs.createdBy.username,
                           objs.updatedBy.username, iscancelled, cancel_reason, objs.createdFor.manager.username,
                           objs.cheque_dd_number, objs.bank_name, objs.utr_number, request.user.username]
                    for col_num in range(len(row)):
                        ws2.write(ws2_row_num, col_num, row[col_num], font_style_for_data)

            wb.save(response)
        else:
            return HttpResponseNotFound('<h1>No entry Found</h1>')
    elif obj.model_type == 2:
        # Pro-forma-Booking
        if 'SuperAdmin' in l:
            model_obj = ProFormaBooking.objects.filter(created_date__range=[obj.from_date, obj.to_date])
        else:
            model_obj = [each_booking for each_booking in
                         ProFormaBooking.objects.filter(created_date__range=[obj.from_date, obj.to_date]) if
                         each_booking.created_For.manager.id == request.user.id]
        if model_obj:
            columns = ['Sl No.', 'ProForma-Invoice Id',
                       'Product', 'gross_amount', 'amount', 'SGST_amount', 'CGST_amount',
                       'IGST_amount',  # 'cheque_dd_number',# 'cheque_dd_date',# 'utr_number',
                       'created_date',
                       'updated',
                       # 'send_receipt',a
                       'dealer code',
                       'created_For',
                       'city',
                       'state',
                       'createdBy',
                       'updated_By',
                       'Is Cancelled',
                       'Cancel Reason',
                       'Wellnet manager',
                       'requested_by']
            for col_num in range(len(columns)):
                ws.write(row_num, col_num, columns[col_num], font_style)
            for objs in model_obj:
                row_num += 1

                prd = ",".join([prod.product.description + "({})".format(prod.quantity) for prod in
                                ProFormaProductQuantity.objects.filter(booking=objs.pk)])
                created_date = objs.created_date.strftime("%d-%m-%Y") if objs.created_date else ""
                updated = objs.updated.strftime("%d-%m-%Y") if objs.updated else ""
                iscancelled = "YES" if objs.is_cancelled else "NO"
                cancel_reason = objs.cancel_reason if objs.cancel_reason else "NA"
                row = [row_num,
                       objs.pk, prd, objs.gross_amount,
                       objs.amount, objs.SGST_amount, objs.CGST_amount,
                       objs.IGST_amount, created_date,
                       updated,
                       objs.created_For.dealer_code,
                       objs.created_For.username, objs.created_For.city.name,
                       objs.created_For.state.name, objs.createdBy.username,
                       objs.updated_By.username,
                       iscancelled,
                       cancel_reason,
                       objs.created_For.manager.username
                    , request.user.username
                       ]
                for col_num in range(len(row)):
                    ws.write(row_num, col_num, row[col_num], font_style_for_data)
            wb.save(response)
        else:
            return HttpResponseNotFound('<h1>No entry Found</h1>')
    elif obj.model_type == 3:
        # InventoryManagement
        model_obj = InventoryManagement.objects.filter(date_of_receipt__range=[obj.from_date, obj.to_date])
        if model_obj:
            columns = ['Sl No.', 'id', 'packaging_number', 'product_name', 'size', 'date_of_receipt', 'expiry_date',
                       'dispatch_date', 'current_ownership', "manager", 'requested_by', 'created date','utr number'
                       , 'payment type', 'delivery_date', 'bank_name', 'bank_branch', 'cheque_dd_date', 'cheque_dd_number'
                       , 'transfer_date', 'settlement_amt', 'settlement_date', 'goods_sold', 'goods_price'
                       , 'difference_amount', 'difference_bank_branch', 'difference_bank_name'
                       , 'difference_cheque_dd_date', 'difference_cheque_dd_number', 'difference_payment_type'
                       , 'difference_realisation_date', 'difference_transfer_date', 'difference_utr_number']

            for col_num in range(len(columns)):
                ws.write(row_num, col_num, columns[col_num], font_style)
            for objs in model_obj:
                row_num += 1
                inv_data = InventoryInvoice.objects.filter(partner=objs.current_ownership)
                if inv_data:
                    re = inv_data[0].get_json()
                # for inv in inv_data:
                #     create_date = inv.created_date if inv.created_date else ""
                row = [row_num, objs.pk, objs.packaging_number, objs.product_name.description, objs.size,
                       objs.date_of_receipt.strftime("%d-%m-%Y") if objs.date_of_receipt else "",
                       objs.expiry_date.strftime("%d-%m-%Y") if objs.expiry_date else "",
                       objs.dispatch_date.strftime("%d-%m-%Y") if objs.dispatch_date else "",
                       objs.current_ownership.username, objs.current_ownership.manager.username,
                       request.user.username,
                       re['created_date'], re['utr_number'],
                       re['payment_type'], re['delivery_date'], re['bank_name'], re['bank_branch'], re['cheque_dd_date'],
                       re['cheque_dd_number'], re['transfer_date'], re['settlement_amt'], re['settlement_date'],
                       re['goods_sold'], re['goods_price'], re['difference_amount'], re['difference_bank_branch'],
                       re['difference_bank_name'], re['difference_cheque_dd_date'], re['difference_cheque_dd_number'],
                       re['difference_payment_type'], re['difference_realisation_date'], re['difference_transfer_date'],
                       re['difference_utr_number']]
                for col_num in range(len(row)):
                    ws.write(row_num, col_num, row[col_num], font_style_for_data)
            wb.save(response)
        else:
            return HttpResponseNotFound('<h1>No entry Found</h1>')
    elif obj.model_type == 4:
        # SupplierManagement
        model_obj = [sup for sup in SupplierManagement.objects.all() if
                     (obj.to_date > sup.agreement_date.date() > obj.from_date)]
        if model_obj:
            columns = ['Sl No.', 'id', 'company_name', 'company_name_for_invoice', 'company_address', 'state',
                       'city', 'country', 'pin_code', 'phone_no', 'authorised_person', 'email_id', 'agreement_date',
                       'agreed_products', 'requested_by']
            for col_num in range(len(columns)):
                ws.write(row_num, col_num, columns[col_num], font_style)
            for objs in model_obj:
                row_num += 1
                row = [row_num, objs.pk, objs.company_name, objs.company_name_for_invoice,
                       objs.company_address,
                       objs.state.name
                    , objs.city.name, objs.country, objs.pin_code, objs.phone_no, objs.authorised_person,
                       objs.email_id, objs.agreement_date.strftime("%d-%m-%Y"), objs.agreed_products.description,
                       request.user.username]
                for col_num in range(len(row)):
                    ws.write(row_num, col_num, row[col_num], font_style_for_data)
            wb.save(response)
        else:
            return HttpResponseNotFound('<h1>No entry Found</h1>')
    elif obj.model_type == 5:
        model_obj = FieldEmployeesActivityReport.objects.filter(date__range=[obj.from_date, obj.to_date])
        calltypes = {1: 'Presentation call', 2: 'Presentation & Demo call', 3: 'Follow up', 4: 'Closure',
                     5: 'Relationship Call', 6: 'Training'}
        if model_obj:
            columns = ['Sl No.', 'Id', 'contact_number', 'name', 'designation', 'company', 'city', 'state',
                       'time_from', 'date', 'time_to', 'discussion_point', 'call_type', 'created_by',
                       'requested_by']
            for col_num in range(len(columns)):
                ws.write(row_num, col_num, columns[col_num], font_style)
            for objs in model_obj:
                sub_model_obj = Reports.objects.filter(field_emp=objs.pk)
                if sub_model_obj:
                    for sub_obj in sub_model_obj:
                        if sub_obj.call_type:
                            call_type = calltypes[sub_obj.call_type]
                        else:
                            call_type = None
                        row_num += 1
                        row = [row_num,
                               objs.id,
                               sub_obj.contact_number,
                               sub_obj.name,
                               sub_obj.designation,
                               sub_obj.company,
                               sub_obj.city.name,
                               sub_obj.state.name,
                               sub_obj.time_from.strftime('%I:%M %p'),
                               objs.date.strftime("%d-%m-%Y"),
                               sub_obj.time_to.strftime('%I:%M %p'),
                               sub_obj.discussion_point, call_type, objs.createdBy.username,
                               request.user.username,
                               ]
                        for col_num in range(len(row)):
                            ws.write(row_num, col_num, row[col_num], font_style_for_data)
            wb.save(response)
        else:
            return HttpResponseNotFound('<h1>No entry Found</h1>')
    elif obj.model_type == 6:
        # partner
        if 'SuperAdmin' in l:
            model_obj = ChannelPartner.objects.all()
        else:
            # model_obj = ChannelPartner.objects.filter(manager=request.user)
            """
            remove above comment before deploying to production and comment below code model_obj
            """
            model_obj = ChannelPartner.objects.all()
        if model_obj:
            columns = ['Sl No.', 'dealer code', 'username', 'email', 'is_staff', 'dealership_category', 'company_name',
                       'company_name_invoice', 'segments', 'state', 'city', 'company_address',
                       'pin_code', 'landline', 'GSTIN', 'company_pan_number', 'number_of_staff',
                       'number_of_branches',
                       'number_of_products', 'year_of_establishment', 'manager', 'requested_by',
                       'created date', 'utr number', 'payment type', 'delivery_date', 'bank_name',
                       'bank_branch', 'cheque_dd_date', 'cheque_dd_number', 'transfer_date',
                       'settlement_amt', 'settlement_date', 'goods_sold', 'goods_price',
                       'difference_amount', 'difference_bank_branch', 'difference_bank_name',
                       'difference_cheque_dd_date', 'difference_cheque_dd_number', 'difference_payment_type',
                       'difference_realisation_date', 'difference_transfer_date', 'difference_utr_number'
                       ]
            for col_num in range(len(columns)):
                ws.write(row_num, col_num, columns[col_num], font_style)
            for objs in model_obj:
                seg = ""
                for segment in objs.segments.all():
                    if segment:
                        seg += segment.description + ","
                row_num += 1

                inv_data = InventoryInvoice.objects.filter(partner_id=objs.pk)
                if inv_data:
                    re = inv_data[0].get_json()
                row = [row_num,
                       objs.dealer_code,
                       objs.username, objs.email, objs.is_staff, objs.dealership_category.description,
                       objs.company_name, objs.company_name_invoice, seg[:-1], objs.state.name, objs.city.name,
                       objs.company_address, objs.pin_code,
                       objs.landline, objs.GSTIN, objs.company_pan_number, objs.number_of_staff,
                       objs.number_of_branches, objs.number_of_products, objs.year_of_establishment,
                       objs.manager.name, request.user.username,
                       re['created_date'], re['utr_number'],
                       re['payment_type'], re['delivery_date'], re['bank_name'], re['bank_branch'],
                       re['cheque_dd_date'],
                       re['cheque_dd_number'], re['transfer_date'], re['settlement_amt'], re['settlement_date'],
                       re['goods_sold'], re['goods_price'], re['difference_amount'], re['difference_bank_branch'],
                       re['difference_bank_name'], re['difference_cheque_dd_date'], re['difference_cheque_dd_number'],
                       re['difference_payment_type'], re['difference_realisation_date'], re['difference_transfer_date'],
                       re['difference_utr_number']
                       ]
                for col_num in range(len(row)):
                    ws.write(row_num, col_num, row[col_num], font_style_for_data)
            wb.save(response)
        else:
            return HttpResponseNotFound('<h1>No entry Found</h1>')
    elif obj.model_type == 7:
        # product
        model_obj = Product.objects.all()
        if model_obj:
            columns = ['Sl No.', 'id', 'description', 'type', 'HSN_code', 'active', 'requested_by']
            for col_num in range(len(columns)):
                ws.write(row_num, col_num, columns[col_num], font_style)
            for objs in model_obj:
                row_num += 1
                row = [row_num, objs.pk, objs.description, objs.get_type_display(), objs.HSN_code,
                       str(bool(objs.active)),
                       request.user.username
                       ]
                for col_num in range(len(row)):
                    ws.write(row_num, col_num, row[col_num], font_style_for_data)
            wb.save(response)
        else:
            return HttpResponseNotFound('<h1>No entry Found</h1>')
    return response
