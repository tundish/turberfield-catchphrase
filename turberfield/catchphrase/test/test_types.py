import unittest


import textwrap
import uuid

from turberfield.catchphrase.render import Settings

from turberfield.dialogue.model import SceneScript
from turberfield.dialogue.model import Model


class ModelTests(unittest.TestCase):

    def test_init_from_setter(self):
        text = textwrap.dedent("""
        .. entity:: THEME_SETTINGS

        .. property:: THEME_SETTINGS.midtone hsl(86, 93%, 12%, 0.7)
        """)
        uid = uuid.uuid4()
        theme = type("Fake", (), {})()
        theme.settings = Settings(id=uid)
        script = SceneScript("inline", doc=SceneScript.read(text))
        script.cast(script.select([theme.settings]))
        model = Model(script.fP, script.doc)
        script.doc.walkabout(model)
        self.assertEqual(1, len(model.shots))
        shot = model.shots[0]
        self.assertEqual(1, len(shot.items))
        setter = shot.items[0]
        self.assertIsInstance(setter, Model.Property)


class SettingsTests(unittest.TestCase):

    def test_init_from_setter(self):
        text = textwrap.dedent("""
        .. entity:: THEME_SETTINGS

        Scene
        =====

        Shot
        ----

        .. property:: THEME_SETTINGS.midtone hsl(86, 93%, 12%, 0.7)
        """)
        uid = uuid.uuid4()
        theme = type("Fake", (), {})()
        theme.settings = Settings(id=uid)
        script = SceneScript("inline", doc=SceneScript.read(text))
        script.cast(script.select([theme.settings]))
        model = Model(script.fP, script.doc)
        script.doc.walkabout(model)
        self.assertEqual(1, len(model.shots))
        shot = model.shots[0]
        self.assertEqual(1, len(shot.items))
        setter = shot.items[0]
        self.assertIsInstance(setter, Model.Property)
