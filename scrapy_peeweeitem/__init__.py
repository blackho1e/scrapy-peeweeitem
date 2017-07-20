# -*- coding: utf-8 -*-

from scrapy.item import Field, Item, ItemMeta
from six import with_metaclass


class PeeweeItemMeta(ItemMeta):

    def __new__(mcs, class_name, bases, attrs):
        cls = super(PeeweeItemMeta, mcs).__new__(mcs, class_name, bases, attrs)
        cls.fields = cls.fields.copy()
        cls._models = []

        for model in cls.db_models:
            primary_keys = self._get_primary_keys(model)
            lookup =
            item = {
                'database': model._meta.database,
                'model': model,
                'primary_keys': primary_keys,
            }
            fields = []
            for field in model._meta.fields:
                fields.append(field)
                if field not in cls.fields:
                    cls.fields[field] = TextField()
            item['fields'] = fields
            cls._models.append(item)
        return cls

    def _get_primary_keys(self, model):
        pk = model._meta.primary_key
        if "field_names" in pk.__dict__:
            names = pk.field_names
        else:
            names = (pk.name,)
        return names

class PeeweeItem(with_metaclass(PeeweeItemMeta, Item)):

    db_models = []

    def __init__(self, *args, **kwargs):
        super(PeeweeItem, self).__init__(*args, **kwargs)
        self._instance = None
        for k, v in self.fields.iteritems():
            if v:
                self[k] = v.get('default', None)

    def instance(self, model):
        if self._instance is None:
            primary_keys = model['primary_keys']
            fields = model['fields']

            lookup = {}
            for key in primary_keys:
                lookup[key] = item[key]

            # modelargs = dict((k, self.get(k)) for k in self._values if k in fields)
            # db_model = model['model']
            # self._instance = db_model.create(**modelargs)
            _instance, created = cls.get_or_create(**lookup)
            for key, value in item.iteritems():
                setattr(_instance, key, value)
        return self._instance

    def save(self):
        for model in self._models:
            self.instance(model).save()
