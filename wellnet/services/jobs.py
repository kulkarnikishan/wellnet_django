from django_cron import CronJobBase, Schedule
from .models import CustomerInvoice
import datetime
from .common import send_service_reminder


class ServiceReminder(CronJobBase):

    RUN_AT_TIMES = ['08:30']
    schedule = Schedule(run_at_times=RUN_AT_TIMES)
    code = "app.jobs.ServiceReminder"

    def do(self):
        delta_days = datetime.date.today() - datetime.timedelta(days=85)
        invoices = CustomerInvoice.objects.filter(created_date=delta_days)
        if len(invoices) != 0:
            for invoice in invoices:
                send_service_reminder(invoice)

