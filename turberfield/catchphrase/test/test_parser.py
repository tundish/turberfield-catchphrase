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
import unittest

from turberfield.catchphrase.parser import CommandParser

from turberfield.dialogue.types import DataObject


class ParserTests(unittest.TestCase):

    class Location(enum.Enum):
        HERE = "here"
        THERE = "there"

    class Liquid(DataObject): pass
    class Mass(DataObject): pass
    class Space(DataObject): pass

    def test_unpack_annotation_single_enum(self):
        rv = list(CommandParser.unpack_annotation("locn", ParserTests.Location, ensemble=[]))
        self.assertTrue(rv)
        self.assertTrue(all(isinstance(i, tuple) for i in rv), rv)
        self.assertEqual(
            len([v for i in ParserTests.Location for v in ([i.value] if isinstance(i.value, str) else i.value)]),
            len(rv),
            rv
        )

    def test_unpack_annotation_enum_list(self):
        class Season(enum.Enum):
            spring = "Spring"
            summer = "Summer"
            autumn = "Autumn"
            winter = "Winter"

        rv = list(CommandParser.unpack_annotation("item", [ParserTests.Location, Season], ensemble=[]))
        self.assertTrue(rv)
        self.assertTrue(all(isinstance(i, tuple) for i in rv), rv)
        self.assertTrue(all(isinstance(i[0], str) for i in rv), rv)
        self.assertTrue(all(isinstance(i[1], enum.Enum) for i in rv), rv)
        self.assertEqual(
            len([
                v for i in list(ParserTests.Location) + list(Season)
                for v in ([i.value] if isinstance(i.value, str) else i.value)
            ]),
            len(rv),
            rv
        )

    def test_unpack_annotation_single_class(self):
        ensemble = [ParserTests.Liquid(), ParserTests.Mass(), ParserTests.Space()]
        rv = list(CommandParser.unpack_annotation("item", ParserTests.Liquid, ensemble))
        self.assertTrue(rv)
        self.assertTrue(all(isinstance(i, tuple) for i in rv), rv)
        self.assertEqual(1, len(rv), rv)
        self.assertIsInstance(rv[0][1], ParserTests.Liquid)

    def test_unpack_annotation_dataobject(self):
        ensemble = [ParserTests.Liquid(), ParserTests.Mass(), ParserTests.Space()]
        rv = list(CommandParser.unpack_annotation("thing", [ParserTests.Liquid, ParserTests.Mass], ensemble))
        self.assertTrue(all(isinstance(i, tuple) for i in rv), rv)
        self.assertEqual(2, len(rv), rv)
        self.assertIsInstance(rv[0][1], ParserTests.Liquid)
        self.assertIsInstance(rv[1][1], ParserTests.Mass)

    def test_expand_commands_no_preserver(self):

        thing = DataObject(name="thing")

        def func(obj: DataObject):
            """
            pick up a {obj.name}
            """

        rv = dict(CommandParser.expand_commands(func, ensemble=[thing]))
        self.assertIn("pick up thing", rv)

    def test_expand_commands_sequence_with_preserver(self):

        thing = DataObject(names=["thing"])

        def func(obj: DataObject):
            """
            pick up a {obj.names[0]}.
            """

        rv = dict(CommandParser.expand_commands(func, ensemble=[thing]))
        self.assertIn("pick up a thing", rv)

    def test_expand_commands_sequence_no_preserver(self):

        thing = DataObject(names=["thing"])

        def func(obj: DataObject):
            """
            pick up a {obj.names[0]}
            """

        rv = dict(CommandParser.expand_commands(func, ensemble=[thing]))
        self.assertIn("pick up thing", rv)

    def test_expand_commands_sequence_synonyms_no_preserver(self):

        thing = DataObject(names=["thing", "doobrey"])
        idea = DataObject(names=["idea"])

        def func(obj: [object, DataObject]):
            """
            pick up a {obj.names[0]} | grab a {obj.names[0]}
            pick up a {obj.names[1]} | grab a {obj.names[1]}
            """

        rv = dict(CommandParser.expand_commands(func, ensemble=[idea, thing, idea]))
        self.assertIn("pick up thing", rv)
        self.assertIn("pick up doobrey", rv)
        self.assertIn("grab thing", rv)
        self.assertIn("grab doobrey", rv)

    def test_expand_commands_with_preserver(self):

        thing = DataObject(name="thing")

        def func(obj: DataObject):
            """
            pick up a {obj.name}.
            """

        rv = dict(CommandParser.expand_commands(func, ensemble=[thing]))
        self.assertIn("pick up a thing", rv)

    def test_expand_commands_discrimminator(self):

        ensemble = [
            DataObject(names=["thing"], colour="blue"),
            DataObject(names=["thing"], colour="red"),
        ]

        def func(obj: DataObject):
            """
            pick up a {obj.colour} {obj.names[0]}
            """

        rv = dict(CommandParser.expand_commands(func, ensemble=ensemble))
        self.assertIn("pick up blue thing", rv)
        self.assertEqual("blue", rv["pick up blue thing"][1]["obj"].colour)
        self.assertIn("pick up red thing", rv)
        self.assertEqual("red", rv["pick up red thing"][1]["obj"].colour)

