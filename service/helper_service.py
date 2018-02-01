class HelperService:
    @staticmethod
    def get_shows_info_tz_for_country(country):
        if country == 'es':
            return 'Europe/Madrid'

        # todo use custom execption
        raise Exception
