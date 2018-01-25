from google.appengine.ext import ndb


class ScrapingService:
    __MAX_STORE_BATCH_SIZE = 500

    def __init__(self, scraper):
        self.__scraper = scraper

    def scrap_and_store_shows_for_dates(self, *args):
        for date in args:
            self._scrap_and_store_shows(date)

    def _scrap_and_store_shows(self, date):
        shows_to_persist = []
        current_batch_size = 0
        for show in self.__scraper.get_shows_for_date(date):
            if current_batch_size < self.__MAX_STORE_BATCH_SIZE:
                shows_to_persist.append(show)
                current_batch_size += 1

            # Store current batch
            ndb.put_multi(shows_to_persist)
            shows_to_persist = []
            current_batch_size = 0
