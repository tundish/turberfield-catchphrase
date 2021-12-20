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

    def test_render_video_local(self):
        text = textwrap.dedent("""
        .. fx:: pot.mp4  crow_flying-3s.mp4
            :offset:    0
            :duration:  3000
            :loop:      1
            :label:     As the crow flies

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
        self.assertIsInstance(setter, Model.Video)

        presenter = Presenter(model)
        animation = presenter.animate(presenter.frames[0])
        rv = Renderer.animated_video_to_html(animation[Model.Video][0])
        self.assertIn('src="/video/crow_flying-3s.mp4"', rv)
        self.assertIn('type="video/mp4"', rv)

    def test_render_video_remote(self):
        text = textwrap.dedent("""
        .. fx:: pot.mp4 http://vimeo.com/abcdef/crow_flying-32s.mp4
            :offset:    0
            :duration:  32000
            :loop:      1
            :label:     As the crow flies
            :poster:    /img/cover.jpg
            :url:       http://vimeo.com/abcdef/

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
        self.assertIsInstance(setter, Model.Video)

        presenter = Presenter(model)
        animation = presenter.animate(presenter.frames[0])
        rv = Renderer.animated_video_to_html(animation[Model.Video][0])
        self.assertIn('src="http://vimeo.com/abcdef/crow_flying-32s.mp4"', rv)
        self.assertIn('poster="/img/cover.jpg"', rv)
        self.assertIn('<a href="http://vimeo.com/abcdef/">', rv)
        self.assertIn("Download MP4", rv)

    def test_render_video_url(self):
        text = textwrap.dedent("""
        .. fx:: pot.mp4 crow_flying-32s.mp4
            :offset:    0
            :duration:  32000
            :loop:      1
            :label:     As the crow flies
            :poster:    /img/cover.jpg
            :url:       http://vimeo.com/abcdef/

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
        self.assertIsInstance(setter, Model.Video)

        presenter = Presenter(model)
        animation = presenter.animate(presenter.frames[0])
        rv = Renderer.animated_video_to_html(animation[Model.Video][0])
        self.assertIn('src="http://vimeo.com/abcdef/"', rv)
        self.assertIn('poster="/img/cover.jpg"', rv)
        self.assertIn('<a href="http://vimeo.com/abcdef/">', rv)
        self.assertIn("Download MP4", rv)
