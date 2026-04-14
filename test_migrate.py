# test_migrate.py
import unittest
from migrate import extract_reviews, extract_news_entries, slugify, NAV_LINKS

SAMPLE_REVIEW_HTML = '''<html><body>
<table><tr>
<td width="650">
  <table><tr><td class="body2">Chimera</td></tr>
  <tr><td class="body5">(2004, SEASONS OF MIST)</td></tr>
  <tr><td></td><td></td><td></td><td class="body4">8.0 / 10.0</td></tr></table>
  <table><tr><td class="body1">This is the review text.</td></tr></table>
</td>
<td width="650">
  <table><tr><td class="body2">Grand Declaration Of War</td></tr>
  <tr><td class="body5">(2000, SEASON OF MIST)</td></tr>
  <tr><td></td><td></td><td></td><td class="body4">8.5 / 10.0</td></tr></table>
  <table><tr><td class="body1">Another review.</td></tr></table>
</td>
</tr></table>
</body></html>'''

SAMPLE_NEWS_HTML = '''<html><body><table>
<tr><td width="550" bgcolor="#666666" class="body6">DARK THRONE</td></tr>
<tr><td class="body5">Some news about Dark Throne.</td></tr>
<tr><td width="550" bgcolor="#666666" class="body6">FINNTROLL</td></tr>
<tr><td class="body5">Some news about Finntroll.</td></tr>
</table></body></html>'''

class TestExtractReviews(unittest.TestCase):
    def test_extracts_two_albums(self):
        self.assertEqual(len(extract_reviews(SAMPLE_REVIEW_HTML)), 2)

    def test_title(self):
        self.assertEqual(extract_reviews(SAMPLE_REVIEW_HTML)[0]['title'], 'Chimera')

    def test_year(self):
        self.assertEqual(extract_reviews(SAMPLE_REVIEW_HTML)[0]['year'], '2004')

    def test_label(self):
        self.assertEqual(extract_reviews(SAMPLE_REVIEW_HTML)[0]['label'], 'SEASONS OF MIST')

    def test_score(self):
        self.assertEqual(extract_reviews(SAMPLE_REVIEW_HTML)[0]['score'], '8.0 / 10.0')

    def test_text(self):
        self.assertIn('review text', extract_reviews(SAMPLE_REVIEW_HTML)[0]['text'])

class TestExtractNews(unittest.TestCase):
    def test_two_entries(self):
        self.assertEqual(len(extract_news_entries(SAMPLE_NEWS_HTML)), 2)

    def test_band_name(self):
        self.assertEqual(extract_news_entries(SAMPLE_NEWS_HTML)[0]['band'], 'DARK THRONE')

    def test_content(self):
        self.assertIn('Dark Throne', extract_news_entries(SAMPLE_NEWS_HTML)[0]['content'])

class TestSlugify(unittest.TestCase):
    def test_lowercase(self):
        self.assertEqual(slugify('MAYHEM'), 'mayhem')

    def test_spaces(self):
        self.assertEqual(slugify('Dark Throne'), 'dark_throne')

class TestNavLinks(unittest.TestCase):
    def test_has_review(self):
        self.assertIn('review', NAV_LINKS)

if __name__ == '__main__':
    unittest.main()
