#!/usr/bin/env python

import wsgiref.handlers
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from helpers import *

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
            values = {
                'leads':leads,
                'offset':offset,
                'are_more':more,
                'page':page,
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
            values = {
                'leads':leads,
                'offset':offset,
                'are_more':more,
                'page':page,
            }
            self.response.out.write(template.render('list2.html', values))
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
        # Close Leads
        # On Success redirect to success
        # On Failure redirect to failure
        leads_to_close = self.request.get('guid')
        if type(leads_to_close)==type([]):
            for lead in leads_to_close:
                close(self, lead)
        else:
            close(self, leads_to_close)
        values = {
            'params':None,
            'offset':self.request.get('offset')
        }
        self.response.out.write(template.render('list2.html', values))

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