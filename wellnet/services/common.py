import datetime
import json
import re
from decimal import *

import requests
from django.contrib.humanize.templatetags.humanize import intcomma
from wellnet.settings import EKONNECT_ACCOUNT_ID as userid
from wellnet.settings import EKONNECT_NEW_BOOKING_TEMPLATE_ID as new_book_id
from wellnet.settings import EKONNECT_NEW_ORDER_TEMPLATE_ID as new_order_id
from wellnet.settings import EKONNECT_NEW_ORDER_V2_TEMPLATE_ID as new_order_v2_id
from wellnet.settings import EKONNECT_NEW_PARTNER_TEMPLATE_ID as new_partner_id
from wellnet.settings import EKONNECT_SERVICE_REMAINDER_TEMPLATE_ID  as remainder_service_id

from .models import CustomerProductQuantity, ChannelPartner, PartnerAsOwner, ProductQuantity


def send_service_reminder(invoice):
    products_ordered = CustomerProductQuantity.objects.filter(invoice=invoice)
    if len(products_ordered) != 0:
        products = [prod.product.id for prod in products_ordered if prod.product.type == 2]  # type 2 is service
        if len(products) != 0:
            name = invoice.user.first_name  # parameter 1
            category = invoice.segment.description  # parameter 2
            created_on = invoice.created_date.strftime('%d/%m/%Y')  # parameter 3
            partner = ChannelPartner.objects.get(pk=invoice.createdBy.pk)
            partner_company = partner.company_name  # parameter 4
            area = partner.city.name  # parameter 5
            number = invoice.user.mobile_number
            service_due_date = datetime.date.today() + datetime.timedelta(days=5)
            date_string = service_due_date.strftime('%d/%m/%Y')  # parameter 6
            # Call sms api here for service reminder template, use EKONNECT_ACCOUNT_ID
            send_service_reminder_sms(name,category,created_on,partner_company,area,date_string,number)


def send_service_reminder_sms(name,category,created_on,partner_company,area,date_string,number):
    sms_url = "http://104.236.156.119:3675/restconf/operations/server/send-message"
    body = {
        "input": {
                "numbers": [number],
                "user-uuid": userid,
                "msg-template": remainder_service_id,
                "msg-template-var": {
                  "variables": [
                    {
                      "param-id": "Username",
                      "value":name
                    },
                    {
                      "param-id": "ServiceName",
                      "value": category
                    },
                    {
                      "param-id": "Date",
                      "value": str(created_on)
                    },
                    {
                      "param-id": "Place",
                      "value": partner_company
                    },
                    {
                       "param-id": "AnotherPlace",
                       "value": area
                    },
                    {
                          "param-id": "Product",
                          "value": str(date_string)
                    }
                ]
            }
        }
    }
    headers = {'content-type': 'application/json'}
    r = requests.post(sms_url, data=json.dumps(body), headers=headers)
    return r


def send_booking_confirmation(booking):
    owner = PartnerAsOwner.objects.filter(partner=booking.createdFor)[0]
    name = owner.name  # parameter 1
    order_id = booking.id  # parameter 2
    number = owner.mobile_number
    products = ProductQuantity.objects.filter(booking=booking)
    if len(products) != 0:
        prod_str = ""
        for product in products:
            prod_str += str(product.product.description) + " (" + str(product.quantity) + ") and "
        prod_str = prod_str[:-5]  # parameter 3
        amount = "Rs. " + intcomma(str(Decimal(booking.amount)
                                       .quantize(Decimal('.01'), rounding=ROUND_DOWN)))  # parameter 4
        # Call sms api here for new booking
        send_booking_confirmation_sms(name, order_id, prod_str, amount, number)


def send_booking_confirmation_sms(name, order_id, prod_str, amount, num):
    sms_url = "http://104.236.156.119:3675/restconf/operations/server/send-message"
    body = {
        "input": {
                "numbers": [num],
                "user-uuid": userid,
                "msg-template": new_book_id,
                "msg-template-var": {
                  "variables": [
                    {
                      "param-id": "Username",
                      "value": name
                    },
                    {
                      "param-id": "OrderNo",
                      "value": str(order_id)
                    },
                    {
                      "param-id": "ProductName",
                      "value": prod_str
                    },
                    {
                      "param-id": "TotalAmount",
                      "value": str(amount)
                    }
                ]
            }
        }
    }
    headers = {'content-type': 'application/json'}
    r = requests.post(sms_url, data=json.dumps(body), headers=headers)
    return r


