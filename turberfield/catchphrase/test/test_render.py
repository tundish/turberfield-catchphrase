import unittest


import textwrap
import uuid

from turberfield.catchphrase.presenter import Presenter
from turberfield.catchphrase.render import Renderer

from turberfield.dialogue.model import SceneScript
from turberfield.dialogue.model import Model


class RenderTests(unittest.TestCase):

    def test_render_audio(self):
        text = textwrap.dedent("""
        .. fx:: pot.mp3  crow_call-3s.mp3
           :offset: 0
           :duration: 3000
           :loop: 1

        """)
        uid = uuid.uuid4()
        script = SceneScript("inline", doc=SceneScript.read(text))
        script.cast(script.select([]))
        model = Model(script.fP, script.doc)
        script.doc.walkabout(model)

        self.assertEqual(1, len(model.shots))
        shot = model.shots[0]
        self.assertEqual(1, len(shot.items))
        setter = shot.items[0]
        self.assertIsInstance(setter, Model.Audio)

        presenter = Presenter(model)
        animation = presenter.animate(presenter.frames[0])
        rv = Renderer.animated_audio_to_html(animation[Model.Audio][0])
        self.assertIn('src="/audio/crow_call-3s.mp3"', rv)
