import json
import re
from functools import partial

import jsonpipe as jp

__all__ = ['jsonpipe', 'jsonunpipe', 'select', 'search_attr']


jsonpipe = jp.jsonpipe
jsonunpipe = jp.jsonunpipe
pipe = jp.pipe
pipe2 = jp.pipe2


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
        >>> list(pipe(jsonpipe, partial(select, path='/b'))(obj))
        ['/b\t{}',
        '/b/c\t3',
        '/b/d\t4']
        >>> pipe(jsonpipe, partial(select, path='/b'), jsonunpipe)(obj)
        {'b': {'c': 3, 'd': 4}}
    """

    path = re.sub(r'%s$' % re.escape(pathsep), r'', path)
    reg = re.compile(rf'^{re.escape(path)}[\t{re.escape(pathsep)}]')
    return (line for line in stdin if reg.match(line))

def sed(stdin, pattern_src, replacement, exclusive=False):
    r"""
    Apply :func:`re.sub` to each line on stdin with the given pattern/repl.

        >>> list(sed(iter(['cat', 'cabbage']), r'^ca', 'fu'))
        ['fut', 'fubbage']

    Upon encountering a non-matching line of input, :func:`sed` will pass it
    through as-is. If you want to change this behaviour to only yield lines
    which match the given pattern, pass `exclusive=True`::

        >>> list(sed(iter(['cat', 'nomatch']), r'^ca', 'fu'))
        ['fut', 'nomatch']
        >>> list(sed(iter(['cat', 'nomatch']), r'^ca', 'fu', exclusive=True))
        ['fut']

    """
    pattern = re.compile(pattern_src)
    for line in stdin:
        match = pattern.search(line)
        if match:
            yield (line[:match.start()] +
                   match.expand(replacement) +
                   line[match.end():])
        elif not exclusive:
            yield line

def search_attr(stdin, attr, value, pathsep='/'):
    r"""
    Search stdin for an exact attr/value pair.

    Yields paths to objects for which the given pair matches. Example:

        >>> obj = {'a': 1, 'b': {'a': 2, 'c': {'a': "Hello"}}}
        >>> list(pipe(jsonpipe, partial(search_attr, attr='a', value=1))(obj))
        ['/']
        >>> list(pipe(jsonpipe, partial(search_attr, attr='a', value=2))(obj))
        ['/b']
        >>> list(pipe(jsonpipe, partial(search_attr, attr='a', value="Hello"))(obj))
        ['/b/c']

    Multiple matches will result in multiple paths being yielded:

        >>> obj = {'a': 1, 'b': {'a': 1, 'c': {'a': 1}}}
        >>> list(pipe(jsonpipe, partial(search_attr, attr='a', value=1))(obj))
        ['/', '/b', '/b/c']
    """

    # '...path/attribute\tvalue' => 'path'.
    pattern = rf'^(.*){re.escape(pathsep)}{re.escape(attr)}\t{re.escape(json.dumps(value))}'
    blank = r'^$'
    return iter(
        pipe2(
            partial(sed, pattern_src=pattern, replacement=r'\1', exclusive=True),
            partial(sed, pattern_src=blank, replacement=pathsep)
        )(stdin)
    )

    # return iter(stdin |
    #             calabash.common.sed(r'^(.*)%s%s\t%s' % (
    #                 re.escape(pathsep),
    #                 re.escape(attr),
    #                 re.escape(json.dumps(value))),
    #                 r'\1', exclusive=True) |
    #             calabash.common.sed(r'^$', pathsep))
