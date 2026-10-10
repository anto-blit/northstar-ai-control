"""Content-preservation and portable publishing checks; no model calls."""
import hashlib
from pathlib import Path
import unittest
from pip_assets import SOURCE, build_assets, metadata, transcript


class PipTests(unittest.TestCase):
    def test_source_preserves_original_except_authorized_domain_fix(self):
        source = SOURCE.read_bytes()
        self.assertEqual(source.count(b'dontkillthehumans.org'), 1)
        original = source.replace(b'dontkillthehumans.org', b'tentozero.org').replace(
            b'<rect x="310" y="412" width="340"', b'<rect x="355" y="412" width="250"')
        self.assertEqual(hashlib.sha256(original).hexdigest(), '8194241f3eb623c054d15f7fada93505458d0d43ac5b672bbb23932ce8b3d766')

    def test_scenes_and_timing_are_preserved(self):
        episodes = metadata()
        self.assertEqual([e['duration'] for e in episodes], [77500, 79500, 103000])
        self.assertEqual([len(e['scenes']) for e in episodes], [11, 11, 12])
        for i, episode in enumerate(episodes):
            from html import unescape
            text = unescape(transcript(i))
            for scene in episode['scenes']:
                self.assertIn(scene['caption'], text)

    def test_player_reuses_original_scenes_and_audio_verbatim(self):
        source = SOURCE.read_text(encoding='utf-8')
        core = source.split('<script>')[1].split('/* ---------- player ---------- */')[0]
        player = build_assets()['watch/player.html'].decode()
        self.assertIn(core, player)
        self.assertNotIn('fonts.googleapis.com', player)

    def test_episode_pages_have_searchable_transcripts_and_share_metadata(self):
        assets = build_assets()
        for episode in metadata():
            page = assets[f'watch/{episode["slug"]}/index.html'].decode()
            self.assertIn('property="og:image"', page)
            self.assertIn('name="twitter:card"', page)
            self.assertIn('pip-transcript', page)
            self.assertIn(episode['evidenceLabel'], page)
            self.assertIn('watch/previews/'+episode['slug']+'.png', assets)


if __name__ == '__main__':
    unittest.main()