def send_customer_invoice_confirmation(invoice):
    products_ordered = CustomerProductQuantity.objects.filter(invoice=invoice)
    if len(products_ordered) != 0:
        products_array = [prod.product for prod in products_ordered]
        products = ''
        for product in products_array:
            if product.type == 2:
                products += 'doing ' + product.description + ' service to your ' + invoice.segment.description
            else:
                products += 'buying ' + product.description + ' product'
            products += ' and '
        name = invoice.user.first_name  # parameter 1
        products = products[:-5]  # parameter 2
        partner = ChannelPartner.objects.get(pk=invoice.createdBy.pk)
        number = invoice.user.mobile_number
        partner_company = partner.company_name  # parameter 3
        # Call SMS api here for new customer invoice
        send_customer_invoice_confirmation_sms_v2(name, products, partner_company, number)


def send_customer_invoice_confirmation_sms(name, products, partner_company,num):
    sms_url = "http://104.236.156.119:3675/restconf/operations/server/send-message"
    body = {
                    "input": {
                        "numbers": [num],
                        "user-uuid": userid,
                        "msg-template": new_order_id,
                        "msg-template-var": {
                            "variables": [
                                {
                                    "param-id": "Username",
                                    "value": name
                                },
                                {
                                    "param-id": "Products",
                                    "value": products
                                },
                                {
                                    "param-id": "PartnerName",
                                    "value": partner_company
                                }
                            ]
                        }
                    }
                }
    headers = {'content-type': 'application/json'}
    r = requests.post(sms_url, data=json.dumps(body), headers=headers)
    return r

def send_customer_invoice_confirmation_sms_v2(name, products, partner_company,num):
    sms_url = "http://104.236.156.119:3675/restconf/operations/server/send-message"
    body = {
                    "input": {
                        "numbers": [num],
                        "user-uuid": userid,
                        "msg-template": new_order_v2_id,
                        "msg-template-var": {
                            "variables": [
                                {
                                    "param-id": "Username",
                                    "value": name
                                },
                                {
                                    "param-id": "PartnerName",
                                    "value": partner_company
                                }
                            ]
                        }
                    }
                }
    headers = {'content-type': 'application/json'}
    r = requests.post(sms_url, data=json.dumps(body), headers=headers)
    return r


def send_partner_onboarding_confirmation(partner):
    owner = PartnerAsOwner.objects.filter(partner=partner)[0]
    name = owner.name  # parameter 1
    number = owner.mobile_number
    # Call SMS api here for new partner - no parameters in template
    send_partner_onboarding_confirmation_sms(name, number)
    #pass


def send_partner_onboarding_confirmation_sms(name, num):
    sms_url = "http://104.236.156.119:3675/restconf/operations/server/send-message"
    body = {
        "input": {
                "numbers": [num],
                "user-uuid": userid,
                "msg-template": new_partner_id,
                "msg-template-var": {
                    "variables": [
                        {
                            "param-id": "name",
                            "value": name
                        }
                    ]
                }
        }
    }
    headers = {'content-type': 'application/json'}
    r = requests.post(sms_url, data=json.dumps(body), headers=headers)
    return r


def send_message(num, msg_tmp_name=None, **kwargs):
    if '+91' in num:
        num = num[3:]
    senderid = 'WELNET'
    url2 = ''
    for param, val in kwargs.items():
        url2 += '&{}={}'.format(param, val)
    url1 = "https://websms.way2mint.com/index.php/web_service/sendSMS?username=forkt&password=f0rkt3ch90909&destination={}&template_name={}".format(
        num, msg_tmp_name)
    url = url1 + url2 + '&response_format=json&sender_id={}'.format(senderid)
    r = requests.post(url)
    r.status_code = '200 OK'
    # logger.debug("url {}, code {}, text {}".format(url, r.status_code, r.text))
    return r.status_code


def get_msg_template_var_from_tmpl(tmpl_name):
    # way2mint provides url only for list templates duh!
    get_tmpl_url = 'https://websms.way2mint.com/index.php/web_service/listusertemplates?username=forkt&password=f0rkt3ch90909&response_format=json'
    tresp = requests.get(get_tmpl_url)
    templ_list = json.loads(tresp.text)
    # each templates message is present in tmpl['content']
    tmplate = [tmpl['content'] for tmpl in templ_list[
        'content'] if tmpl['template_name'] == tmpl_name]
    '''
    the regex pattern is the one maintained by way2mint websms
    hence seraching for it here
    '''
    regex = re.compile('#~.~#')
    # tmplate[0] gives string from the list
    tmplate_var = re.findall(regex, tmplate[0])
    v = 0
    for var in tmplate_var:
        tmplate_var[v] = "templateParameters[" + \
                         "".join(re.findall("[a-zA-Z]+", var)) + "]"
        v += 1
    # returns a list of template variables
    return tmplate_var
