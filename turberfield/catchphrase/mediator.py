#!/usr/bin/env python3
#   encoding: utf-8

# This file is part of turberfield.
#
# Turberfield is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Turberfield is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with turberfield.  If not, see <http://www.gnu.org/licenses/>.

import collections.abc
from collections import defaultdict
from collections import deque
from collections import namedtuple
import difflib
import itertools
import random
import re
import textwrap
import types

from turberfield.catchphrase.parser import CommandParser



class Mediator:

    """

    Mediator objects are callable objects. They operate via Python's callable and generator protocols.

    They also conform to two conventions:

    * The docstrings of their methods declare syntax for the Catchphrase parser_.
    * Mediator objects dynamically generate dialogue.

    Mediator methods must declare by annotation the types of their keyword parameters.
    They must also provide a docstring to define the format of the text commands which apply to them.

    Subclasses will override these methods:

    * build
    * interpret

    """
    Record = namedtuple("Record", ["name", "args", "kwargs", "result"])

    def __init__(self, *args, maxlen=None, serializer=None, **kwargs):
        self.active = set(filter(None, (getattr(self, i, None) for i in args)))
        self.serializer = serializer or "\n".join
        self.facts = defaultdict(str)
        self.history = deque(maxlen=maxlen)

    def __call__(self, fn, *args, **kwargs):
        rv = fn(fn, *args, **kwargs)
        if not isinstance(rv, collections.abc.Sized) and isinstance(rv, collections.abc.Iterable):
            rv = list(rv)
        if isinstance(rv, (list, tuple)):
            rv = self.serializer(rv)

        self.history.appendleft(self.Record(fn.__name__, args, kwargs, rv))
        return rv

    def interpret(self, options):
        return next(iter(options), (None,) * 3)

    def match(self, text, context=None, ensemble=[], cutoff=0.95):
        """
        FIXME: Docs
        """
        options = defaultdict(list)
        for fn in self.active:
            for k, v in CommandParser.expand_commands(fn, ensemble, parent=self):
                options[k].append(v)

        tokens = CommandParser.parse_tokens(text, discard=CommandParser.discard)
        matches = (
            difflib.get_close_matches(" ".join(tokens), options, cutoff=cutoff)
            or difflib.get_close_matches(text.strip(), options, cutoff=cutoff)
        )
        try:
            yield from ((fn, [text, context], kwargs) for fn, kwargs in options[matches[0]])
        except (IndexError, KeyError):
            yield (None, [text, context], {})
