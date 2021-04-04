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
from collections import defaultdict
from turberfield.dialogue.types import Stateful

__doc__ = """

Explore possibilities of state age so design with timed coloured Petri Nets might be possible.

"""


class State:
    pass


class Impulsive(Stateful):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._states = defaultdict(list)

    def set_state(self, *args):
        for value in args:
            self._states[type(value).__name__].append(value)
        return self

    def get_state(self, typ=int, default=0):
        return self._states.get(typ.__name__, [default])[-1]


class StateTests(unittest.TestCase):

    class Crossing(State, enum.Enum):

        waiting = enum.auto()
        pausing = enum.auto()
        walking = enum.auto()
        running = enum.auto()
        arrived = enum.auto()

    def test_deltas(self):
        self.fail(self.Crossing.waiting)

