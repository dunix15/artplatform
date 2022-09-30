from itertools import count, groupby
from typing import Iterable


DEFAULT_CHUNK_SIZE = 5_000


class iterlist(list):
    # based on https://www.mysociety.org/2015/06/01/django-streaminghttpresponse-json-html/

    def __init__(self, gen, count=None):
        self.ITERABLE = gen

        super().__init__(([1] * count) if count is not None else ["HACK"])

    def __iter__(self):
        return self.ITERABLE


def split_every(n: int, iterable: Iterable):
    """Generator that splits `iterable` every `n`th item"""
    c = count()

    for _, g in groupby(iterable, lambda _: next(c) // n):
        yield g


def chunked_qs(qs, chunk_size=DEFAULT_CHUNK_SIZE):
    return split_every(chunk_size, qs.iterator(chunk_size))
