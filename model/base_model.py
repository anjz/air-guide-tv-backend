from google.appengine.ext import ndb
from google.appengine.ext.ndb.key import Key


class BaseModel(ndb.Model):
    def to_dict(self):
        output = {}
        for key, prop in self._properties.iteritems():
            key_code_name = prop._code_name
            value = BaseModel._coerce(getattr(self, key_code_name))
            if value is not None:
                output[key_code_name] = value

        return output

    @staticmethod
    def _coerce(value):
        simple_types = (int, long, float, bool, basestring)

        import datetime
        if value is None or isinstance(value, simple_types):
            return value
        elif isinstance(value, datetime.date):
            return value.isoformat()
        elif hasattr(value, 'to_dict'):
            return value.to_dict()
        elif isinstance(value, dict):
            return dict((BaseModel._coerce(k), BaseModel._coerce(v)) for k, v in value.items())
        elif hasattr(value, '__iter__'):
            return map(BaseModel._coerce, value)
        elif isinstance(value, Key):
            return value.id()
        else:
            raise ValueError('cannot encode %r' % value)