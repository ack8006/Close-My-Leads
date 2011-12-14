from django.utils import simplejson as json
import urllib2
import base64
import time
import datetime
from sanetime import sanetime

try:
    # if keys are present, encrypt the cookies
    from supa_secret import secret_key
    if len(secret_key) not in [16, 24, 32]:
        raise
    else:
        # we only need Crypto if we have keys!
        import Crypto.Cipher.AES as aes
    keys_exist = True
except:
    # if no keys are present, just base64 encode the cookies... This should never happen though.
    # this try/except is only for testing purposes.
    keys_exist = False

PADDING = '{' #because our API key will never contain this character :)
BLOCK_SIZE = 32
LIST_URL = 'https://hubapi.com/leads/v1/list/?hapikey=%s&excludeConversionEvents=true&max=21&offset=%s&sort=lastName'
SEARCH_URL = 'https://hubapi.com/leads/v1/list/?hapikey=%s&excludeConversionEvents=true&max=21&%s=%s'
LEAD_URL = 'https://hubapi.com/leads/v1/list/?hapikey=%s&excludeConversionEvents=true&max=1&offset=%s&sort=lastName'
SETTINGS_URL = "https://hubapi.com/settings/v1/settings?hapikey=%s"
 

def pad_string(raw_string):
    output = raw_string + (BLOCK_SIZE - len(raw_string) % BLOCK_SIZE)*PADDING
    return output

def decoded_cookie_str(encoded_cookie_str):
    if keys_exist:
        cipher = aes.new(secret_key)
        return cipher.decrypt(base64.b64decode(encoded_cookie_str)).rstrip(PADDING)
    else:
        return base64.b64decode(encoded_cookie_str)

def encoded_cookie_str(raw_cookie_str):
    if keys_exist:
        cipher = aes.new(secret_key)
        return base64.b64encode(cipher.encrypt(pad_string(raw_cookie_str)))
    else:
        return base64.b64encode(raw_cookie_str)

def setcookie(self, raw_key):
    self.response.headers['Set-Cookie'] = 'auth='+encoded_cookie_str(raw_key)
    self.response.headers['Set-Cookie'] += '; Expires=Wed, 09 Jun 2025 10:18:14 GMT'

def list_twenty_leads_from_offset(self, offset):
    decoded_cookie = decoded_cookie_str(self.request.cookies.get('auth'))
    url = LIST_URL % (decoded_cookie, offset)
    return json.load(urllib2.urlopen(url))

def search_leads(self, param):
    # takes a tuple in the form of (key, value)
    decoded_cookie = decoded_cookie_str(self.request.cookies.get('auth'))
    url = SEARCH_URL % (decoded_cookie, param[0], param[1])
    return json.load(urllib2.urlopen(url))

def is_lead(self, offset):
    decoded_cookie = decoded_cookie_str(self.request.cookies.get('auth'))
    url = LEAD_URL % (decoded_cookie, offset)
    return json.load(urllib2.urlopen(url))

def portal_from_key(self):
    addr = SETTINGS_URL % self.request.get('api_key')
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
    

def unix_to_date(unix_time):
    return datetime.datetime.fromtimestamp(int(unix_time)).strftime('%m/%d/%Y')

def num_pages(self):
    pass

def convert_lead_date(lead):
    if lead["closedAt"]:
        close_time_secs = lead["closedAt"]/1000
        close_time = unix_to_date(close_time_secs)
        lead["closedAt"] = close_time
    return lead

def set_vals_for_search(leads_results, search_term):
    values = {
        'leads': leads_results,
        'search': True,
        'offset': '0',
        'search_term': search_term,
    }
    return values

def parse_csv(csv):
    lines = csv.split('\n')
    headers = lines[0].split(',')
    headers = [term.lower().strip() for term in headers]
    EMAIL_INDEX = headers.index('email')
    DATE_INDEX = headers.index('date')
    leads_to_close = {}
    for line in lines[1:]:
        line_ = line.split(',')
        if len(line_) < 2:
            continue
        date = line_[DATE_INDEX].split('/')
        st = sanetime(int(date[2]), int(date[0]), int(date[1]))
        leads_to_close[line_[EMAIL_INDEX].strip()] = str(st.ms)
    return leads_to_close

def parse_param(search_term):
    if '@' in search_term:
        params = ('email', search_term)
    else:
        params = ('lastName', search_term)
    return params

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
