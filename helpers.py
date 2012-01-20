from django.utils import simplejson as json
import urllib2
import time
import datetime

LIST_URL = 'https://hubapi.com/leads/v1/list/?access_token=%s&excludeConversionEvents=true&max=21&offset=%s&sort=lastName'
SEARCH_URL = 'https://hubapi.com/leads/v1/list/?access_token=%s&excludeConversionEvents=true&max=21&%s=%s'
LEAD_URL = 'https://hubapi.com/leads/v1/list/?access_token=%s&excludeConversionEvents=true&max=1&offset=%s&sort=lastName'
SETTINGS_URL = "https://hubapi.com/settings/v1/settings?access_token=%s"
 

def list_twenty_leads_from_offset(self, offset):
    access_token = self.request.get('hubspot.marketplace.accessToken')
    url = LIST_URL % (access_token, offset)
    return json.load(urllib2.urlopen(url))

def search_leads(self, param):
    # takes a tuple in the form of (key, value)
    access_token = self.request.get('hubspot.marketplace.accessToken')
    url = SEARCH_URL % (access_token, param[0], param[1])
    return json.load(urllib2.urlopen(url))

def is_lead(self, offset):
    access_token = self.request.get('hubspot.marketplace.accessToken')
    url = LEAD_URL % (access_token, offset)
    return json.load(urllib2.urlopen(url))

def offset_from_page(self):
    offset = self.request.get('offset')
    if self.request.get('next'):
        return str(int(offset)+20)
    elif self.request.get('prev'):
        return str(max([int(offset)-20, 0]))
    else:
        return '0'

def format_date(date_string):
    if not date_string:
        return 'Open'
    else:
        big_date = time.ctime(date_string).split()
        return ' '.join([seg for seg in big_date if ':' not in seg])

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
        month = str(date[0])
        if len(month) ==1:
            month = "0"+month
        day = str(date[1])
        if len(day) == 1:
            day = "0"+day
        timeStr = str(date[2]) + " " +month+" "+ day
        firstTime = time.strptime(timeStr, "%Y %m %d")
        st = time.mktime(firstTime)
        #Used so that the close date of leads page as well as json call line up
        #Time in the two places is apparently different in timezones
        day = 60*60*18
        st =str(int(st) + day) + '000'
        leads_to_close[line_[EMAIL_INDEX].strip()] = str(st)
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
