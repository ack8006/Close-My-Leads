from django.utils import simplejson as json
import urllib2
import base64
import time
import Crypto


def decoded_cookie_str(encoded_cookie_str):
    return base64.b64decode(encoded_cookie_str)

def encoded_cookie_str(raw_cookie_str):
    return base64.b64encode(raw_cookie_str)

def setcookie(self, raw_key):
    self.response.headers['Set-Cookie'] = 'auth='+encoded_cookie_str(raw_key)
    self.response.headers['Set-Cookie'] += '; Expires=Wed, 09 Jun 2025 10:18:14 GMT'

def list_twenty_leads_from_offset(self, offset):
    decoded_cookie = decoded_cookie_str(self.request.cookies.get('auth'))
    url = 'https://hubapi.com/leads/v1/list/?hapikey='+decoded_cookie
    url += '&excludeConversionEvents=true&max=21'
    url += '&offset='+str(offset)
    url += '&sort=lastName'
    return json.load(urllib2.urlopen(url))

def is_lead(self, offset):
    decoded_cookie = decoded_cookie_str(self.request.cookies.get('auth'))
    url = 'https://hubapi.com/leads/v1/list/?hapikey='+decoded_cookie
    url += '&excludeConversionEvents=true&max=1'
    url += '&offset='+str(offset)
    url += '&sort=lastName'
    return json.load(urllib2.urlopen(url))

def portal_from_key(self):
    addr="https://hubapi.com/settings/v1/settings?hapikey="
    addr += self.request.get('api_key')
    try:
        real_portal = str(json.load(urllib2.urlopen(addr))[0]['portalId'])
    except:
        real_portal='None'
    return real_portal

def offset_from_page(self):
    offset = self.request.get('offset')
    if self.request.get('next'):
        return str(int(offset)+20)
    elif self.request.get('prev'):
        return str(max([int(offset)-20, 0]))
    else:
        return '0'

def format_date(date_string):
    if date_string==0:
        return 'Open'
    else:
        big_date = time.ctime(date_string).split()
        return ' '.join([seg for seg in d if ':' not in seg])

demo_leads_response = [
    {
        'firstName':"Andy", 'lastName':"Aylward", 'email':"aaylward@gmail.com",
        'guid':"67892349872634", 'closedAt':"Open"
    },
    {
        'firstName':"Mike", 'lastName':"Aylward", 'email':"maylward@gmail.com",
        'guid':"98234576923425", 'closedAt':"Open"
    }
    ]
