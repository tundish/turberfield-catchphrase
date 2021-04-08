#!/usr/bin/env python3
# encoding: UTF-8

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

import unittest

#

import enum
from collections import Counter
from collections import defaultdict
import re
from types import SimpleNamespace

from turberfield.dialogue.types import EnumFactory
from turberfield.dialogue.types import Stateful

__doc__ = """

Explore possibilities of state age so design with timed coloured Petri Nets might be possible.

"""


class State(EnumFactory):
    pass


class Impulsive(Stateful):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._states = defaultdict(Counter)

    @property
    def tally(self):
        return {k: next(iter(c.values()), 0) for k, c in self._states.items()}

    def set_state(self, *args):
        for new_state in args:
            key = type(new_state).__name__
            old_state = self.get_state(type(new_state))
            if new_state != old_state:
                counter = Counter([new_state])
                self._states[key] = counter + self._states[key]
            else:
                self._states[key][new_state] += 1 
        return self

    def get_state(self, typ=int, default=0):
        return next(iter(self._states[typ.__name__]), default)


class StateTests(unittest.TestCase):

    class Crossing(enum.Enum):

        waiting = enum.auto()
        pausing = enum.auto()
        walking = enum.auto()
        running = enum.auto()
        arrived = enum.auto()

    def test_regex(self):
        fmt = "{0.tally[Crossing]:02}"
        pattern = "(?P<even>\d+[02468])|(?P<odd>\d+[13579])"
        regex = re.compile(pattern.format())
        obj = Impulsive()
        obj.state = self.Crossing.waiting
        for n in range(64):
            obj.state = self.Crossing.waiting
            text = fmt.format(obj)
            with self.subTest(obj=obj, text=text):
                m = regex.match(text)
                self.assertTrue(m)
                self.assertEqual("odd" if n % 2 else "even", m.lastgroup)

    def test_compatibility(self):
        obj = Impulsive()
        self.assertEqual(0, obj.get_state(self.Crossing))
        obj.state = self.Crossing.waiting
        self.assertEqual(self.Crossing.waiting, obj.get_state(self.Crossing))

        obj.state = self.Crossing.walking
        self.assertEqual(self.Crossing.walking, obj.get_state(self.Crossing))

        obj.state = self.Crossing.arrived
        self.assertEqual(self.Crossing.arrived, obj.get_state(self.Crossing))

    def test_aging(self):
        obj = Impulsive()
        obj.state = self.Crossing.waiting
        self.assertEqual(self.Crossing.waiting, obj.get_state(self.Crossing))

        obj.state = self.Crossing.walking
        self.assertEqual(self.Crossing.walking, obj.get_state(self.Crossing))

        obj.state = self.Crossing.walking
        self.assertEqual(self.Crossing.walking, obj.get_state(self.Crossing))

        obj.state = self.Crossing.walking
        self.assertEqual(self.Crossing.walking, obj.get_state(self.Crossing))

        obj.state = self.Crossing.walking
        self.assertEqual(self.Crossing.walking, obj.get_state(self.Crossing))

        obj.state = self.Crossing.walking
        self.assertEqual(self.Crossing.walking, obj.get_state(self.Crossing))

        obj.state = self.Crossing.arrived
        self.assertEqual(self.Crossing.arrived, obj.get_state(self.Crossing))

