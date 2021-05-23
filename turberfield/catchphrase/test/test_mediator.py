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

    def do_this(self, this, text):
        """
        This?

        """
        return "Yes, this"

    def do_that(self, this, text):
        """
        That?

        """
        return ["Yes", "that"]

    def do_tother(self, this, text):
        """
        Or?

        """
        yield "Or"
        yield "maybe"
        yield "tother"


class MediatorMatchTests(unittest.TestCase):

    def test_do_help(self):
        mediator = Mediator()
        mediator.active.add(mediator.do_help)
        fn, args, kwargs = next(mediator.match("help"))
        self.assertEqual(mediator.do_help, fn)
        self.assertEqual(["help"], args)
        self.assertFalse(kwargs)

    def test_mismatch(self):
        mediator = Mediator()
        cmd = "release the frog"
        fn, args, kwargs = next(mediator.match(cmd))
        self.assertIs(None, fn)
        self.assertEqual([cmd], args)
        self.assertFalse(kwargs)


class MediatorFactsTests(unittest.TestCase):

    def setUp(self):
        self.mediator = Trivial("do_this", "do_that", "do_tother")

    def test_do_this(self):
        fn, args, kwargs = next(self.mediator.match("this?"))
        self.assertEqual(self.mediator.do_this, fn)
        self.assertEqual(["this?"], args)
        self.assertFalse(kwargs)

        fn, args, kwargs = self.mediator.interpret([(fn, args, kwargs)])
        self.assertEqual(self.mediator.do_this, fn)
        self.assertEqual(["this?"], args)

        data = self.mediator(fn, *args, **kwargs)
        self.assertEqual("Yes, this", data)
        self.assertEqual("Yes, this", self.mediator.facts[fn.__name__])

