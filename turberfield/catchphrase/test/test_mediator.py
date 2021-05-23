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

class MediatorBuildDialogueTests(unittest.TestCase):

    def test_simple(self):
        line = "Single line mediator."
        rv = "\n".join(Mediator.build_dialogue(line))
        self.assertIn(line, rv, rv)
        self.assertNotIn("-", rv)
        self.assertNotIn("]_", rv, rv)
        self.assertTrue(rv.endswith("\n"))

    def test_entity(self):
        line = "Single line mediator."
        rv = "\n".join(Mediator.build_dialogue(line, shot="Epilogue", entity="NARRATOR"))
        self.assertIn(line, rv)
        self.assertIn("Epilogue\n--------", rv)
        self.assertIn("[NARRATOR]_", rv)
        self.assertTrue(rv.endswith("\n"))

    def test_multiline_shot(self):
        lines = ["Say hello.", "Wave goodbye"]
        rv = "\n".join(Mediator.build_dialogue(*lines, shot="Epilogue", entity="NARRATOR"))
        self.assertEqual(1, rv.count("Epilogue\n-----"))
        self.assertEqual(2, rv.count("[NARRATOR]_"))

    def test_multishot_lines(self):
        lines = ["Say hello.", "Wave goodbye"]
        rv = "\n".join(Mediator.build_dialogue(*lines, shot=["one", "two"], entity="NARRATOR"))
        self.assertEqual(1, rv.count("one\n---"), rv)
        self.assertEqual(1, rv.count("two\n---"), rv)
        self.assertEqual(2, rv.count("[NARRATOR]_"))


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


class MediatorWriteDialogueTests(unittest.TestCase):

    def test_append_simple(self):
        text = textwrap.dedent("""
        Dialogue
        ========
        
        1
        -

        I have a line.
        """)
        line = "And another line"
        rv = Mediator.write_dialogue(text, line)
        self.assertEqual(len(text) + len(line) + 2, len(rv), rv)

    def test_simple_format(self):
        shot = "Mediator dialogue"
        text = textwrap.dedent("""
        Dialogue
        ========
        
        1
        -

        I have a line.
        {0}

        2
        -

        There, I've finished.
        """)
        line = "And another line"
        rv = Mediator.write_dialogue(text, line)
        self.assertEqual(len(text) + len(line) + 6 + 2 * len(shot) - 3, len(rv), rv)

    def test_format_error(self):
        text = textwrap.dedent("""
        Dialogue
        ========
        
        1
        -

        I have a line.
        {0}

        2
        -

        {1}
        There, I've finished.
        """)
        line = "And another line"
        rv = Mediator.write_dialogue(text, line)
        self.assertEqual(len(text) + len(line) - 6 + 1, len(rv), rv)

    def test_format_multi(self):
        text = textwrap.dedent("""
        Dialogue
        ========

        1
        -

        {0}
        I have a line.

        2
        -

        {1}
        {0}

        3
        -

        {2}
        There, I've finished.
        """)
        lines = ["Every now and again.", "And another line.", "And this one.", ]
        rv = Mediator.write_dialogue(text, *lines)
        self.assertEqual(len(text) + len([i for l in lines for i in l]) + 12, len(rv), rv)
