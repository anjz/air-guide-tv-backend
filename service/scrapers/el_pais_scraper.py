import json
import urllib2
from urllib2 import HTTPError

import arrow
from model.show_model import ShowModel


class ElPaisScraper:
    __BASE_URL = 'https://programacion-tv.elpais.com/data/'
    __FILE_NAME_FORMAT = 'parrilla_{}{}{}.json'
    __DESCRIPTIONS_FILE_NAME_FORMAT = 'programas/{}.json'

    TIME_ZONE = 'Europe/Madrid'

    def get_shows_for_date(self, date, parent=None):
        """
        A list of tv shows in the given date.

        :param Arrow date: Arrow object for the desired date.
        :return: A list of show models.
        :rtype: list[ShowModel]
        """
        two_digits_day = '{:02d}'.format(date.day)
        two_digits_month = '{:02d}'.format(date.month)
        four_digits_year = date.year

        shows_file_name = self.__FILE_NAME_FORMAT.format(two_digits_day, two_digits_month, four_digits_year)
        shows_file_url = self.__BASE_URL + shows_file_name

        try:
            shows_response = urllib2.urlopen(shows_file_url).read()
        except HTTPError as e:
            import logging
            logging.error('Couldn\'t retrieve shows info from: ' + shows_file_url)
            logging.error('Error code: ', e.code)
            return
        except urllib2.URLError as e:
            import logging
            logging.error('Failed reaching server: ' + shows_file_url)
            logging.error('Reason: ' + e.reason)
            return
        else:
            show_list = []
            channels_list = json.loads(shows_response, 'utf-8')

            for channel in channels_list:
                for show in channel['programas']:
                    show_model = ShowModel(parent=parent)
                    show_model.timezone = self.TIME_ZONE
                    show_model.channel_id = channel['idCanal']
                    # Dates in the json document are Madrid dates.
                    # After replacing timezone by Europe/Madrid the date is converted to UTC.
                    # naive property returns a Python datetime.datetime object without tzinfo (ideal for ndb lib)
                    start_time = arrow.get(show['iniDate']).replace(tzinfo='Europe/Madrid').to('utc').naive
                    end_time = arrow.get(show['endDate']).replace(tzinfo='Europe/Madrid').to('utc').naive

                    show_model.show_id = show['id_programa']
                    show_model.start_time = start_time
                    show_model.end_time = end_time
                    show_model.show_name = show['title']
                    show_model.show_description = show['description']

                    show_list.append(show_model)

            return show_list
