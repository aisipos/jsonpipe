from functools import partial
import re
import json

import jsonpipe as jp


__all__ = ['jsonpipe', 'jsonunpipe', 'select', 'search_attr']


jsonpipe = jp.jsonpipe
compose = jp.compose


def select(stdin, path, pathsep='/'):

    r"""
    Select only lines beginning with the given path.

    This effectively selects a single JSON object and all its sub-objects.

        >>> obj = {'a': 1, 'b': {'c': 3, 'd': 4}}
        >>> list(jsonpipe(obj))
        ['/\t{}',
        '/a\t1',
        '/b\t{}',
        '/b/c\t3',
        '/b/d\t4']
        >>> list(compose(jsonpipe, partial(select, '/b'))(obj))
        ['/b\t{}',
        '/b/c\t3',
        '/b/d\t4']
        >>> list(compose(jsonpipe(obj), partial(select, '/b')), jsonunpipe()))
        [{'b': {'c': 3, 'd': 4}}]
    """

    path = re.sub(r'%s$' % re.escape(pathsep), r'', path)
    reg = re.compile(rf'^{re.escape(path)}[\t{re.escape(pathsep)}]')
    return (line for line in stdin if reg.match(line))

def search_attr(stdin, attr, value, pathsep='/'):

    r"""
    Search stdin for an exact attr/value pair.

    Yields paths to objects for which the given pair matches. Example:

        >>> obj = {'a': 1, 'b': {'a': 2, 'c': {'a': "Hello"}}}
        >>> list(compose(jsonpipe, partial(search_attr, attr='a', value=1))(obj))
        ['/']
        >>> list(compose(jsonpipe, partial(search_attr, attr='a', value=2))(obj))
        ['/b']
        >>> list(compose(jsonpipe, partial(search_attr, attr='a', value="Hello"))(obj))
        ['/b/c']

    Multiple matches will result in multiple paths being yielded:

        >>> obj = {'a': 1, 'b': {'a': 1, 'c': {'a': 1}}}
        >>> list(compose(jsonpipe, partial(search_attr, attr='a', value=1))(obj))
        ['/', '/b', '/b/c']
    """

    # '...path/attribute\tvalue' => 'path'.
    reg = re.compile(
        rf'^(.*){re.escape(pathsep)}{re.escape(attr)}\t{re.escape(json.dumps(value))}'
    )
    i1 = (reg.sub(r'\1', line) for line in stdin)
    # Replace empty strings with the root pathsep.
    return (re.sub(r'^$', pathsep, line) for line in i1)
    # return iter(stdin |
    #             calabash.common.sed(r'^(.*)%s%s\t%s' % (
    #                 re.escape(pathsep),
    #                 re.escape(attr),
    #                 re.escape(json.dumps(value))),
    #                 r'\1', exclusive=True) |
    #             calabash.common.sed(r'^$', pathsep))
