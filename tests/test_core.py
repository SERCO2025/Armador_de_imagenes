import unittest
from PIL import Image, ImageDraw

from armador.core import detect_side_borders, crop_side_borders, find_vertical_overlap, stitch_vertical


class CoreTests(unittest.TestCase):
    def test_side_border_detection_proposes_black_margins(self):
        image = Image.new("RGB", (100, 40), "black")
        ImageDraw.Draw(image).rectangle((10, 0, 89, 39), fill="white")
        self.assertEqual(detect_side_borders(image), (10, 90))

    def test_crop_does_not_resize(self):
        image = Image.new("RGB", (100, 40), "white")
        cropped = crop_side_borders(image, (10, 90))
        self.assertEqual(cropped.size, (80, 40))

    def test_stitch_keeps_exact_pixels_and_dimensions(self):
        top = Image.new("RGB", (12, 20), "white")
        bottom = Image.new("RGB", (12, 20), "white")
        ImageDraw.Draw(top).rectangle((0, 10, 11, 19), fill="red")
        ImageDraw.Draw(bottom).rectangle((0, 0, 11, 9), fill="red")
        result = stitch_vertical(top, bottom, 10)
        self.assertEqual(result.size, (12, 30))
        self.assertEqual(result.getpixel((0, 25)), bottom.getpixel((0, 15)))

    def test_overlap_search_returns_reviewable_proposal(self):
        top = Image.new("RGB", (80, 100), "white")
        draw = ImageDraw.Draw(top)
        draw.rectangle((5, 30, 60, 50), fill="black")
        bottom = top.crop((0, 40, 80, 100))
        # Both input images are required to have equal width; matching is bounded.
        result = find_vertical_overlap(top, bottom, min_overlap=10, max_overlap=50, stride=1)
        self.assertIn("overlap_pixels", result)
        self.assertIn("needs_review", result)


if __name__ == "__main__":
    unittest.main()
