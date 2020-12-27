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
import difflib
import enum
import inspect
import itertools
import random
import textwrap
import random

from turberfield.catchphrase.parser import CommandParser
from turberfield.dialogue.types import DataObject
from turberfield.dialogue.types import Stateful

# From Addison Arches
from collections import namedtuple

Action = namedtuple(
    "Action", ["name", "rel", "typ", "ref", "method", "parameters", "prompt"])


class Drama:

    Parameter = namedtuple("Parameter", ["name", "required", "regex", "values", "tip"])

    @classmethod
    def param(cls, name, required, regex, values, tip):
        def decorator(method):
            p = cls.Parameter(name, required, regex, values, tip)
            if not hasattr(method, "parameters"):
                method.parameters = []
            method.parameters.append(p)
            return method
        return decorator

    @staticmethod
    def build():
        return []

    def __init__(self, lookup=None, prompt=">", refusal="That is not an option just now.", **kwargs):
        self.lookup = lookup or defaultdict(set)
        self.prompt = prompt
        self.refusal = refusal
        self.active = set([self.do_help])
        self.history = []
        for i in self.build():
            self.add(i)
        self.input_text = ""

    def __call__(self, fn, *args, **kwargs):
        self.input_text = args and args[0] or ""

        if fn is None:
            yield self.refusal
        else:
            self.history.append((fn, args, kwargs))
            yield from fn(fn, *args, **kwargs)

    def add(self, item):
        for n in getattr(item, "names", []):
            self.lookup[n].add(item)

    @property
    def ensemble(self):
        return list({i for s in self.lookup.values() for i in s}) + [self]

    @property
    def turns(self):
        return len(self.history)

    def match(self, text, ensemble=[], cutoff=0.95):
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
            yield (None, [], {})

    def interpret(self, options):
        return next(iter(options), "")

    def do_help(self, key, text):
        """
        help | ?

        """
        options = list(filter(
            lambda x: len(x) > 1,
            (i[0] for fn in self.active for i in CommandParser.expand_commands(fn, self.ensemble))
        ))
        hints = "\n".join("* {0}".format(i) for i in random.sample(options, min(3, len(options))))
        yield textwrap.dedent("""

        Here are some commands to try:

        {hints}

        """).format(text=text, hints=hints)
