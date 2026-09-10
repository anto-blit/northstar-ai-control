# The NorthStar Clock

[Open the dashboard](https://anto-blit.github.io/northstar-ai-control/).
You can also open `dashboard/index.html` directly in a browser. It is one
portable file with embedded data, styles and scripts: no server, installation,
account, analytics, external fonts or API key is required.

## What the clock means

The founder chose **10.00% as an assumed starting point** and zero as an
aspiration. This is not a measured baseline or a current estimate of AI-caused
human extinction. There is no calibrated event horizon or aggregate impact
model. Current risk and quantified reduction remain explicitly unknown.

Passing tests, milestones and simulated prevention rates never subtract from
that baseline. The dashboard separately shows research progress: recorded
checks, executed analyses, prepared studies and work still ahead. Its monitor
slider selects declared detector error rates from an experiment; it does not
adjust humanity-wide risk.

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
