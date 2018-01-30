import logging
from google.appengine.ext import ndb

from model.scrap_model import ScrapModel
from model.show_model import ShowModel


class ScrapingService:
    __MAX_BATCH_SIZE = 500

    def __init__(self, scraper):
        self.__scraper = scraper

    def scrap_and_store_shows_for_dates(self, *args):
        scrap_entity_id = ScrapModel.generate_id_for_new_entity(self.__scraper.TIME_ZONE)
        scrap_entity = ScrapModel.get_by_id(scrap_entity_id)

        if scrap_entity is not None:
            # Scraping data for today already exists. Delete it.
            logging.info('Deleting existing scrap info for today')
            delete_keys = ShowModel.query(ancestor=scrap_entity.key).fetch(keys_only=True)
            delete_keys.append(scrap_entity.key)

            for entity_index in range(0, len(delete_keys), self.__MAX_BATCH_SIZE):
                delete_batch = delete_keys[entity_index:min(entity_index + self.__MAX_BATCH_SIZE, len(delete_keys))]
                ndb.delete_multi(delete_batch)

        import arrow
        scrap_entity = ScrapModel(
            id=scrap_entity_id,
            timezone=self.__scraper.TIME_ZONE,
            scrap_date_time=arrow.utcnow().naive,
            amount_dates_to_scrap=len(args),
            amount_dates_scraped=0
        )

        scrap_entity_key = scrap_entity.put()

        for date in args:
            logging.info('Deferring scraping. Date: {}. Timezone: {}'.format(date.humanize(), self.__scraper.TIME_ZONE))
            from google.appengine.ext.deferred import deferred
            deferred.defer(self._scrap_and_store_shows, date.naive, scrap_entity_key)

    def _scrap_and_store_shows(self, date, scrap_info_entity_key):
        shows = self.__scraper.get_shows_for_date(date, parent=scrap_info_entity_key)

        for show_index in range(0, len(shows), self.__MAX_BATCH_SIZE):
            shows_to_persist = shows[show_index:min(show_index + self.__MAX_BATCH_SIZE, len(shows))]
            ndb.put_multi(shows_to_persist, use_cache=False)

        # todo update scrap_info_entity in a transaction. Increment the amount_dates_scrapped

        # todo if this is the last date to be scrapped, defer a task for deleting show entities that are child of scraping
        # info model older than 3 days
