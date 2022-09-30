import inspect
from uuid import UUID
from collections import defaultdict
from datetime import date, datetime

from django.db.models import Model, QuerySet
from django.db.models.constants import LOOKUP_SEP
from django.db.models.query import FlatValuesListIterable, ModelIterable

from .utils import A, chunked_qs, DEFAULT_CHUNK_SIZE


class BaseQuerySet(QuerySet):
    @staticmethod
    def _prepare_arg(arg):
        if (
            isinstance(arg, (Model, int, str, bool, datetime, date, UUID))
            or arg is None
            or inspect.isclass(arg)
        ):
            arg = [arg]
        elif isinstance(arg, QuerySet):
            assert issubclass(
                arg._iterable_class, (ModelIterable, FlatValuesListIterable)
            ), "Wrong _iterable_class for queryset in filter."
        elif not isinstance(arg, (list, set)):
            arg = list(arg)

        return arg

    @staticmethod
    def _prepare_id_filter_arg(arg):
        arg = BaseQuerySet._prepare_arg(arg)

        if isinstance(arg, BaseQuerySet):
            if not issubclass(arg._iterable_class, FlatValuesListIterable):
                arg = arg.ids()
        else:
            arg = [getattr(item, "pk", item) for item in arg]

        return arg

    def field_filter(self, path, arg):
        return self.filter(**{f"{path}__in": self._prepare_arg(arg)})

    def id_field_filter(self, path, arg):
        return self.filter(**{f"{path}__in": self._prepare_id_filter_arg(arg)})

    def field_exclude(self, path, arg):
        return self.exclude(**{f"{path}__in": self._prepare_arg(arg)})

    def id_field_exclude(self, path, arg):
        return self.exclude(**{f"{path}__in": self._prepare_id_filter_arg(arg)})

    def id(self, arg):
        """
        Filter queryset by id field

        :param Any arg: any type of argument, i.e. Model, int, list etc
        """
        return self.id_field_filter("id", arg)

    def id_not(self, arg):
        """
        Exclude queryset by id field

        :param Any arg: any type of argument, i.e. Model, int, list etc
        """
        return self.id_field_exclude("id", arg)

    def ids(self, *fields, force_eval=False):
        """
        Returns values list of queryset .

        :param fields: path to value
        :param bool force_eval: if true queryset evaluation is forced
        """
        fields = fields or ["id"]

        if force_eval or (
            self._result_cache is not None
            and not any(LOOKUP_SEP in field for field in fields)
        ):
            a_fields = [A(field) for field in fields]
            if len(fields) == 1:
                a_field = a_fields[0]
                return [
                    a_field.resolve_with_none(obj, quiet=False) for obj in iter(self)
                ]
            else:
                return [
                    tuple(
                        a_field.resolve_with_none(obj, quiet=False)
                        for a_field in a_fields
                    )
                    for obj in iter(self)
                ]

        if len(fields) == 1:
            return self.values_list(*fields, flat=True)
        else:
            return self.values_list(*fields)

    def to_dict(self, *fields):
        """
        Converts queryset into dictionary, where `fields` are key and object is value.

        :param fields: path to value which should be key
        """
        return dict(zip(self.ids(*fields, force_eval=True), self))

    def to_nonunique_dict(self, *fields):
        """
        Converts queryset into nonunique dictionary, where `fields` are key and objects matched to key are value.

        :param fields: path to value which should be key
        """
        res = defaultdict(list)
        for key, obj in zip(self.ids(*fields, force_eval=True), self):
            res[key].append(obj)

        return res

    def to_chunks(self, chunk_size=DEFAULT_CHUNK_SIZE):
        return chunked_qs(self, chunk_size)
