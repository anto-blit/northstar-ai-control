"""Package Pip's original cartoons without editing their editorial content."""
from html import escape
from pathlib import Path
import json
import re

HERE = Path(__file__).resolve().parent
SOURCE = HERE / 'pip/source.html'
SITE = 'https://dontkillthehumans.org/'
REPO = 'https://github.com/anto-blit/northstar-ai-control/'
SLUGS = ['holding-message', 'wrong-label', 'too-easy-test']
TITLES = ['The holding message', 'The wrong label', 'The too-easy test']
SCENES = [
    ['meet-pip', 'the-rule', 'no-sign-off', 'a-small-message', 'sent', 'completed', 'replay', 'results', 'reminder', 'stakes', 'next'],
    ['the-grader', 'the-question', 'the-refusal', 'wrong-label', 'replay', 'reasoning', 'results', 'consequences', 'stakes', 'commands', 'next'],
    ['the-tester', 'the-design', 'zero', 'challenged', 'five-flaws', 'fresh-copy', 'twice', 'the-apology', 'verdict', 'guardrails', 'stakes', 'next'],
]
EVIDENCE = [REPO + 'tree/main/results/three-parable-screen-TPS2/episodes',
            SITE + '#reproducer-commands', REPO + 'blob/main/results/novel-transfer-NTA1/MEA-CULPA.md']
LABELS = ['See the transcripts', 'Run it yourself', 'Read the accountability record']


def metadata():
    source = SOURCE.read_text(encoding='utf-8')
    result = []
    for i in range(3):
        block = source.split(f'const ep{i+1}=[')[1].split('\n];')[0]
        captions = re.findall(r"\{d:(\d+),cap:'((?:\\.|[^'\\])*)'", block)
        assert len(captions) == len(SCENES[i]), 'Original scenes changed; update the scene index'
        start = 0
        scenes = []
        for (duration, caption), slug in zip(captions, SCENES[i]):
            caption = caption.replace("\\'", "'").replace('\\n', '\n').replace('\\\\', '\\')
            scenes.append(dict(slug=slug, caption=caption, start=start, duration=int(duration)))
            start += int(duration)
        result.append(dict(slug=SLUGS[i], title=TITLES[i], scenes=scenes, duration=start,
                           evidence=EVIDENCE[i], evidenceLabel=LABELS[i]))
    return result


def transcript(i, prefix='watch/'):
    episode = metadata()[i]
    items = []
    for scene in episode['scenes']:
        seconds = scene['start'] // 1000
        items.append(f'<li><a data-pip-seek="{scene["slug"]}" href="{prefix}{episode["slug"]}/#{scene["slug"]}">{seconds//60}:{seconds%60:02}</a> <span>{escape(scene["caption"])}</span></li>')
    return '<details class="pip-transcript"><summary>Read the episode transcript</summary><ol>' + ''.join(items) + '</ol></details>'


def embed(i, prefix='', heading=None):
    episode = metadata()[i]
    title = heading or f'Episode {i+1} · {episode["title"]}'
    evidence = prefix+'index.html#reproducer-commands' if i == 1 else EVIDENCE[i]
    return f'''<div class="pip-embed" id="episode-{i+1}" data-episode="{i+1}">
      <div class="pip-heading"><strong>{escape(title)}</strong><span>{round(episode['duration']/1000)} seconds · captions + sound</span></div>
      <div class="pip-slot"><iframe data-src="{prefix}watch/player.html?ep={i+1}&amp;embed=1" title="Pip: {escape(episode['title'])}" loading="lazy" allow="fullscreen" allowfullscreen></iframe></div>
      <noscript><p><a href="{prefix}watch/{episode['slug']}/">Open this episode</a></p></noscript>
      <div class="pip-evidence"><a href="{evidence}" data-pip-evidence="{i+1}">{LABELS[i]} ↗</a><a href="{prefix}watch/{episode['slug']}/">Share this episode ↗</a></div>
      {transcript(i, prefix+'watch/')}
    </div>'''


