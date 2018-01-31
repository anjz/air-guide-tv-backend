from google.appengine.api import memcache
from google.appengine.ext import ndb

from model.scrap_model import ScrapModel
from model.show_model import ShowModel


class ShowsService:
    @classmethod
    def retrieve_on_air_shows_for_country(cls, timezone):
        import arrow
        now_datetime = arrow.now(timezone).naive

        on_air_memcache_key = cls._get_on_air_memcache_key(timezone, now_datetime)
        cached_on_air_shows = memcache.get(on_air_memcache_key)
        if cached_on_air_shows:
            return cached_on_air_shows

        scrap_entity = cls._get_most_recent_scrap_entity(timezone)

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
        current_shows = ndb.get_multi(current_shows_keys)

        current_shows_dict = [show.to_dict() for show in current_shows]
        memcache.set(on_air_memcache_key, current_shows_dict, time=60)

        return current_shows_dict

    @classmethod
    def _get_most_recent_scrap_entity(cls, timezone):
        # Check if there is scrapping information from today.
        scrap_entity = ScrapModel.get_by_id(ScrapModel.generate_id_for_new_entity(timezone))
        if scrap_entity and scrap_entity.is_scrap_complete():
            return scrap_entity

        # No luck. Try to get yesterday's scrap model
        import arrow
        yesterday_date = arrow.utcnow().shift(days=-1)
        scrap_entity = ScrapModel.get_by_id(ScrapModel.generate_id_for_new_entity(timezone, yesterday_date))

        if scrap_entity and scrap_entity.is_scrap_complete():
            return scrap_entity

        # No luck. Try to get before yesterday's scrap model
        before_yesterday_date = yesterday_date.shift(days=-1)
        scrap_entity = ScrapModel.get_by_id(ScrapModel.generate_id_for_new_entity(timezone, before_yesterday_date))

        if scrap_entity and scrap_entity.is_scrap_complete():
            return scrap_entity

        # todo replace generic exception by a custom exception
        raise Exception

    @classmethod
    def _get_on_air_memcache_key(cls, timezone, now_datetime):
        memcache_key = '{}-{}-{}-{}-{}-{}'.format(
            timezone,
            now_datetime.year,
            now_datetime.month,
            now_datetime.day,
            now_datetime.hour,
            now_datetime.minute
        )

        return memcache_key
