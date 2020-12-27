#!/usr/bin/env python3
# encoding: utf-8

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


import enum
import inspect
import itertools


class CommandParser:

    discard = ("a", "an", "any", "her", "his", "my", "some", "the", "their")

    @staticmethod
    def unpack_annotation(name, annotation, ensemble):
        terms = annotation if isinstance(annotation, list) else [annotation]
        for t in terms:
            if issubclass(t, enum.Enum):
                yield from (
                    (name, i) for i in t for v in (
                        [i.value] if isinstance(i.value, str) else i.value
                    )
                )
            else:
                yield from ((name, i) for i in ensemble if isinstance(i, t))

    @staticmethod
    def parse_tokens(text, preserver=".", discard=None):
        discard = discard or set()
        return [
            i.strip()
            for i in text.rstrip(preserver).lower().split()
            if i not in discard or text.endswith(preserver)
        ]

    @staticmethod
    def expand_commands(method, ensemble=[]):
        """
        Read a method's docstring and expand it to create all possible matching
        command phrases. Calculate the corresponding keyword arguments.

        Generates pairs of each command with a 2-tuple; (method, keyword arguments).

        """
        doc = method.func.__doc__ if hasattr(method, "func") else method.__doc__
        terms = list(filter(None, (i.strip() for line in doc.splitlines() for i in line.split("|"))))
        params = list(itertools.chain(
            list(CommandParser.unpack_annotation(p.name, p.annotation, ensemble))
            for p in inspect.signature(method, follow_wrapped=True).parameters.values()
            if p.annotation != inspect.Parameter.empty
        ))
        cartesian = [dict(i) for i in itertools.product(*params)]
        for term in terms:
            tokens = CommandParser.parse_tokens(term, discard=CommandParser.discard)
            for prod in cartesian:
                try:
                    yield (" ".join(tokens).format(**prod).lower(), (method, prod))
                except (AttributeError, IndexError, KeyError) as e:
                    continue
