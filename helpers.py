from django.utils import simplejson as json
import urllib2
import base64
import time
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
    pass

def num_pages(self):
    pass


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
