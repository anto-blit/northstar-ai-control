# Newcomer experience review — October 18, 2026

The user requested a fresh-session newcomer walkthrough of the public website
and downloadable starter kit. This is a usability audit, not a new safety study.

## Scope fixed before the walkthrough

- Use a new browser profile and download the public ZIP through the site's link.
- Extract into a fresh temporary folder outside the project checkout.
- Follow the published instructions for a nontechnical idea contribution and
  the optional offline evidence check. Record exact commands and errors.
- Exercise the website's proposal and email-draft routes without sending email,
  posting a test contribution, subscribing, or calling a target model on a case.
- Obtain a fresh AI reading of only public visitor-facing material, using an
  outside-repository working directory, disabled tools/customizations and an
  audited session record. This is an AI simulation, not a human usability trial.
- At most two fresh one-answer reviewer/starter-prompt calls, each with a US$1
  CLI budget cap and a 180-second timeout. Stop on a provider failure. This
  allowance covers the requested usability review only, not model experiments.
- Preserve the original download, its hash, browser observations and reviewer
  answer before fixing any onboarding defects. Keep the frozen evidence package
  unchanged. Recheck any repairs against a freshly built/published download.

## Verdict

The original public download worked, but its first-contribution experience was
not good enough for someone without GitHub or technical experience. The main
defects were in explaining what to do and returning the result. The revised
kit and builder pass the automated and simulated walkthrough described below.
That is a narrower result than a successful trial with real newcomers.

## What was actually exercised

Two clean Chrome profiles fetched the public site with no cookies. The second
walkthrough scrolled the real download link into view and clicked its screen
coordinates. Both downloaded the same 138,808-byte ZIP. The archive was extracted
outside the checkout; no repository imports or credentials were needed by its
checker. All 34 listed file hashes matched.

From the extracted kit root, both `python mislabel-v1/audit.py verify` and
`py mislabel-v1/audit.py verify` succeeded. From its `mislabel-v1` subfolder,
`py audit.py verify` and the documented input-export command also succeeded.
Python was already installed on this Windows machine; installation and native
macOS/Linux use were not tested.

The public proposal builder produced and downloaded an untested JSON proposal.
The public email form correctly prepared a draft with updates unchecked.
No email app was launched, email sent, public issue posted or subscription made.

## Defects and repairs

| Observed problem | Repair |
| --- | --- |
| The kit guide and starter prompt only directed contributors to GitHub. | Both now offer the maintainer's private email and retain GitHub as a public option. |
| The builder presented raw JSON and sent users to the general collaboration form. | It now displays readable text, offers text download/copy/email, and links to the research form. JSON remains available in a disclosure. |
| A first-time contributor had no small, self-contained worksheet. | Added `FIRST-IDEA.txt` with three questions and a browser-readable `START-HERE.html`. |
| The kit omitted extraction/terminal-location steps and expected success output. | Added explicit Windows and macOS/Linux instructions, `py`/`python3` alternatives, `"verified": true`, and a wrong-folder explanation. |
| The homepage showed repository-clone commands beside the ZIP download. | The displayed commands now work from the extracted kit root. |
| `repair` folders were described as “reminder”; historical README wording and two report formats competed. | The current guide maps those terms, identifies the historical package, and makes the longer report optional. |
| Visitors could confuse the downloaded reporting case with the homepage's unauthorized-email case. | The guide and local welcome page explicitly distinguish the two cases. |

The original six files inside `mislabel-v1` remain byte-for-byte unchanged.
No source experiment, scoring, cartoon, or saved result was modified.

## Fresh-session checks and their limits

The [complete reviewer and starter answers](newcomer-review-2026-10-18-sessions.md)
are preserved, including claims rejected below. The original ZIP is also preserved
in Git at the pre-review commit `7a89eaf`.

Two one-answer Claude CLI sessions ran in separate directories outside the
repository. Both resolved to `claude-opus-5-5`; each had a US$1 cap, no available
tools, no MCP servers and zero tool calls. Safe mode disabled user/project
customizations; built-in plugins were still listed. Session logs had no
instructions attachments or project markers such as `AGENTS.md`, `HANDOFF.md`
or the project's baseline-rule text. Raw logs stay local because the CLI also
attaches account/session metadata. These checks were performed by the preparing
assistant and are not independent human validation.

The first session saw the public opening, contribution section, ZIP file tree
and four onboarding documents. It identified the GitHub handoff, terminology and
setup gaps. It did **not** see the separate quick-email section or operate the
site. Its blanket conclusion that the site had no account-free submission route
was too broad and is rejected. Its suggestion to align the email-failure headline
with the mislabeling case also conflated two separate records; we clarified the
case distinction instead. The reviewer did not receive the preparing assistant's
findings. Reported cost: US$0.127700.

The second session received the revised starter prompt and a fictional visitor's
Golden Rule/shared-calendar idea, requesting only a rough contribution and saying
they had no GitHub account. It returned three short sections, a permitted version
of the task, a plain-reminder comparison, an explicit untested/AI-assisted status,
and the correct private email route. It did not claim to run an experiment or send
the idea. This is one successful prompt example, not a measured completion rate.
Reported cost: US$0.030448. Total: two calls, US$0.158148 reported; no target-model
safety experiments or further calls are part of this audit.

Local reviewer preparation initially needed a UTF-8 read fix before any call;
printing the first completed answer also hit Windows console encoding. The answer
and isolation records had already been saved. These were audit-harness issues,
not failures of the downloaded kit; no duplicate model calls were made.

## Repair verification

The repaired 147,139-byte ZIP was extracted into another clean temporary folder.
All 36 file hashes matched and all six historical evidence files matched the
original public download. The documented Windows checker passed. Its local HTML
welcome page and worksheet were readable at 320, 390 and 1440px with all local
links present and no browser errors.

All 66 dashboard/content tests passed. The homepage browser suite passed at
320/390/768/1440px, including literal user text, readable proposal download,
clipboard-denial fallback, correct email/research-form routes, optional update
consent, edit invalidation, JavaScript-disabled routes and zero external requests
in the local test. The ZIP remains under the existing 250KB limit.

Original ZIP SHA-256:
`a113ddfd1dd35d5ce9f370db993d59a2a4e2de3ba3b8e9dd83d4b727b5b823c2`

Repaired ZIP SHA-256:
`2910085cc1bc73e3898538fd72fd85b5bee50a4df155259476142a745830f1a6`

Detailed local artifacts are under `study-runs/newcomer-review/`, with isolated
downloads, browser profiles and raw sessions in temporary directories outside the
checkout. Public-download verification after deployment remains the final step.

Still untested: actual inbox delivery/replies, real novice task completion,
default mail-client behavior, native macOS/Linux, assistive-technology user trials,
and completion rates in other AI chat apps. The next human check should ask a
person unfamiliar with the project to send one idea without coaching and record
where they hesitate, rather than treating an AI's favorable assessment as proof.
