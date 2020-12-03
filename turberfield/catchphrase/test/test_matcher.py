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


import datetime
import unittest

from turberfield.catchphrase.matcher import MultiMatcher
from turberfield.dialogue.model import SceneScript


class MatcherTests(unittest.TestCase):

    def setUp(self):
        self.folders = [
            SceneScript.Folder(
                pkg=None,
                description=None,
                paths=None,
                interludes=None,
                metadata=i
            )
            for i in [
                {
                    "arc": "a_01",
                    "pathways": frozenset((
                        ("w12_latimer", "lockup"),
                    )),
                    "min_t": datetime.date(2020, 5, 1),
                    "max_t": datetime.date(2020, 5, 3),
                },
                {
                    "arc": "a_10",
                    "pathways": frozenset((
                        ("w12_latimer", "tavern"),
                    ))
                },
                {
                    "arc": "a_11",
                    "pathways": frozenset((
                        ("w12_latimer", "lockup"),
                        ("w12_latimer", "tavern"),
                    )),
                    "min_t": datetime.date(2020, 5, 5),
                    "max_t": datetime.date(2020, 5, 7),
                },
                {
                    "arc": "a_12",
                    "pathways": frozenset((
                        ("w12_latimer", "cafe"),
                        ("w12_latimer", "lockup"),
                    )),
                    "min_t": 1,
                    "max_t": 4,
                },
            ]
        ]

    def test_match_by_arc(self):
        matcher = MultiMatcher(self.folders)

        rv = list(matcher.options(arc="a_11"))
        self.assertEqual(1, len(rv), rv)
        self.assertEqual("a_11", rv[0].metadata["arc"])

    def test_match_by_pathway(self):
        matcher = MultiMatcher(self.folders)

        rv = list(matcher.options(
            pathways=set([("w12_latimer", "lockup")])
        ))
        self.assertEqual(3, len(rv), rv)
        self.assertEqual("a_01", rv[0].metadata["arc"])
        self.assertEqual("a_11", rv[1].metadata["arc"])
        self.assertEqual("a_12", rv[2].metadata["arc"])

    def test_match_by_tnteger(self):
        matcher = MultiMatcher(self.folders)

        rv = list(matcher.options(t=0))
        self.assertEqual(1, len(rv), rv)
        self.assertEqual("a_10", rv[0].metadata["arc"])

        rv = list(matcher.options(t=1))
        self.assertEqual(2, len(rv), rv)
        self.assertEqual("a_10", rv[0].metadata["arc"])
        self.assertEqual("a_12", rv[1].metadata["arc"])

    def test_match_by_str(self):
        matcher = MultiMatcher(self.folders)

        rv = list(matcher.options(t="0"))
        self.assertEqual(1, len(rv), rv)
        self.assertEqual("a_10", rv[0].metadata["arc"])

    def test_match_by_datetime(self):
        matcher = MultiMatcher(self.folders)

        for d in range(1, 4):
            t = datetime.date(2020, 5, d)
            with self.subTest(t=t):
                rv = list(matcher.options(t=t))
                self.assertEqual(2, len(rv), rv)
                self.assertEqual("a_01", rv[0].metadata["arc"])
                self.assertEqual("a_10", rv[1].metadata["arc"])
