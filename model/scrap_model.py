from google.appengine.ext import ndb


class ScrapModel(ndb.Model):
    """
    Class with information about a specific scrap session.
    Entities using this model are used as parent entities of the ones containing show information.
    """
    scrap_date_time = ndb.DateTimeProperty(name='sdt')
    amount_dates_to_scrap = ndb.IntegerProperty(name='adts')
    amount_dates_scraped = ndb.IntegerProperty(name='ads')

    def is_scrap_complete(self):
        """
        Checks if the scraped information for the intended dates has finished.
        Information contained in child entities should be used only if the scrap has been completed.

        :return: Whether all the dates intended to be scraped are already scraped or not.
        :rtype: bool
        """
        return self.amount_dates_scraped == self.amount_dates_to_scrap

    @classmethod
    def generate_id_for_new_model(cls, date=None):
        """
        Generate an entity id based on date.

        :param datetime.datetime|Arrow|None date: A date used to generate an id. UTC now used if date not supplied.
        :return: A string that can be used as id for an entity based on this model
        """
        if date is None:
            import arrow
            date = arrow.utcnow()

        return '{}-{}-{}'.format(date.day, date.month, date.year)
