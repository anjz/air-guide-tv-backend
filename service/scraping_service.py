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
            self._delete_scrap_info(scrap_entity.key)

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
        logging.info('Scraping date: {}'.format(date.isoformat()))
        shows = self.__scraper.get_shows_for_date(date, parent=scrap_info_entity_key)

        for batch in self._get_list_in_batches(shows, self.__MAX_BATCH_SIZE):
            ndb.put_multi(batch, use_cache=False)

        self._increment_amount_dates_scraped(scrap_info_entity_key)

    def _get_list_in_batches(self, full_list, batch_size):
        for item_index in range(0, len(full_list), batch_size):
            yield full_list[item_index:min(item_index + batch_size, len(full_list))]

    def _delete_scrap_info(self, scrap_parent_entity_key):
        logging.info('Deleting old shows information')
        delete_keys = ShowModel.query(ancestor=scrap_parent_entity_key).fetch(keys_only=True)
        delete_keys.append(scrap_parent_entity_key)

        for batch in self._get_list_in_batches(delete_keys, self.__MAX_BATCH_SIZE):
            ndb.delete_multi(batch)

    @ndb.transactional()
    def _increment_amount_dates_scraped(self, scrap_info_entity_key):
        scrap_info_entity = scrap_info_entity_key.get()
        scrap_info_entity.amount_dates_scraped += 1
        scrap_info_entity.put()

        if scrap_info_entity.amount_dates_scraped == scrap_info_entity.amount_dates_to_scrap:
            logging.info('Scraping Complete')
            from google.appengine.ext.deferred import deferred
            deferred.defer(self._cleanup_old_shows_info, scrap_info_entity.scrap_date_time)

    def _cleanup_old_shows_info(self, latest_datetime):
        logging.info('Cleaning show info scrapped before than: {}'.format(latest_datetime))
        old_scrap_info_entities = ScrapModel.query(ScrapModel.scrap_date_time < latest_datetime).fetch()

        for old_entity in old_scrap_info_entities:
            from google.appengine.ext.deferred import deferred
            deferred.defer(self._delete_scrap_info, old_entity.key)
