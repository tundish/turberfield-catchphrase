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
    Record = namedtuple("Record", ["fn", "args", "kwargs", "result"])

    @classmethod
    def param(cls, name, required, regex, values, tip):
        """ Experimental. Do not use. """
        def decorator(method):
            p = cls.Parameter(name, required, regex, values, tip)
            if not hasattr(method, "parameters"):
                method.parameters = []
            method.parameters.append(p)
            return method
        return decorator

    def __init__(self, *args, serializer=None, **kwargs):
        self.active = set(filter(None, (getattr(self, i, None) for i in args)))
        self.serializer = serializer or "\n".join
        self.facts = defaultdict(str)
        self.history = deque()
        self.lookup = defaultdict(set)

    def __call__(self, fn, *args, **kwargs):
        rv = fn(fn, *args, **kwargs)
        if isinstance(fn, types.GeneratorType):
            rv = list(rv)
        if isinstance(rv, (list, tuple)):
            rv = self.serializer(rv)

        self.facts[fn.__name__] = rv
        self.history.appendleft(self.Record(fn.__name__, args, kwargs, rv))
        return rv

    @property
    def ensemble(self):
        return list({i for s in self.lookup.values() for i in s})

    @property
    def turns(self):
        return len(self.history)

    def build(self, ensemble=None):
        yield from ensemble or []

    def add(self, *args):
        for item in args:
            for n in getattr(item, "names", []):
                self.lookup[n].add(item)

    def interlude(self, folder, index, **kwargs) -> dict:
        return {}

    def interpret(self, options):
        return next(iter(options), (None,) * 3)

    def match(self, text, ensemble=[], cutoff=0.95):
        """
        FIXME: Docs
        """
        options = defaultdict(list)
        for fn in self.active:
            for k, v in CommandParser.expand_commands(fn, ensemble + list(self.ensemble)):
                options[k].append(v)

        tokens = CommandParser.parse_tokens(text, discard=CommandParser.discard)
        matches = (
            difflib.get_close_matches(" ".join(tokens), options, cutoff=cutoff)
            or difflib.get_close_matches(text.strip(), options, cutoff=cutoff)
        )
        try:
            yield from ((fn, [text], kwargs) for fn, kwargs in options[matches[0]])
        except (IndexError, KeyError):
            yield (None, [text], {})

    # TODO: Move to a mixin
    def do_help(self, key, text):
        """
        help | ?

        """
        options = list(filter(
            lambda x: len(x) > 1,
            (i[0] for fn in self.active for i in CommandParser.expand_commands(fn, self.ensemble))
        ))
        return "\n".join("* {0}".format(i) for i in random.sample(options, min(3, len(options))))
