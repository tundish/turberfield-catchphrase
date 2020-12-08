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

import types
import unittest

from turberfield.catchphrase.presenter import Presenter
from turberfield.dialogue.model import Model
from turberfield.dialogue.types import Stateful


class PresenterTests(unittest.TestCase):

    def test_condition_simple(self):
        obj = types.SimpleNamespace(name="test")
        c = Model.Condition(obj, "name", "test", None)
        self.assertTrue(Presenter.allows(c))

    def test_condition_state(self):
        obj = Stateful().set_state(4)
        c = Model.Condition(obj, "state", 4, None)
        self.assertTrue(Presenter.allows(c))

        c = Model.Condition(obj, "state", "4", None)
        self.assertFalse(Presenter.allows(c))
