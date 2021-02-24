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
import functools
import importlib.resources
import itertools
import random
import re
import textwrap

from turberfield.catchphrase.parser import CommandParser



class Drama:

    """

    Drama objects are callable objects. They operate via Python's callable and generator protocols.

    They also conform to two conventions:

    * The docstrings of their methods declare syntax for the Catchphrase parser_.
    * Drama objects dynamically generate dialogue.

    Drama methods must declare by annotation the types of their keyword parameters.
    They must also provide a docstring to define the format of the text commands which apply to them.

    Subclasses will override these methods:

    * build
    * interpret

    """
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
        """
        FIXME: Docs
        """
        return []

    @staticmethod
    @functools.cache
    def load_dialogue(pkg, resource):
        """
        FIXME: Docs
        """
        with importlib.resources.path(pkg, resource) as path:
            return path.read_text(encoding="utf-8")

    @staticmethod
    def build_dialogue(*args, shot="", entity=""):
        """
        FIXME: Docs
        """
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
        """
        FIXME: Docs
        """
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

    def __init__(self, **kwargs):
        self.lookup = defaultdict(set)
        self.active = set()
        self.history = deque()

    def __call__(self, fn, *args, **kwargs):
        lines = list(fn(fn, *args, **kwargs))
        self.history.appendleft(self.Record(fn, args, kwargs, lines))
        yield from lines

    @property
    def ensemble(self):
        return list({i for s in self.lookup.values() for i in s})

    @property
    def turns(self):
        return len(self.history)

    def build(self):
        yield from []

    def add(self, *args):
        for item in args:
            for n in getattr(item, "names", []):
                self.lookup[n].add(item)

    def interlude(self, folder, index, **kwargs) -> dict:
        return {}

    def interpret(self, options):
        return next(iter(options), "")

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
