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
from types import SimpleNamespace

from turberfield.dialogue.types import EnumFactory
from turberfield.dialogue.types import Stateful

__doc__ = """

Explore possibilities of state age so design with timed coloured Petri Nets might be possible.

"""


class State(EnumFactory):
    pass


class Impulsive(Stateful):

    def __init__(self, period=6, **kwargs):
        super().__init__(**kwargs)
        self._states = defaultdict(Counter)
        self.period = period

    @property
    def pulse(self):
        for s in self._states.values():
            period = s.states[s.name]
            print(period)
        return {k: (next(iter(c.values()), 0) % self.period) or self.period for k, c in self._states.items()}

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

    class CrossingMachine:

        states = {
            "waiting": 6,
            "pausing": 1,
            "walking": 3,
            "running": 2,
            "arrived": 6,
        }

    Crossing = enum.Enum("Crossing", CrossingMachine.states, type=State)

    def test_aging(self):
        fmt = "{0.age:02X}"
        for age in range(64):
            obj = SimpleNamespace(age=age)
            print(fmt.format(obj))

    def test_compatibility(self):
        obj = Impulsive()
        self.assertEqual(0, obj.get_state(self.Crossing))
        obj.state = self.Crossing.waiting
        self.assertEqual(self.Crossing.waiting, obj.get_state(self.Crossing))

        obj.state = self.Crossing.walking
        self.assertEqual(self.Crossing.walking, obj.get_state(self.Crossing))

        obj.state = self.Crossing.arrived
        self.assertEqual(self.Crossing.arrived, obj.get_state(self.Crossing))

    def test_pulse(self):
        obj = Impulsive(period=4)
        obj.state = self.Crossing.waiting
        self.assertEqual(self.Crossing.waiting, obj.get_state(self.Crossing))
        self.assertEqual(1, obj.pulse["Crossing"])

        obj.state = self.Crossing.walking
        self.assertEqual(self.Crossing.walking, obj.get_state(self.Crossing))
        self.assertEqual(1, obj.pulse["Crossing"])

        obj.state = self.Crossing.walking
        self.assertEqual(self.Crossing.walking, obj.get_state(self.Crossing))
        self.assertEqual(2, obj.pulse["Crossing"])

        obj.state = self.Crossing.walking
        self.assertEqual(self.Crossing.walking, obj.get_state(self.Crossing))
        self.assertEqual(3, obj.pulse["Crossing"])

        obj.state = self.Crossing.walking
        self.assertEqual(self.Crossing.walking, obj.get_state(self.Crossing))
        self.assertEqual(4, obj.pulse["Crossing"])

        obj.state = self.Crossing.walking
        self.assertEqual(self.Crossing.walking, obj.get_state(self.Crossing))
        self.assertEqual(1, obj.pulse["Crossing"])

        obj.state = self.Crossing.arrived
        self.assertEqual(self.Crossing.arrived, obj.get_state(self.Crossing))
        self.assertEqual(1, obj.pulse["Crossing"])

