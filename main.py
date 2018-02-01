import os
import webapp2
from google.appengine.ext import vendor

from handler.shows import OnAirHandler
from handler.cron_scrap import CronScrapHandler

vendor.add(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib'))
debug = os.environ.get('SERVER_SOFTWARE', '').startswith('Dev')

app = webapp2.WSGIApplication([
    webapp2.Route('/<country_code:[aA-zZ]{2,3}>', handler=OnAirHandler, methods='GET'),
    webapp2.Route('/cron/scrap/elpais', handler=CronScrapHandler, handler_method='scrap_el_pais', methods='GET')
], debug=debug)
