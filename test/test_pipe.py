import pytest

from functools import partial
from jsonpipe.sh import select
from jsonpipe import jsonunpipe, pipe
from jsonpipe import jsonpipe

# Shim for easier demonstration.
def jpipe(obj):
    return ''.join(jsonpipe(obj))

# The simplest case is outputting JSON values (strings, numbers, booleans and
# nulls
def test_simple_cases():
    assert jpipe("Hello, World!") == '/	"Hello, World!"'
    assert jpipe(123) == '/	123'
    assert jpipe(0.25) == '/	0.25'
    assert jpipe(None) == '/	null'
    assert jpipe(True) == '/	true'
    assert jpipe(False) == '/	false'

# jsonpipe always uses '/' to represent the top-level object. Dictionaries
# are displayed as ``{}``, with each key shown as a sub-path:
def test_dictionary():
    assert jpipe({"a": 1, "b": 2}) == '/\t{}/a\t1/b\t2'


# Lists are treated in much the same way, only the integer indices are used
# as the keys, and the top-level list object is shown as ``[]``:
def test_list():
    assert list(jsonpipe([1, "foo", 2, "bar"])) == ['/\t[]', '/0\t1', '/1\t"foo"', '/2\t2', '/3\t"bar"']

def test_select_jsonupipe():
    obj = {'a': 1, 'b': {'c': 3, 'd': 4}}
    l = pipe(jsonpipe, partial(select, path='/b'), jsonunpipe)(obj)
    assert l == {'b': {'c': 3, 'd': 4}}
