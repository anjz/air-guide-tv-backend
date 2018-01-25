import os
import webapp2
from google.appengine.ext import vendor

from handler.on_air import OnAirHandler

vendor.add(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib'))
debug = os.environ.get('SERVER_SOFTWARE', '').startswith('Dev')

app = webapp2.WSGIApplication([
    webapp2.Route('<country_code:[aA-zZ]{2,3}>', handler=OnAirHandler, methods='POST')
], debug=debug)
