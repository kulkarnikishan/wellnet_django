from django.http import HttpResponseRedirect
from django.http import HttpResponseServerError
import re
import time

class RejectSpambotRequestsMiddleware(object):  
    def process_request(self, request):  
        t = int(time.time())
        if t % 2 == 0:
            try:
                # Log every alternate request
                fpw = open('/temp/request.log', 'w+')
                fpw.write('Got request at {}'.format(t))
                fpw.close()
            except Exception:
                # Should never happen
                return HttpResponseServerError()

class PasswordChangeMiddleware:
    def process_request(self, request):
        if request.user.is_authenticated() and re.match(r'^/admin/?', request.path) and not re.match(
                r'^/admin/password_change/?', request.path) and not re.match(r'^/admin/logout/?', request.path):
            if request.user.force_password_change:
                return HttpResponseRedirect('/admin/password_change/')
