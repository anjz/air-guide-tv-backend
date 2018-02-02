from google.appengine.ext import ndb

from model.base_model import BaseModel


class ShowModel(BaseModel):
    """
    Ndb model holding tv show information
    """
    scrap_info_key = ndb.KeyProperty(name='sk')
    timezone = ndb.StringProperty(name='tz')
    channel_id = ndb.StringProperty(name='ci')
    show_id = ndb.StringProperty(name='sid')
    start_time = ndb.DateTimeProperty(name='st')
    end_time = ndb.DateTimeProperty(name='et')
    show_name = ndb.StringProperty(name='sn', indexed=False)
    show_description = ndb.StringProperty(name='de', indexed=False)
