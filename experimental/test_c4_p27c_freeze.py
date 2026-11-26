from p27c_freeze import freeze
import unittest
class P27CFreeze(unittest.TestCase):
    def test_generate_frozen_candidates(self):
        freeze()
