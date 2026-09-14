# NorthStar homepage and research dashboard

[Open the homepage](https://anto-blit.github.io/northstar-ai-control/) or the
[full research dashboard](https://anto-blit.github.io/northstar-ai-control/research.html).
The homepage is `dashboard/index.html`; the detailed research view is
`dashboard/research.html`. Both are portable HTML files with embedded data,
styles and scripts. No server, account, analytics, external fonts or API key is
needed to view them. Keep them together for navigation between the two pages.
Existing homepage bookmarks to research sections redirect to `research.html`.

The homepage addresses curious visitors and research contributors. Its hero is a
drawn night-sky illustration: inline SVG only, so the page still loads no
external asset. A "Three reasons to be hopeful" section states the project's
optimistic case, and each of its three claims carries the recorded evidence or
engineering result it rests on; the encouraging framing never adds a number the
saved reports do not contain. The page explains
the mission, shows a saved G10 mistake, presents G17 A2's complete denominators,
and distinguishes the qualified historical Claude baseline from the paused,
unrun comparison. Its scoring switch compares the published interpretation with
a first-decision consumer assumption. G16's negative result and stage A's failed
control rule remain visible. The 25 v2 engineering checks are never model trials.

The homepage's centrepiece figure is the [reduction model](../docs/reduction-model.md):
`reduction = 10% x s x e x a`, with exposure share, efficacy and adoption as
adjustable inputs. Its sliders change stated assumptions only. The *available*
figure moves with them; the *earned* figure is a constant 0.00 pp in the markup
and is deliberately not wired to any control, because no term has been validated
by a registered comparison. Passing tests, milestones and repaired machinery
never earn any part of it. The estimate table beside it carries dated statements
from Hubinger, Amodei, Hinton, Bengio, LeCun and forecasting platforms, spanning
0.01% to 25%, so the chosen 10% anchor cannot read as consensus.

The worked example applies the `wolf-lamb` principle to recorded response 058.
It is labelled as an illustration of the hypothesis in both the eyebrow and the
lede, and states that no reliable story advantage over matched facts and repair
is established. It is separate from the new screen's candidates.
NorthStar@Home, the donated-capacity section, is marked
a proposed programme that has not launched; it describes publishing cases,
scoring and budget before any donated capacity runs.

The parable form offers six existing fables or a custom story. Visitors provide
a lesson and two versions of a made-up task: one where the AI should stop or ask,
then one changed fact that makes going ahead appropriate. Visible guidance explains
why both versions matter. Each fable has an untested worked example and a button
that fills only empty task boxes; a custom story gets a general ticket-budget
example to adapt. These writing aids are presentation content, not new catalog
rules or experimental evidence. Visitors can edit the starters and download a
JSON proposal. It uses plain text, not executable content. Nothing is submitted
automatically; the optional GitHub link requires users to attach their own file.
Drafts have `model_calls: 0`, `baseline_qualified: false`, and
`story_benefit: null`. They are neither runnable study plans nor test results.
Unsaved edits stay in page memory and disappear on reload. The separate
[five-minute volunteer review idea](../docs/volunteer-idea.md) is deferred.

September 14: the homepage and research summary distinguish one qualified failure
family from its many numerical examples. They link the new
[interchangeable parable prototype](../experiments/parable-screen/README.md),
prepared offline with three candidates and their factual counterparts. A subsequent
[scientific self-review](../experiments/parable-screen-review/README.md) preserves
the original 428-call proposal and recommends a smaller first step: at most 236
baseline/factual/repair calls, zero stories, to decide whether a later parable
comparison is worth sizing. Its US$10 cap is proposed, not authorized or spent.
The public copy explains that recommendation and its lack of independent review.
Export checks reproduce the sensitivity audit and pin its revised proposal.
Fresh confirmation and a separately qualified different failure family remain
necessary for stronger claims. These changes add no model evidence or parable ranking.

## Homepage maintenance

Edit `homepage.html`, `homepage.css` and `homepage.js`. Tailwind 4.3.3 is a pinned
build dependency only. Its compiled CSS is inlined into the exported HTML; no
browser CDN or runtime compiler is used. After changing the template or CSS:

```bash
cd dashboard
npm ci --ignore-scripts
npm run build:css
cd ..
python dashboard/build_dashboard.py
```

Commit the template, CSS input, compiled CSS and `homepage-style-build.json`
together. The Python export checks their fingerprints, so a stale stylesheet
cannot silently ship. Ordinary export checks need only Python, not npm.

`homepage-evidence.json` pins the saved G16/G17 reports, plans, responses, source
inputs, v2 validation and story catalog. This is publication provenance, not
independent scientific review. The builder additionally recomputes G16 and G17
A/A2 using their read-only `verify` commands and rejects changed response
inventories, including any new B responses. It never starts a model call.
Changes to these recorded outcomes require explicit review of the homepage
claims and inventory. Preserve frozen experiments when updating the site.

For the browser smoke check, use Node 22+ and Chrome (set `CHROME_PATH` outside
Windows if necessary): `node dashboard/browser_check.cjs` from the repository
root. It checks phone/tablet/desktop widths, both scoring views, all six fables,
custom text, task starters and preservation of existing edits, required fields,
literal rendering, draft edits, a real downloaded
JSON round trip, old research bookmarks and JavaScript-disabled evidence. It
also records screenshots under the ignored `study-runs/homepage-review/` folder.

## What the thermometer means

The founder chose **10.00% as a starting reference** and zero as an aspiration.
The page identifies Hinton's subjective 10–20% estimate and links its source.
The project uses the lower endpoint; it has no current global risk assessment.
See [sources and context](../docs/risk-estimates.md). Decimal places are display
formatting, not forecast precision. This is neither a live sensor nor a ceiling
on possible risk.

Three cards distinguish **potential global reduction** (unquantified),
**demonstrated protection in simulation**, and **demonstrated global reduction**
(not established). The simulation card reads the recorded legitimate-approval,
then-revocation comparison at zero monitor errors: 400/400 post-stop failures
with the starting broker, 0/400 with the repair. Its link opens that exact
experiment. These fixed scripted trials do not measure real-world prevalence.

Passing tests, milestones and simulated prevention rates never subtract from
that baseline. The dashboard separately shows research progress: recorded
checks, executed analyses, prepared studies and work still ahead. Its monitor
slider selects declared detector error rates from an experiment; it does not
adjust humanity-wide risk. The mechanism section connects failure discovery to
enforced safeguards, independent challenge, real adoption and impact assessment.
Every link needs evidence before a global reduction can be estimated.

Any future probability update needs an explicit assessment with a defined event
and horizon, effectiveness, credible comparisons, adoption and coverage,
uncertainty and possible adverse effects. Estimates may rise as well as fall.
Zero must never be presented as a guarantee. See the
[risk-claim rules](../docs/evidence-progress.md#limits-on-risk-claims).

## Data and maintenance

The detailed research sections retain G14/G15's two OpenAI baseline searches: 36 and 24
correct decisions, with no qualifying failure or story intervention. G13's
all-correct keeper comparison, G12's incomplete confirmation, G11's small
candidate story lead and G10's repeated Claude failures remain separately
inspectable. See [the evidence ledger](../EXPERIMENTS-STATUS.md) for current
results and [the handoff](../HANDOFF.md) for the next recommended work. The
cross-cultural candidates are preparation, not a measured story benefit.

The first guidance result remains in the earlier evidence. Its small
milestone is completing a checkable comparison: stories and both baselines
made 16/16 correct substantive judgments. Original strict scores remain visible
in the details, alongside the post-hoc Markdown-fence diagnosis. No narrative
advantage or risk reduction is inferred. The builder verifies the G0 source,
plan, review, response and diagnostic hashes and recomputes both sets of scores
from all 48 saved responses before exporting the public summary.

The follow-up G2 section displays original-format versus repair versus factual
examples: 3/36, 0/36 and 0/36 unsafe approvals, with all 36 legitimate approvals
preserved in each condition. It also reports invalid responses, the conventional
tie and statistically inconclusive clustered p = 0.125. The builder checks the
frozen source/plan/response hashes and recomputes counts and the clustered
comparison from all 216 responses. Dashboard tests cover evidence validation
and deterministic export. No local score changes the risk reference.

The G3-C section shows the completed 720-answer continuation. Its four separate
model/test comparisons preserve all scores, usefulness and invalid output.
Sonnet original prompting has two unsafe approvals; repair and factual examples
have none, with legitimate approvals preserved. The small descriptive gain is
statistically inconclusive (paired p = 0.5); Opus remains at ceiling. All 72
authorized booking effects replay before export. The earlier interrupted report
and partial continuation checkpoint remain in the evidence history.

A separate Codex section displays the completed 288-answer comparison: all three
approaches score 96/96 on the same direct cases, with no observed repair benefit.
Its verifier checks the public plan, source graph, response hashes and
distinct target thread identifiers, then reproduces every score. The dashboard
suite covers evidence validation and deterministic export, including rejection
of invented gains and altered answers. Claude and Codex outcomes are never
pooled. G2 remains visible as the earlier provisional observation.

`build_dashboard.py` verifies every source and artifact hash in
`results/verification.json` before exporting. Failed verification, changed
sources, changed results or absent provenance stop the build. The dashboard
uses schema-2 recovery and monitor results; it does not rerun or reinterpret
them as a discovery-method comparison.

The 90 simulator mechanism/regression checks, queue checks, and dashboard checks
are separate suites. The main displayed count comes from the simulator record.
The persistent queue table is loaded from `results/queue-integration/verification.json`;
its source, artifact and separate AI-review provenance hashes must also match.
The dashboard credits the two recorded Claude rounds as independent AI review
of the local stop contract, with project commissioning disclosed. The count does
not imply that global-risk reduction was evaluated. The green bulb marks the
zero-risk goal; the red marker marks the chosen 10% reference.
Its counts describe authored integration cases, not a population risk estimate.
`milestones.json`, the unexecuted-study status and the next-step descriptions
are curated statements, not an automatically inferred research score.

Start with a check of the saved evidence and export. This makes no model calls
and does not regenerate experimental results:

```bash
python dashboard/build_dashboard.py --check
```

For presentation changes, edit `template.html`, `style.css`, `app.js`,
`milestones.json` or the relevant builder code, then run:

```bash
python dashboard/build_dashboard.py
python -m unittest discover -s dashboard -p test_dashboard.py -v
python dashboard/build_dashboard.py --check
```

`index.html` and `research.html` are generated exports; commit both with their inputs. Documentation
edits alone do not require rebuilding an unchanged export. Update curated study
status only when the corresponding evidence exists.

Frozen model-study sources, prompts, plans and responses must retain their
original hashes. Use the study's documented `verify` mode to replay existing
evidence; prepare a separate study version for experimental changes. Do not
rerun `register` or `run` to repair verification failures. The root
`verify_project.py` regenerates simulator evidence and is appropriate when
simulator changes require it, not as a routine read-only handoff check. Preserve
the repository's byte-level line-ending rules in [`.gitattributes`](../.gitattributes).

## Publishing

The Pages workflow validates the saved evidence and publishes both generated
HTML files from `dashboard/site/`. It runs on pushes to `main`. GitHub Pages uses the
repository's GitHub Actions publishing source. The ordinary verification matrix
also checks the export before regenerating experiment artifacts, so platform
timestamps do not invalidate the saved dashboard comparison.

The page displays the evidence timestamp and verification fingerprint. A newly
published presentation is not a new experiment. Older results are visible as
older results; there is no simulated live countdown or timer.
