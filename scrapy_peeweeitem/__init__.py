# -*- coding: utf-8 -*-

from peewee import CompositeKey
from scrapy.item import Field, Item, ItemMeta
from six import with_metaclass


class PeeweeItemMeta(ItemMeta):

    def __new__(mcs, class_name, bases, attrs):
        cls = super(PeeweeItemMeta, mcs).__new__(mcs, class_name, bases, attrs)
        cls.fields = cls.fields.copy()
        cls._models = []
        for model in cls.db_models:
            item = dict(db_model=model)
            fields = []
            for field in model._meta.fields:
                fields.append(field)
                if field not in cls.fields:
                    cls.fields[field] = Field()
            item['fields'] = fields
            item['primary_keys'] = mcs._get_primary_keys(mcs, model)
            cls._models.append(item)
        return cls

    def _get_primary_keys(self, model):
        meta = model._meta
        pk = meta.primary_key
        return pk.field_names if isinstance(pk, CompositeKey) else [f.name for f in meta.sorted_fields if f.primary_key]

class PeeweeItem(with_metaclass(PeeweeItemMeta, Item)):

    db_models = []

    def __init__(self, *args, **kwargs):
        super(PeeweeItem, self).__init__(*args, **kwargs)
        self._instance = {}

    def instance(self, model):
        db_model = model['db_model']
        if self._instance.get(db_model._meta.name) is None:
            fields = model['fields']
            primary_keys = model['primary_keys']
            args = dict((k, self.get(k, None)) for k in self._values if k in primary_keys and self.get(k))
            values = dict((k, self.get(k, None)) for k in self._values if k in fields and self.get(k))
            if args:
                instance = db_model.get_or_create(**args)[0]
                for k, v in values.items():
                    setattr(instance, k, v)
            else:
                instance = db_model.create(**values)
            self._instance[db_model._meta.name] = instance
            return instance
        return None

    def save(self, excludes=[]):
        for model in self._models:
            db_model = model['db_model']
            if db_model not in excludes:
                self.instance(model).save()

