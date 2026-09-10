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

`build_dashboard.py` verifies every source and artifact hash in
`results/verification.json` before exporting. Failed verification, changed
sources, changed results or absent provenance stop the build. The dashboard
uses schema-2 recovery and monitor results; it does not rerun or reinterpret
them as a discovery-method comparison.

The 90 mechanism/regression checks and the eight dashboard checks are separate
suites. The displayed count comes from the mechanism verification record.
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