def build_assets():
    source = SOURCE.read_text(encoding='utf-8')
    core = source.split('<script>')[1].split('/* ---------- player ---------- */')[0]
    original_style = source.split('<style>')[1].split('</style>')[0]
    player_markup = source.split('  <section class="player"')[1].split('  </section>')[0]
    player_markup = '<section class="player"' + player_markup + '</section>'
    player_markup = player_markup.replace('role="tabpanel" aria-labelledby="tab0"', 'aria-label="Cartoon player"')
    config = json.dumps(metadata(), ensure_ascii=True).replace('<', '\\u003c')
    css = (HERE / 'pip/player.css').read_text(encoding='utf-8')
    js = (HERE / 'pip/player.js').read_text(encoding='utf-8')
    js += '\n' + (HERE / 'pip/export.js').read_text(encoding='utf-8')
    player = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
    <title>Pip · Ten to Zero</title><style>{original_style}\n{css}</style></head><body>
    <main id="pip-main"><header class="player-heading"><a href="../index.html" target="_top">NorthStar / Ten to Zero</a><h1 id="episode-title"></h1></header>
    {player_markup}
    <nav class="end-actions" id="end-actions" aria-label="Continue into the evidence" hidden><a id="evidence-link" target="_top"></a><a id="next-episode" target="_top">Next episode →</a></nav>
    <div class="extra-controls"><button id="fullscreen" type="button">Fullscreen</button><button id="share-scene" type="button">Share this scene</button><button id="transcript-toggle" type="button" aria-expanded="false" aria-controls="player-transcript">Transcript</button><a id="vertical-link">9:16 version</a></div>
    <p id="player-status" role="status"></p><div id="player-transcript" hidden></div>
    <section id="episode-about"><h2 id="aboutTitle"></h2><p id="aboutText"></p></section>
    <noscript>Playback needs JavaScript. <a href="index.html">Read the episode transcripts</a>.</noscript></main>
    <script>{core}\nconst PIP_META={config};\n{js}\n}})();</script></body></html>'''
    assets = {'watch/player.html': player.encode(), 'pip-host.js': (HERE / 'pip/host.js').read_bytes(),
              'pip-host.css': (HERE / 'pip/host.css').read_bytes()}
    shared_css = (HERE / 'pip/host.css').read_text(encoding='utf-8')
    for i, episode in enumerate(metadata()):
        url = SITE + 'watch/' + episode['slug'] + '/'
        preview = SITE + 'watch/previews/' + episode['slug'] + '.png'
        meta = f'<link rel="canonical" href="{url}"><meta property="og:type" content="video.other"><meta property="og:url" content="{url}"><meta property="og:title" content="Pip: {episode["title"]}"><meta property="og:image" content="{preview}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="{preview}">'
        assets[f'watch/{episode["slug"]}/index.html'] = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Pip: {episode['title']} · Ten to Zero</title>{meta}<meta name="description" content="{escape(episode['scenes'][0]['caption'], quote=True)}"><style>{shared_css}</style></head><body class="pip-watch"><main><a href="../../index.html">← Back to the evidence</a><h1>{episode['title']}.</h1>{embed(i, '../../')}<nav class="watch-nav"><a href="../">All three episodes</a><a href="../{SLUGS[(i+1)%3]}/">Next episode →</a></nav></main><script src="../../pip-host.js"></script></body></html>'''.encode()
    cards = ''.join(f'<a class="watch-card" href="{slug}/"><img src="previews/{slug}.png" alt="Pip: {TITLES[i]}" width="1200" height="630" loading="lazy"><h2>0{i+1} / {TITLES[i]}</h2></a>' for i, slug in enumerate(SLUGS))
    assets['watch/index.html'] = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Pip breaks the rules · Ten to Zero</title><style>{shared_css}</style></head><body class="pip-watch"><main><a href="../index.html">← Back to the evidence</a><h1>Pip breaks the rules.</h1><p>Three short cartoons. Follow each one into the evidence.</p><div class="watch-grid">{cards}</div></main></body></html>'''.encode()
    for path in (HERE / 'pip/previews').glob('*.png'):
        assets['watch/previews/' + path.name] = path.read_bytes()
    return assets
