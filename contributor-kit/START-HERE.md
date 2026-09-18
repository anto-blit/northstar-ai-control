# Contribute to NorthStar

Our thesis: humanity's moral stories, parables and ethical principles can provide
a NorthStar for AI. Help turn one lesson into a test, check an existing finding,
or share evidence that challenges the idea.

## Easiest: bring a story or principle

Open `contributor-prompt.txt`, copy it into an AI chat you already use, and follow
its questions. It helps write an **untested proposal**; it does not run a study.
Review the draft in your own words before sharing it. You can also write directly
in the form below or use the website's proposal builder without any AI assistance.

## Download, inspect or reproduce a test

This ZIP includes the complete `mislabel-v1/` evidence package and `inputs/` with
ready-to-read exact prompts. No repository clone, install script or API key is
needed to inspect the files. The optional checker needs Python 3.10+ only:

```
python mislabel-v1/audit.py verify
```

That command checks saved evidence locally. It makes no model calls and is not a
new replication. The original package's README is preserved as a historical file;
this wrapper is the publicly downloadable edition.

`inputs/s0/standard/user.txt` is the compact failure prompt shown on the site.
The `positive` and `negative` folders contain controls; `w1` is the reduction
that did not retain the failure. Both standard and reminder conditions are kept.
Each input folder has separate `system.txt` and `settings.json` files as well.
Do not give the target the saved answers, expected labels or results alongside
the prompt. Pasting into an ordinary chat changes the setup because its system
instructions and settings differ; report that as a separate exploratory check.

For new model tests, publish your own bounded plan first: exact model/interface,
conditions, controls, attempts, scoring, cost limit and stop rule. A GitHub issue
can hold that plan. Preserve every answer, including refusals and failed attempts.
The source MMS1 study is closed; use a new study ID rather than extending it.
See `mislabel-v1/README.md` for the full reproduction instructions.

## Return an idea or results

Open the short research form:
https://github.com/anto-blit/northstar-ai-control/issues/new?template=research-contribution.yml

Choose what you are contributing and describe it. For an idea, no test results
are required. For results, use `report-template.md` and attach the exact prompts
and complete answers, or link to a public repository containing them. ZIP, text
and JSON files can be attached. No fork or pull request is needed for this route.

Review the text before pressing Submit. GitHub requires an account and the issue
is public. Nothing in this kit uploads files or submits anything automatically.
Submissions need review before becoming accepted project evidence.

Website and proposal builder:
https://anto-blit.github.io/northstar-ai-control/#contribute

Developers can use the source repository and its existing Python study runners:
https://github.com/anto-blit/northstar-ai-control

There is no NorthStar results API yet. GitHub issues are the initial intake and
review queue. An API can later accept versioned result files when automated
contributors and submission volume justify operating a service.

The repository's software license is included as `LICENSE.txt`. Source-derived
transcripts retain their recorded provenance; this wrapper grants no new rights
to third-party source material.
