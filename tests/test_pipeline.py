# run with :
# python -m unittest tests.test_pipeline
# python -m unittest discover     
import unittest
from Providers.ImapShotsProvider import ImapShotsProvider

class TestPipeline(unittest.TestCase):

    def test_imapShotsProvider(self):
        target = ImapShotsProvider('temp')
        shots = target.GetShots('camera/foscam')
        self.assertEqual(3, len(shots))
        self.assertIsNotNone(shots[0].filename)
        self.assertIsNotNone(shots[0].fullname)
        self.assertIsNotNone(shots[0].Exist())
        return