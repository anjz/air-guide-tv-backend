import json

from handler.base.public_handler import PublicHandler
from service.shows_service import ShowsService


class OnAirHandler(PublicHandler):
    def get(self, country_code):
        # todo change this and use a helper class for getting timezone associated with scraped shows
        if country_code == 'es':
            shows = ShowsService.retrieve_on_air_shows_for_country('Europe/Madrid')

            # todo format response correctly
            self.response.write(json.dumps([show.show_name for show in shows]))
