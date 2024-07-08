import unittest

from screenuler import helpers


class TestHelpers(unittest.TestCase):
    def test_get_position(self):
        assert (1, 1) == helpers.get_position('0x0+1+1')
        assert (0, 0) == helpers.get_position('1x1+0+0')

    def test_get_size(self):
        assert (1, 1) == helpers.get_size('1x1+0+0')
        assert (0, 0) == helpers.get_size('0x0+1+1')

if __name__ == '__main__':
    unittest.main()