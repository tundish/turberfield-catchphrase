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


class PresenterAllowsTests(unittest.TestCase):

    def test_condition_bad(self):
        obj = types.SimpleNamespace(name="test")
        c = Model.Condition(obj, "g:n[0]m*e", "test", None)
        self.assertFalse(Presenter.allows(c))

    def test_condition_complex(self):
        obj = types.SimpleNamespace(
            a={
                "b": types.SimpleNamespace(
                    c=[
                        types.SimpleNamespace(d="foo"),
                        types.SimpleNamespace(e="bar")
                    ]
                )
            }
        )
        c = Model.Condition(obj, "a[b].c[1].e", "bar", None)
        self.assertTrue(Presenter.allows(c))

    def test_condition_dict(self):
        obj = types.SimpleNamespace(
            a={"b": types.SimpleNamespace(c="test")}
        )
        c = Model.Condition(obj, "a[b].c", "test", None)
        self.assertTrue(Presenter.allows(c))

        c = Model.Condition(obj, "a[f].c", "test", None)
        self.assertFalse(Presenter.allows(c))

    def test_condition_float(self):
        obj = types.SimpleNamespace(value=1.234)
        c = Model.Condition(obj, "value:04.1f", "01.2", None)
        self.assertTrue(Presenter.allows(c))

    def test_condition_list(self):
        obj = types.SimpleNamespace(
            a=["foo", "bar"]
        )
        c = Model.Condition(obj, "a[0]", "foo", None)
        self.assertTrue(Presenter.allows(c))

        c = Model.Condition(obj, "a[2]", "foo", None)
        self.assertFalse(Presenter.allows(c))

    def test_condition_missing(self):
        obj = types.SimpleNamespace(name="test")
        c = Model.Condition(obj, "gnome", "test", None)
        self.assertFalse(Presenter.allows(c))

    def test_condition_mistyped(self):
        obj = types.SimpleNamespace(name="test")
        c = Model.Condition(obj, "name:02d", "test", None)
        self.assertFalse(Presenter.allows(c))

    def test_condition_simple(self):
        obj = types.SimpleNamespace(name="test")
        c = Model.Condition(obj, "name", "test", None)
        self.assertTrue(Presenter.allows(c))

        c = Model.Condition(obj, "name", "toast", None)
        self.assertFalse(Presenter.allows(c))

    def test_condition_nested(self):
        obj = types.SimpleNamespace(
            a=types.SimpleNamespace(
                b=types.SimpleNamespace(c="test")
            )
        )
        c = Model.Condition(obj, "a.b.c", "test", None)
        self.assertTrue(Presenter.allows(c))

    def test_condition_state(self):
        obj = Stateful().set_state(4)
        c = Model.Condition(obj, "state", 4, None)
        self.assertTrue(Presenter.allows(c))

        c = Model.Condition(obj, "state", "4", None)
        self.assertFalse(Presenter.allows(c))

class PresenterBuildShots(unittest.TestCase):

    def test_simple(self):
        line = "Single line drama."
        rv = "\n".join(Presenter.build_shots(line))
        self.assertIn(line, rv, rv)
        self.assertNotIn("-", rv)
        self.assertNotIn("]_", rv, rv)
        self.assertTrue(rv.endswith("\n"))

    def test_entity(self):
        line = "Single line drama."
        rv = "\n".join(Presenter.build_shots(line, shot="Epilogue", entity="NARRATOR"))
        self.assertIn(line, rv)
        self.assertIn("Epilogue\n--------", rv)
        self.assertIn("[NARRATOR]_", rv)
        self.assertTrue(rv.endswith("\n"))

    def test_multiline_shot(self):
        lines = ["Say hello.", "Wave goodbye"]
        rv = "\n".join(Presenter.build_shots(*lines, shot="Epilogue", entity="NARRATOR"))
        self.assertEqual(1, rv.count("Epilogue\n-----"))
        self.assertEqual(2, rv.count("[NARRATOR]_"))

    def test_multishot_lines(self):
        lines = ["Say hello.", "Wave goodbye"]
        rv = "\n".join(Presenter.build_shots(*lines, shot=["one", "two"], entity="NARRATOR"))
        self.assertEqual(1, rv.count("one\n---"), rv)
        self.assertEqual(1, rv.count("two\n---"), rv)
        self.assertEqual(2, rv.count("[NARRATOR]_"))
