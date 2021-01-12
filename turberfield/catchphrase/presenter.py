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
import itertools
import math
import operator

from turberfield.catchphrase.drama import Drama
from turberfield.dialogue.model import Model
from turberfield.dialogue.model import SceneScript
from turberfield.dialogue.types import Stateful


class Presenter:

    Animation = namedtuple("Animation", ["delay", "duration", "element"])

    @staticmethod
    def build_presenter(folder, /, *args, ensemble=[], strict=True, roles=1):
        for n, p in enumerate(folder.paths):
            folder_dialogue = Drama.load_dialogue(folder.pkg, p)
            text = Drama.write_dialogue(folder_dialogue, *args)
            rv = Presenter.build_from_text(text, ensemble=ensemble, strict=strict, roles=roles, path=p)
            if rv:
                return (n, rv)
        else:
            return (None, None)

    @staticmethod
    def build_from_text(text, ensemble=[], strict=True, roles=1, path="inline"):
        script = SceneScript(path, doc=SceneScript.read(text))
        selection = script.select(ensemble, roles=roles)
        if all(selection.values()) or (not strict and any(selection.values())):
            script.cast(selection)
            model = script.run()
            rv = Presenter(model, ensemble=ensemble)
            for k, v in model.metadata:
                rv.metadata[k].append(v)
            return rv

    @staticmethod
    def allows(item: Model.Condition):
        if item.attr == "state" and isinstance(item.object, Stateful):
            lhs = item.object.get_state(type(item.val))
            rhs = item.val
        else:
            fmt = "".join(("{0.", item.attr, "}"))
            try:
                lhs = fmt.format(item.object)
            except (AttributeError, IndexError, KeyError, ValueError):
                return False
            else:
                rhs = str(item.val)

        op = item.operator or operator.eq
        return op(lhs, rhs)

    @staticmethod
    def animate_audio(seq):
        """ Generate animations for audio effects."""
        yield from (
            Presenter.Animation(asset.offset, asset.duration, asset)
            for asset in seq
        )

    @staticmethod
    def animate_lines(seq, dwell, pause):
        """ Generate animations for lines of dialogue."""
        offset = 0
        for line in seq:
            duration = pause + dwell * line.text.count(" ")
            yield Presenter.Animation(offset, duration, line)
            offset += duration

    @staticmethod
    def animate_stills(seq):
        """ Generate animations for still images."""
        yield from (
            Presenter.Animation(
                getattr(still, "offset", 0) or 0 / 1000,
                getattr(still, "duration", 0) or 0 / 1000,
                still
            )
            for still in seq
        )

    @staticmethod
    def refresh_animations(frame, min_val=8):
        rv = min_val
        for typ in (Model.Line, Model.Still, Model.Audio):
            try:
                last_anim = next(filter(None, reversed(frame[typ])))
                rv = max(rv, math.ceil(last_anim.delay + last_anim.duration))
            except (IndexError, StopIteration, TypeError) as e:
                continue
        return rv

    def __init__(self, dialogue, scene=None, ensemble=None):
        self.frames = [
            defaultdict(list, dict(
                {k: list(v) for k, v in itertools.groupby(i.items, key=type)},
                name=i.name, scene=i.scene
            ))
            for i in getattr(dialogue, "shots", [])
            if scene is None or i.scene == scene
        ]
        self.ensemble = ensemble
        self.metadata = defaultdict(list)

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
        if not frame[Model.Condition] or any([self.allows(i) for i in frame[Model.Condition]]):
            frame[Model.Line] = list(
                self.animate_lines(frame[Model.Line], dwell, pause)
            )
            frame[Model.Audio] = list(self.animate_audio(frame[Model.Audio]))
            frame[Model.Still] = list(self.animate_stills(frame[Model.Still]))
            for p in frame[Model.Property]:
                if react and p.object is not None:
                    setattr(p.object, p.attr, p.val)

            for m in frame[Model.Memory]:
                if react and m.object is None:
                    m.subject.set_state(m.state)
                try:
                    if m.subject.memories[-1].state != m.state:
                        m.subject.memories.append(m)
                except AttributeError:
                    m.subject.memories = deque([m], maxlen=6)
                except IndexError:
                    m.subject.memories.append(m)
            return frame
