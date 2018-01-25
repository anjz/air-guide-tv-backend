import json
import urllib2
from urllib2 import HTTPError

import arrow
from model.show_model import ShowModel


class ElPaisScraper:
    __BASE_URL = 'https://programacion-tv.elpais.com/data/'
    __FILE_NAME_FORMAT = 'parrilla_{}{}{}.json'
    __DESCRIPTIONS_FILE_NAME_FORMAT = 'programas/{}.json'
    __COUNTRY = 'es'

    def get_shows_for_date(self, date):
        """
        A generator function for retrieving all the information about the tv shows in the given date.
        :param Arrow date: Arrow object for the desired date.
        :return: A generator function for iterating through show models.
        :rtype: Generator[ShowModel]
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
        except urllib2.URLError as e:
            import logging
            logging.error('Failed reaching server: ' + shows_file_url)
            logging.error('Reason: ' + e.reason)
        else:
            channels_list = json.loads(shows_response, 'utf-8')

            for channel in channels_list:
                show_model = ShowModel(
                    country_code=self.__COUNTRY,
                    channel_id=channel['idCanal']
                )
                for show in channel['programas']:
                    # Dates in the json document are Madrid dates
                    start_time = arrow.get(show['iniDate']).replace(tzinfo='Europe/Madrid')
                    end_time = arrow.get(show['endDate']).replace(tzinfo='Europe/Madrid')

                    show_model.show_id = show['id_programa']
                    show_model.start_time = start_time.datetime
                    show_model.end_time = end_time.datetime
                    show_model.show_name = show['title']
                    show_model.show_info = show['description']

                    yield show_model
