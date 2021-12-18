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

from collections import defaultdict
from collections import deque
from collections import namedtuple
import functools
import importlib.resources
import itertools
import math
import operator
import pathlib
import string

from turberfield.catchphrase.mediator import Mediator
from turberfield.dialogue.model import Model
from turberfield.dialogue.model import SceneScript
from turberfield.dialogue.performer import Performer
from turberfield.dialogue.types import Stateful
from turberfield.utils.misc import group_by_type


class Presenter:

    Animation = namedtuple("Animation", ["delay", "duration", "element"])

    @staticmethod
    @functools.lru_cache()
    def load_dialogue(pkg, resource):
        """
        FIXME: Docs
        """
        if not pkg:
            return pathlib.Path(resource).read_text(encoding="utf-8")

        with importlib.resources.path(pkg, resource) as path:
            return path.read_text(encoding="utf-8")

    @classmethod
    def build_presenter(cls, folder, *args, facts=None, ensemble=None, strict=True, roles=1):
        rv = None
        paths = getattr(folder, "paths", folder)
        pkg = getattr(folder, "pkg", None)
        for n, p in enumerate(paths):
            text = cls.load_dialogue(pkg, p)
            text = string.Formatter().vformat(text, args, facts or defaultdict(str))
            rv = cls.build_from_text(
                text, index=n, ensemble=ensemble or [], strict=strict, roles=roles, path=p
            )
            if rv:
                break

        return rv

    @classmethod
    def build_from_text(cls, text, index=None, ensemble=[], strict=True, roles=1, path="inline"):
        script = SceneScript(path, doc=SceneScript.read(text))
        selection = script.select(ensemble, roles=roles)
        if all(selection.values()) or (not strict and any(selection.values())):
            script.cast(selection)
            casting = {next(iter(i.attributes.get("names", [])), None): i.persona for i in selection}
            model = script.run()
            rv = cls(model, index=index, casting=casting, ensemble=ensemble, text=text)
            for k, v in model.metadata:
                rv.metadata[k].append(v)
            return rv

    @staticmethod
    def allows(item: Model.Condition):
        return Performer.allows(item)

    @classmethod
    def animate_audio(cls, seq):
        """ Generate animations for audio effects."""
        yield from (
            cls.Animation(asset.offset, asset.duration, asset)
            for asset in seq
        )

    @classmethod
    def animate_lines(cls, seq, dwell, pause):
        """ Generate animations for lines of dialogue."""
        offset = 0
        for line in seq:
            duration = pause + dwell * line.text.count(" ")
            yield cls.Animation(offset, duration, line)
            offset += duration

    @classmethod
    def animate_stills(cls, seq):
        """ Generate animations for still images."""
        yield from (
            cls.Animation(
                getattr(still, "offset", 0) or 0 / 1000,
                getattr(still, "duration", 0) or 0 / 1000,
                still
            )
            for still in seq
        )

    @classmethod
    def animate_video(cls, seq):
        """ Generate animations for video effects."""
        yield from (
            cls.Animation(asset.offset, asset.duration, asset)
            for asset in seq
        )

    @staticmethod
    def refresh_animations(cls, frame, min_val=8):
        rv = min_val
        for typ in (Model.Line, Model.Still, Model.Audio):
            try:
                last_anim = next(filter(None, reversed(frame[typ])))
                rv = max(rv, math.ceil(last_anim.delay + last_anim.duration))
            except (IndexError, StopIteration, TypeError) as e:
                continue
        return rv

    def __init__(self, dialogue, index=None, scene=None, casting=None, ensemble=None, text=""):
        self.index = index
        self.frames = [
            defaultdict(list, dict(
                group_by_type(i.items),
                name=i.name, scene=i.scene
            ))
            for i in getattr(dialogue, "shots", [])
            if scene is None or i.scene == scene
        ]
        self.casting = casting or {}
        self.ensemble = ensemble or []
        self.metadata = defaultdict(list)
        self.text = text

    @property
    def dwell(self) -> float:
        return float(next(reversed(self.metadata["dwell"]), "0.3"))

    @property
    def pause(self) -> float:
        return float(next(reversed(self.metadata["pause"]), "1.0"))

    @property
    def pending(self) -> int:
        return len([
            frame for frame in self.frames
            if not frame[Model.Condition] or any([self.allows(i) for i in frame[Model.Condition]])
        ])

    def animate(self, frame, dwell=0.3, pause=1, react=True):
        """ Return the next shot of dialogue as an animated frame."""
        if all([self.allows(i) for i in frame[Model.Condition]]):
            frame[Model.Line] = list(
                self.animate_lines(frame[Model.Line], dwell, pause)
            )
            frame[Model.Audio] = list(self.animate_audio(frame[Model.Audio]))
            frame[Model.Still] = list(self.animate_stills(frame[Model.Still]))
            frame[Model.Video] = list(self.animate_video(frame[Model.Video]))
            for p in frame[Model.Property]:
                if react and p.object is not None:
                    setattr(p.object, p.attr, p.val)

            for m in frame[Model.Memory]:
                if react and m.object is None:
                    m.subject.set_state(m.state)
                elif react:
                    m.object.set_state(m.state)

                try:
                    if m.subject.memories[0].state != m.state:
                        m.subject.memories.appendleft(m)
                except AttributeError:
                    m.subject.memories = deque([m], maxlen=6)
                except IndexError:
                    m.subject.memories.appendleft(m)
            return frame
