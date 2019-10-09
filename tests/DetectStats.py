import unittest
from PIL import Image
from P5Gallows import detect_stats


class DetectStatsTest(unittest.TestCase):
    def test_stats(self):
        img = Image.open('test.png')
        expected = ['en', 'lu']
        result = detect_stats(img)
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()

