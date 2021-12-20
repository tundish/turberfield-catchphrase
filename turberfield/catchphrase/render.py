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

from collections import namedtuple
import functools
import html
import re
import textwrap
import urllib.parse

from turberfield.catchphrase.mediator import Mediator
from turberfield.catchphrase.presenter import Presenter
from turberfield.dialogue.model import Model
from turberfield.dialogue.types import DataObject

"""
catchphrase-banner
    A region of decorative text and background images. Style multiple `catchphrase-banner`s with CSS `nth-of-type`.
catchphrase-reveal
    A region animated to progressively reveal the contents (may include images, icons, etc)
catchphrase-colour-shadows
    A reference to a theme-specific colour variable.

"""

Action = namedtuple("Action", ["name", "rel", "typ", "ref", "method", "parameters", "prompt"])
Parameter = namedtuple("Parameter", ["name", "required", "regex", "values", "tip"])


class Settings(DataObject):
    pass


class Renderer:

    @classmethod
    def param(cls, name, required, regex, values, tip):
        """ Experimental. Do not use. """
        def decorator(method):
            p = cls.Parameter(name, required, regex, values, tip)
            if not hasattr(method, "parameters"):
                method.parameters = []
            method.parameters.append(p)
            return method
        return decorator

    @classmethod
    def animated_audio_to_html(cls, anim, root="/", path="audio/", **kwargs):
        return f"""<div>
<audio src="{root}{path}{anim.element.resource}" autoplay="autoplay"
preload="auto" {'loop="loop"' if anim.element.loop and int(anim.element.loop) > 1 else ""}>
</audio>
</div>"""

    @classmethod
    def animated_video_to_html(cls, anim, root="/", path="video/", autoplay=True, preload="metadata", **kwargs):
        typ = "video/{0}".format(anim.element.resource.rsplit(".", 1)[-1])
        autoplay = "autoplay " if autoplay else ""
        url = anim.element.url
        link = '<a href="{0}">Download {1}</a>'.format(url, typ.split("/")[-1].upper()) if url else ""
        poster = f'poster="{anim.element.poster}"' if anim.element.poster else ""
        resource = anim.element.resource
        if urllib.parse.urlparse(anim.element.resource).scheme:
            root = ""
            path = ""
        elif url:
            resource = url
            root = ""
            path = ""
        return f"""<figure>
<video preload="{preload}" {autoplay}{poster}>
<source src="{root}{path}{resource}" type="{typ}">
{link}
</video>
<figcaption></figcaption>
</figure>"""

    @classmethod
    def animate_controls(cls, *args, delay=0, dwell=0, pause=0, **kwargs):
        for arg in args:
            yield '<li style="animation-delay: {0:.2f}s; animation-duration: {1:.2f}s">'.format(delay, dwell)
            yield arg.strip()
            yield "</li>"
            delay += pause

    @classmethod
    def animated_line_to_html(cls, anim, **kwargs):
        name = anim.element.persona.name if hasattr(anim.element.persona, "name") else ""
        name = "{0.firstname} {0.surname}".format(name) if hasattr(name, "firstname") else name
        if getattr(anim.element.persona, "history", []):  # As per Mediator
            tag = '<blockquote class="catchphrase-method-{0}">'.format(
                anim.element.persona.history[0].name.lower()
            )
        else:
            tag = "<blockquote>"
        return f"""
<li style="animation-delay: {anim.delay:.2f}s; animation-duration: {anim.duration:.2f}s">
{tag}
<header>{name}</header>
{anim.element.html}
</blockquote>
</li>"""

    @classmethod
    def animated_line_to_terminal(cls, anim):
        return "{0}{1}{2}".format(
            anim.element.persona.name if hasattr(anim.element.persona, "name") else "",
            ": " if hasattr(anim.element.persona, "name") else "",
            anim.element.text
        )

    @classmethod
    def animated_still_to_html(cls, anim, **kwargs):
        return f"""
<div style="animation-duration: {anim.duration}s; animation-delay: {anim.delay}s">
<img src="/img/{anim.element.resource}" alt="{anim.element.package} {anim.element.resource}" />
</div>"""

    @classmethod
    def render_action_form(cls, action: Action, autofocus=False):
        url = urllib.parse.quote(action.typ.format(*action.ref))
        if action.parameters:
            yield f'<form role="form" action="{url}" method="{action.method}" name="{action.name}">'
            yield "<fieldset>"

        for p in action.parameters:
            typ = "hidden" if p.required == "hidden" else "text"
            if not p.tip.endswith("."):
                yield f'<label for="input-{p.name}-{typ}" id="input-{p.name}-{typ}-tip">{html.escape(p.tip)}</label>'
            if not p.values:
                yield textwrap.dedent(f"""
                    <input
                    name="{p.name}"
                    pattern="{p.regex.pattern if p.regex else ''}"
                    {'required="required"' if p.required else ''}
                    {'autofocus="autofocus"' if autofocus else ''}
                    type="{'hidden' if p.required == 'hidden' else 'text'}"
                    title="{html.escape(p.tip)}"
                    />""")
            elif len(p.values) == 1:
                yield textwrap.dedent(f"""
                    <input
                    name="{p.name}"
                    placeholder="{p.values[0]}"
                    pattern="{p.regex.pattern if p.regex else ''}"
                    {'required="required"' if p.required else ''}
                    {'autofocus="autofocus"' if autofocus else ''}
                    type="{'hidden' if p.required == 'hidden' else 'text'}"
                    title="{html.escape(p.tip)}"
                    />""")
            else:
                yield f'<select name="{p.name}">'
                for v in p.values:
                    yield f'<option value="{v}">{v}</option>'
                yield "</select>"

        yield f'<button type="submit">{action.prompt}</button>'

        if action.parameters:
            yield "</fieldset>"
            yield "</form>"

    @classmethod
    def render_frame_to_terminal(cls, frame, ensemble=[], title="", backnav=""):
        for i in frame[Model.Line]:
            if i.element.text:
                yield (cls.animated_line_to_terminal(i), i.duration)

    @staticmethod
    def render_dict_to_css(mapping=None, tag=":root"):
        mapping = mapping or {}
        entries = "\n".join("--{0}: {1};".format(k, v) for k, v in mapping.items())
        return "{tag} {{\n{entries}\n}}".format(tag=tag, entries=entries)

    @classmethod
    def render_animated_frame_to_html(cls, frame, controls=[], **kwargs):
        dialogue = "\n".join(cls.animated_line_to_html(i, **kwargs) for i in frame[Model.Line])
        stills = "\n".join(cls.animated_still_to_html(i, **kwargs) for i in frame[Model.Still])
        audio = "\n".join(cls.animated_audio_to_html(i, **kwargs) for i in frame[Model.Audio])
        video = "\n".join(cls.animated_video_to_html(i, **kwargs) for i in frame[Model.Video])
        last = frame[Model.Line][-1] if frame[Model.Line] else Presenter.Animation(0, 0, None)
        controls = "\n".join(
            cls.animate_controls(*controls, delay=last.delay + last.duration, dwell=0.3, **kwargs)
        )
        return f"""
{audio}
{video}
<aside class="catchphrase-reveal">
{stills}
</aside>
<main class="catchphrase-reveal">
<ul>
{dialogue}
</ul>
</main>
<nav class="catchphrase-reveal">
<ul>
{controls}
</ul>
</nav>"""

    @staticmethod
    @functools.lru_cache()
    def render_body_html(title="", refresh=None, next_="", base_style="/css/base/catchphrase.css"):
        base_link = '<link rel="stylesheet" href="{0}" />'.format(base_style) if base_style else ""
        heading = " ".join("<span>{0}</span>".format(i.capitalize()) for i in title.split(" "))
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
{'<meta http-equiv="refresh" content="{0};{1}">'.format(refresh, next_) if refresh and next_ else ''}
<meta http-equiv="X-UA-Compatible" content="ie=edge">
<title>{title}</title>
{base_link}
{{0}}
</head>
<body>
<style type="text/css">
{{1}}
</style>
<section class="catchphrase-banner">
<h1>{heading}</h1>
</section>
{{2}}
</body>
</html>"""
