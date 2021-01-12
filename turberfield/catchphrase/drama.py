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
import functools
import importlib.resources
import itertools
import random
import re
import textwrap

from turberfield.catchphrase.parser import CommandParser

# From Addison Arches
from collections import namedtuple

Action = namedtuple(
    "Action", ["name", "rel", "typ", "ref", "method", "parameters", "prompt"])


class Drama:

    Parameter = namedtuple("Parameter", ["name", "required", "regex", "values", "tip"])
    Record = namedtuple("Record", ["fn", "args", "kwargs", "lines"])

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

    @staticmethod
    def build():
        return []

    @staticmethod
    @functools.cache
    def load_dialogue(pkg, resource):
        with importlib.resources.path(pkg, resource) as path:
            return path.read_text(encoding="utf-8")

    @staticmethod
    def build_dialogue(*args, shot="", entity=""):
        shots = iter([shot]) if isinstance(shot, str) else iter(shot)
        entities = itertools.repeat(entity) if isinstance(entity, str) else entity
        for arg in args:
            shot = next(shots, "")
            under = "-" * len(shot)
            lines = [arg] if isinstance(arg, str) else arg
            if shot:
                yield f"\n\n{shot}\n{under}\n"
            for entity, line in zip(entities, lines):
                if entity:
                    yield f"\n[{entity}]_\n\n    {line}\n"
                else:
                    yield line + "\n"

    @staticmethod
    def write_dialogue(text, *args, shot="Drama dialogue", entity=""):
        # Find how many format parameters there are in the dialogue text
        slots = set(re.findall("\{\d+\}", text))
        if not slots:
            # Append drama dialogue to end of text
            dialogue = Drama.build_dialogue(*args, entity=entity)
            return "{0}\n{1}".format(text, "".join(tuple(dialogue)))
        elif len(slots) == 1:
            # Bind dialogue as a single shot to the format parameter
            dialogue = "\n".join(Drama.build_dialogue(*args, shot=shot, entity=entity))
            return text.format(dialogue)
        else:
            # Bind each line of dialogue to its own format parameter
            dialogue = Drama.build_dialogue(*args, entity=entity)
            return text.format(*itertools.chain(dialogue, itertools.repeat("", len(slots))))

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
            yield "\n{0}\n".format(self.refusal)
        else:
            lines = list(fn(fn, *args, **kwargs))
            self.history.append(self.Record(fn, args, kwargs, lines))
            yield from lines

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
            yield (None, [text], {})

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
