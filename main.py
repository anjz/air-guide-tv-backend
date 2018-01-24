import os
import webapp2

from handlers.on_air import OnAirHandler

debug = os.environ.get('SERVER_SOFTWARE', '').startswith('Dev')

app = webapp2.WSGIApplication([
    webapp2.Route('<country_code:[aA-zZ]{2,3}>', handler=OnAirHandler, methods='POST')
], debug=debug)
