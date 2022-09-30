from django.db.models import QuerySet
from django.db.models.constants import LOOKUP_SEP


class Accessor(str):
    """
    A string describing a path from one object to another via attribute/index accesses.
    For convenience, the class has an alias `.A` to allow for more concise code.

    Relations are separated by "__" characters (LOOKUP_SEP).
    """

    def _resolve(self, context, default, quiet=True):
        """
        Return an object described by the accessor by traversing the attributes
        of context.

        """
        try:
            obj = context
            for level in self.levels:
                if level == "iexact":
                    obj = obj.lower()
                elif isinstance(obj, dict):
                    obj = obj[level]
                elif isinstance(obj, (list, tuple, QuerySet)):
                    obj = obj[int(level)]
                elif callable(getattr(obj, level)):
                    try:
                        obj = getattr(obj, level)()
                    except (KeyError, TypeError):
                        obj = getattr(obj, level)
                else:
                    obj = getattr(obj, level)

                if not obj:
                    break
            return obj
        except Exception as e:
            if quiet:
                return default
            else:
                raise e

    def resolve_with_default(self, context, default, quiet=True):
        return self._resolve(context, default=default, quiet=quiet)

    def resolve(self, context, quiet=True):
        return self.resolve_with_default(context, "", quiet=quiet)

    def resolve_with_none(self, context, quiet=True):
        return self.resolve_with_default(context, None, quiet=quiet)

    @property
    def levels(self):
        if self in ["", "self"]:
            return ()
        return self.split(LOOKUP_SEP)


A = Accessor
