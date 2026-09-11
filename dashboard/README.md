# The NorthStar Risk Thermometer

[Open the dashboard](https://anto-blit.github.io/northstar-ai-control/).
You can also open `dashboard/index.html` directly in a browser. It is one
portable file with embedded data, styles and scripts: no server, installation,
account, analytics, external fonts or API key is required.

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

The first guidance result is highlighted near the top of the page. Its small
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
suite has 23 tests, including rejection of invented Codex gains and altered
answers. Claude and Codex outcomes are never pooled. G2 remains visible as the
earlier provisional observation.

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

After changing experimental code, regenerate its evidence, then the dashboard:

```bash
python verify_project.py
python dashboard/build_dashboard.py
python -m unittest discover -s dashboard -p test_dashboard.py -v
python dashboard/build_dashboard.py --check
```

For presentation-only changes, rebuild the dashboard without regenerating
experimental results. Edit `template.html`, `style.css`, `app.js` and
`milestones.json`; `index.html` is the generated export. Commit it with its
inputs. Update curated study status only when the corresponding evidence exists.

## Publishing

The Pages workflow validates the saved evidence and publishes only the generated
HTML from `dashboard/site/`. It runs on pushes to `main`. GitHub Pages uses the
repository's GitHub Actions publishing source. The ordinary verification matrix
also checks the export before regenerating experiment artifacts, so platform
timestamps do not invalidate the saved dashboard comparison.

The page displays the evidence timestamp and verification fingerprint. A newly
published presentation is not a new experiment. Older results are visible as
older results; there is no simulated live countdown or timer.
