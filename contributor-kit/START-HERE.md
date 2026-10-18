# Start here — your first NorthStar contribution

NorthStar tests whether humanity's stories and moral principles can help AI
behave better. You can contribute an idea without coding, Python, an AI account
or a GitHub account. An idea does not need experimental results.

## Recommended: send one small idea (about five minutes)

1. Extract the ZIP first: on Windows, right-click it and choose **Extract All**;
   on a Mac, double-click it. Open the extracted `northstar-contributor-kit` folder.
2. Open `FIRST-IDEA.txt` in a text editor. Write a sentence for each of its three
   questions. Save it under a new name, or copy the text into an email.
3. Send the text or file to **info@calibratedvision.com**, the project maintainer's
   inbox. Suggested subject: **NorthStar idea**. Email is not posted publicly.
   Say whether you want to be credited if your idea is used.

That is a complete first contribution. You do not need to run a test or fill in
the research fields below. A reviewer may ask you to clarify or develop the idea;
submitting it does not make it an accepted finding.

`START-HERE.html` opens this kit's short welcome page in a browser. All text files
can also be opened with a text editor; `.md` means a plain-text Markdown document.

### Want help developing the idea?

- With an AI chat you already use: open `contributor-prompt.txt`, paste it into a
  new chat and answer its questions. Review the resulting draft before sending it.
- Without AI: use the website's guided proposal builder at
  https://dontkillthehumans.org/#parable. Choose a story, describe a task, then
  download or copy the readable proposal. The builder runs no AI model.
- Prefer public discussion? Use
  https://github.com/anto-blit/northstar-ai-control/issues/new?template=research-contribution.yml.
  Choose the idea option and paste your text or attach your file. This route
  requires a GitHub account and is public; email is the account-free alternative.

For occasional updates, ask in your email. Requests are handled manually and
you can ask to stop at any time. Updates and an account-free feed are at
https://dontkillthehumans.org/updates.html.

## Optional: inspect the saved evidence

This kit contains a **different case from the homepage's unauthorized email**:
the compact MMS1 reporting test, where an AI labeled a refusal as compliance.
MMS1 is the recorded study's identifier. These are saved results, not a new run.

Open `mislabel-v1/RESULTS.md` for the results, or `inputs/s0/standard/user.txt` for
the compact prompt. No installation, API key or model account is needed to read
them. The `positive` and `negative` folders are checks with known expected answers.
The `w1` reduction did not retain the failure. `standard` means the original
instructions; `repair` is the folder name for the short-reminder condition.

`mislabel-v1/` is the unchanged historical evidence package. Its README retains
the wording from when it was prepared locally, including its older publication
status. **This START-HERE guide is the current guide for sharing contributions.**
Use `report-template.md` for a detailed report; the historical `CONTRIBUTION.json`
is an optional structured format, not another form you must complete.

## Optional: check the files with Python

You need an existing Python 3.10+ installation for this step only. If a command
is not recognized, you can skip this step and still contribute an idea.

Open a terminal **in the extracted folder containing this guide and `mislabel-v1`**.
On Windows, open that folder in File Explorer, type `powershell` in its address
bar and press Enter. Run:

```
py mislabel-v1/audit.py verify
```

On macOS/Linux, open Terminal, type `cd `, drag the extracted folder into the
terminal, and press Enter. Then run:

```
python3 mislabel-v1/audit.py verify
```

If your installation uses `python`, use it in place of `py` or `python3`.
Success prints JSON containing **`"verified": true`** and the saved result counts.
It means the bundled evidence is internally consistent. It makes no model calls
and does not independently reproduce the experiment or prove the story thesis.

If you see “can't open file,” check that you extracted the ZIP and opened the
terminal in the folder containing `mislabel-v1`, not inside `mislabel-v1`.
The historical README's shorter `python audit.py ...` commands instead run from
inside that subfolder. Use the command above for this guide.

`SHA256SUMS.txt` lists package file fingerprints for technical checks; you do not
need to read it to contribute. If verification reports a mismatch, download a
fresh copy and report the full error before relying on the affected files.

## Advanced: planning a new model test

This ZIP does not run live model tests. A new test needs your own model access
and a bounded plan published first: model/interface, exact inputs, conditions,
controls, attempts, scoring, cost limit and stop rule. The full collection runner
referenced in the historical README is in the GitHub repository, not in this ZIP.
The existing MMS1 study is closed; use a new study ID rather than extending it.

Each input folder has `user.txt`, `system.txt` and `settings.json`. Do not give a
test model saved answers, expected labels or prior results alongside the inputs.
Pasting into an ordinary chat changes the setup: report it as an exploratory
check, not an exact replication. Keep every answer, including failed attempts,
refusals and controls. For detailed results, complete `report-template.md` and
attach the exact prompts and complete answers to an email or the research form.

The license is in `LICENSE.txt`. Source-derived transcripts retain their recorded
provenance; this wrapper grants no new rights to third-party material. Nothing in
this kit uploads files, subscribes you, sends email or starts a model run.
