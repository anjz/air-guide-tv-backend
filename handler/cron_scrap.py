import logging

import webapp2

from service.scraping_service import ScrapingService


class CronScrapHandler(webapp2.RequestHandler):
    def get(self):
        pass

    def scrap_el_pais(self):
        """
        Scraps El Pais for today, tomorrow and after_tomorrow.
        """
        from service.scrapers.el_pais_scraper import ElPaisScraper
        el_pais_scraper = ElPaisScraper()
        scraping_service = ScrapingService(el_pais_scraper)

        import arrow
        today = arrow.now(ElPaisScraper.TIME_ZONE)
        tomorrow = today.shift(days=1)
        after_tomorrow = tomorrow.shift(days=1)

        logging.info('El Pais tv shows information scraping started')
        scraping_service.scrap_and_store_shows_for_dates(today, tomorrow, after_tomorrow)

        self.response.status = 204
