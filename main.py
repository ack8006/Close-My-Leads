#!/usr/bin/env python

import wsgiref.handlers
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
import datetime
from helpers import *
import hapi.leads

class Welcome(webapp.RequestHandler):
    def get(self):
        self.response.out.write(template.render('welcome.html', None))
    
    def post(self):
        real_portal = portal_from_key(self)
        if real_portal == str(self.request.get('portalId')):
            api_key = str(self.request.get('api_key'))
            setcookie(self, api_key)
            self.redirect('/list')
        else:
            self.redirect('/a')

class Reload(webapp.RequestHandler):
    def get(self):
        self.response.out.write(template.render('welcome2.html', None))
    
    def post(self):
        pass

class List(webapp.RequestHandler):
    def get(self):
        if self.request.cookies['auth']:
            api_key = decoded_cookie_str(self.request.cookies['auth'])
            offset = '0'
            try:
                leads = list_twenty_leads_from_offset(self, offset)
            except:
                leads = demo_leads_response
            try:
                more = leads[20]
            except:
                more = False
            leads = leads[:20]
            page = int(offset)/20 + 1
            for lead in leads:
                close_time_secs = lead["closedAt"]/1000
                close_time = datetime.datetime.fromtimestamp(int(close_time_secs)).strftime('%m/%d/%Y')
                lead["closedAt"] = close_time
            values = {
                'leads':leads,
                'offset':offset,
                'are_more':more,
                'page':page,
                #'close_time':close_times,
            }
            self.response.out.write(template.render('list.html', values))
        else:
            self.redirect('/')
    
    def post(self):
        if self.request.cookies['auth']:
            offset = offset_from_page(self)
            leads = list_twenty_leads_from_offset(self, offset)
            try:
                more = leads[20]
            except:
                more = False
            leads = leads[:20]
            page = int(offset)/20 + 1
            for lead in leads:
                close_time_secs = lead["closedAt"]/1000
                close_time = datetime.datetime.fromtimestamp(int(close_time_secs)).strftime('%m/%d/%Y')
                lead["closedAt"] = close_time
            values = {
                'leads':leads,
                'offset':offset,
                'are_more':more,
                'page':page,
            }
            self.response.out.write(template.render('list.html', values))
        else:
            self.redirect('/')

class Num_Pages(webapp.RequestHandler):
    def get(self):
        pass
    
    def post(self):
        offset = 0
        while True:
            offset += 20
            if not is_lead(self, offset):
                break
        page = list(range(offset/20 + 1))
        values = {
            'pages':page,
        }
        self.response.out.write(template.render('pages.html', values))

class Close(webapp.RequestHandler):
    def get(self):
        self.redirect('/')
    
    def post(self):
        # close them leads!
        # Get lead time from parameter
        api_key = decoded_cookie_str(self.request.cookies['auth'])
        client = hapi.leads.LeadsClient(api_key)
        leads_to_close = self.request.get_all('guid')
        print leads_to_close
        close_time = self.request.get('close_time')
        print close_time
        for lead in leads_to_close:
            client.close_lead(lead, close_time)
        values = {
            'params':None,
            'offset':self.request.get('offset')
        }
        self.response.out.write('Closed %s: %s' % (leads_to_close, api_key))

def main():
    app = webapp.WSGIApplication([
        (r'/', Welcome),
        (r'/a', Reload),
        (r'/list', List),
        (r'/close', Close)
        ], debug=True)
    wsgiref.handlers.CGIHandler().run(app)

if __name__ == '__main__':
    main()
