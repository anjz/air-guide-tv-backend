from google.appengine.ext import ndb

from model.scrap_model import ScrapModel
from model.show_model import ShowModel


class ShowsService:
    @classmethod
    def retrieve_on_air_shows_for_country(cls, timezone):
        scrap_entity = cls._get_most_recent_scrap_entity(timezone)
        import arrow
        now_datetime = arrow.now(timezone).naive

        # Due to DataStore query limitations (inequality filters for more than 1 property are not allowed) two key_only
        # queries are required. The intersection of the 2 result sets contains the desired info.
        past_or_current_shows = ShowModel.query(
            ShowModel.start_time <= now_datetime,
            ancestor=scrap_entity.key
        ).fetch(keys_only=True)

        future_or_current_shows = ShowModel.query(
            ShowModel.end_time >= now_datetime,
            ancestor=scrap_entity.key
        ).fetch(keys_only=True)

        current_shows_keys = set(past_or_current_shows) & set(future_or_current_shows)

        return ndb.get_multi(current_shows_keys)

    @classmethod
    def _get_most_recent_scrap_entity(cls, timezone):
        # Check if there is scrapping information from today.
        scrap_entity = ScrapModel.get_by_id(ScrapModel.generate_id_for_new_entity(timezone))
        if scrap_entity:
            return scrap_entity

        # No luck. Try to get yesterday's scrap model
        import arrow
        yesterday_date = arrow.utcnow().shift(days=-1)
        scrap_entity = ScrapModel.get_by_id(ScrapModel.generate_id_for_new_entity(timezone, yesterday_date))

        if scrap_entity:
            return scrap_entity

        # No luck. Try to get before yesterday's scrap model
        before_yesterday_date = yesterday_date.shift(days=-1)
        scrap_entity = ScrapModel.get_by_id(ScrapModel.generate_id_for_new_entity(timezone, before_yesterday_date))

        if scrap_entity:
            return scrap_entity

        # todo replace generic exception by a custom exception
        raise Exception
