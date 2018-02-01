import json

from handler.base.public_handler import PublicHandler
from service.helper_service import HelperService
from service.shows_service import ShowsService


class OnAirHandler(PublicHandler):
    def get(self, country_code):
        timezone = HelperService.get_shows_info_tz_for_country(country_code)
        shows = ShowsService.retrieve_on_air_shows_for_country(timezone)

        # todo format response correctly
        self.response.write(json.dumps([show['show_name'] for show in shows]))
