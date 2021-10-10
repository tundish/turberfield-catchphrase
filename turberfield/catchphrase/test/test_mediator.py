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

import textwrap
import unittest

from turberfield.catchphrase.mediator import Mediator


class Trivial(Mediator):

    def do_this(self, this, text, context):
        """
        This?

        """
        return "Yes, this."

    def do_that(self, this, text, context):
        """
        That?

        """
        return ["Yes.", "That."]

    def do_tother(self, this, text, context):
        """
        Or?

        """
        yield "Or,"
        yield "Maybe;"
        yield "Tother."


class MediatorMatchTests(unittest.TestCase):

    def setUp(self):
        self.mediator = Trivial("do_this", "do_that", "do_tother")

    def test_do_that(self):
        fn, args, kwargs = next(self.mediator.match("that?"))
        self.assertEqual(self.mediator.do_that, fn)
        self.assertEqual(["that?", None], args)
        self.assertFalse(kwargs)

    def test_mismatch(self):
        cmd = "release the frog"
        fn, args, kwargs = next(self.mediator.match(cmd))
        self.assertIs(None, fn)
        self.assertEqual([cmd, None], args)
        self.assertFalse(kwargs)


class MediatorFactsTests(unittest.TestCase):

    def setUp(self):
        self.mediator = Trivial("do_this", "do_that", "do_tother")

    def test_do_that(self):
        fn, args, kwargs = next(self.mediator.match("that?"))
        self.assertEqual(self.mediator.do_that, fn)
        self.assertEqual(["that?", None], args)
        self.assertFalse(kwargs)

        fn, args, kwargs = self.mediator.interpret([(fn, args, kwargs)])
        self.assertEqual(self.mediator.do_that, fn)
        self.assertEqual(["that?", None], args)

        data = self.mediator(fn, *args, **kwargs)
        self.assertEqual("Yes.\nThat.", data)
        self.assertFalse(self.mediator.facts[fn.__name__])

    def test_do_this(self):
        fn, args, kwargs = self.mediator.interpret(self.mediator.match("That?"))
        data = self.mediator(fn, *args, **kwargs)

        fn, args, kwargs = self.mediator.interpret(self.mediator.match("This?"))
        data = self.mediator(fn, *args, **kwargs)

        self.assertEqual("Yes, this.", data)
        self.assertFalse(self.mediator.facts[fn.__name__])

    def test_do_tother(self):
        fn, args, kwargs = self.mediator.interpret(self.mediator.match("That?"))
        data = self.mediator(fn, *args, **kwargs)

        fn, args, kwargs = self.mediator.interpret(self.mediator.match("This?"))
        data = self.mediator(fn, *args, **kwargs)

        fn, args, kwargs = self.mediator.interpret(self.mediator.match("Or?"))
        data = self.mediator(fn, *args, **kwargs)

        self.assertEqual("Or,\nMaybe;\nTother.", data)
        self.assertFalse(self.mediator.facts[fn.__name__])

