from google.appengine.ext import ndb

from model.scrap_model import ScrapModel


class ScrapingService:
    __MAX_STORE_BATCH_SIZE = 500

    def __init__(self, scraper):
        self.__scraper = scraper

    def scrap_and_store_shows_for_dates(self, *args):
        scrap_entity_id = ScrapModel.generate_id_for_new_entity()
        scrap_entity = ScrapModel.get_by_id(scrap_entity_id)

        if scrap_entity is not None:
            # Scraping data for today already exists. Delete it.
            # todo delete entity and all its childs.
            pass

        import arrow
        scrap_entity = ScrapModel(
            id=scrap_entity_id,
            scrap_date_time=arrow.utcnow().naive,
            amount_dates_to_scrap=len(args),
            amount_dates_scraped=0
        )

        scrap_entity_key = scrap_entity.put()

        for date in args:
            self._scrap_and_store_shows(date, scrap_entity_key)

    def _scrap_and_store_shows(self, date, scrap_info_entity_key):
        shows_to_persist = []
        current_batch_size = 0
        for show in self.__scraper.get_shows_for_date(date):
            if current_batch_size < self.__MAX_STORE_BATCH_SIZE:
                show.parent = scrap_info_entity_key
                shows_to_persist.append(show)
                current_batch_size += 1
            else:
                # Store current batch
                ndb.put_multi(shows_to_persist)
                shows_to_persist = []
                current_batch_size = 0
