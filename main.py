#!/usr/bin/env python

from google.appengine.dist import use_library
use_library('django', '1.2')
import wsgiref.handlers
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from helpers import *
import hapi.leads
import cgi

class Welcome(webapp.RequestHandler):
    def get(self):
        self.response.out.write(template.render('welcome.html', None))
    
    def post(self):
        pass

class Verify(webapp.RequestHandler):
    def get(self):
        pass
    
    def post(self):
        real_portal = portal_from_key(self)
        if real_portal == str(self.request.get("hubspot.marketplace.portal_id")):
            api_key = str(cgi.escape(self.request.get("api_key")))
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
        if self.request.cookies["auth"]:
            api_key = decoded_cookie_str(self.request.cookies["auth"])
            offset = self.request.get('offset') or '0'
            try:
                leads = list_twenty_leads_from_offset(self, offset)
            except:
                # you are probably not connected to the internet. Are you on a plane?
                # I was when I wrote this part!
                leads = demo_leads_response
            try:
                more = leads[20]
            except:
                more = False
            leads = leads[:20]
            page = int(offset)/20 + 1
            for lead in leads:
                lead = convert_lead_date(lead)
            
            values = {
                'leads':leads,
                'offset':offset,
                'are_more':more,
                'page':page,
                #'close_time':close_times,
            }
            self.response.out.write(template.render('list.html', values))
        else:
            self.redirect('/home')
    
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
                lead = convert_lead_date(lead)
            
            values = {
                'leads':leads,
                'offset':offset,
                'are_more':more,
                'page':page,
            }
            self.response.out.write(template.render('list.html', values))
        else:
            self.redirect('/home')

class Num_Pages(webapp.RequestHandler):
    def get(self):
        pass
    
    def post(self):
        pages = 4
        values = {
            'pages':pages,
        }
        self.response.out.write(template.render('pages.html', values))

class Close(webapp.RequestHandler):
    def get(self):
        self.redirect('/')
    
    def post(self):
        # close them leads!
        api_key = decoded_cookie_str(self.request.cookies['auth'])
        client = hapi.leads.LeadsClient(api_key)
        search_term = self.request.get('search')
        leads_to_close = self.request.get_all('guid') #this is a list of guids
        close_time = self.request.get('close_time')
        offset = self.request.get('offset')
        
        for guid in leads_to_close:
            client.close_lead(guid, close_time)

        if search_term:
            params = parse_param(search_term)
            leads_results = search_leads(self, params)
            for lead in leads_results:
                lead = convert_lead_date(lead)
            values = set_vals_for_search(leads_results, search_term)
            self.response.out.write(template.render('list.html', values))
        else:
            self.redirect('/list?offset=%s' % offset)

class CloseCsv(webapp.RequestHandler):
    def get(self):
        self.response.out.write(template.render("csv.html", None))

    def post(self):
        api_key = decoded_cookie_str(self.request.cookies['auth'])
        client = hapi.leads.LeadsClient(api_key)
        csv = self.request.get('csv') #this should be a csv with headers like EMAIL and DATE
        leads_to_close = parse_csv(csv)
        for email, time in leads_to_close.items():
            try:
                lead_guid = search_leads(self, ('email', email))[0]['guid']
            except:
                continue
            client.close_lead(lead_guid, time)
            self.response.out.write("closed %s [guid %s] at %s" % (email, lead_guid, time))
        self.response.out.write('done')

class Search(webapp.RequestHandler):
    def get(self):
        self.redirect('#')

    def post(self):
        search_term = self.request.get('search_term')
        offset  = self.request.get('offset') or '0'
        # determine if the search term is an email address
        params = parse_param(search_term)
        leads_results = search_leads(self, params)
        
        for lead in leads_results:
            lead = convert_lead_date(lead)
        values = set_vals_for_search(leads_results, search_term)
        self.response.out.write(template.render('list.html', values)) 

def main():
    app = webapp.WSGIApplication([
        (r'/', Welcome),
        (r'/home', Verify),
        (r'/a', Reload),
        (r'/list', List),
        (r'/close', Close),
        (r'/search', Search),
        (r'/csv', CloseCsv)
        ], debug=True)
    wsgiref.handlers.CGIHandler().run(app)

if __name__ == '__main__':
    main()

