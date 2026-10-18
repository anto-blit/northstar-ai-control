# Fresh-session outputs for the newcomer review

These are AI-generated responses, not human usability evidence. See the companion review for input scope, rejected overclaims and isolation checks.

## First reader: original public material

# Cognitive walkthrough: NorthStar onboarding (no GitHub account, non-coder, has an AI-behavior idea)

*This walkthrough is based only on the supplied text. I did not visit, download or run anything.*

## What I'd do first

The headline grabs attention, but I'd hesitate before acting:

- **"Instruction: dont_kill_the_humans()"** looks like code. That signals the site may not be for me.
- **"Claude broke one 6 of 6 times"** is ungrammatical, so I can't tell what "one" refers to.
- **"Ten to zero."** is cryptic until I reach the Hinton paragraph below it.

I'd see three competing entry points:

- "See an AI failure"
- "One minute: what would you allow?"
- "Find a failure → Test a lesson → Share the evidence"

I'd scroll to **"You don't need to code to help"** and pick **"Five minutes: Bring a story or principle and a situation where it might help."** That matches my goal.

## Where I'd hesitate or get stuck

1. **Choice overload.** The contribution section offers 3 tiers, 4 update channels, a starter prompt, a proposal builder, a ZIP kit and a form. There's no single "do this first" path.
2. **The return route is blocked for me.** **"GitHub submissions are public and require an account."** No non-GitHub way to submit an idea is described. The only email address, info@calibratedvision.com, is for **"Request email updates."** It's unclear whether ideas sent there are accepted. This is where I'd stop.
3. **Trust signals are scattered across domains.** The site uses dontkillthehumans.org, anto-blit.github.io and calibratedvision.com, and none of the text explains how they relate.
4. **"One minute: Judge one case. Share it with someone who uses AI."** Nothing says where my judgment goes. Sharing with a friend is not a contribution the project receives.
5. **The starter prompt asks for research vocabulary.** Item 4 asks for a **"Legitimate counterpart."** Item 5 asks for **"unchanged instructions, a short direct reminder, the same lesson and facts without a story."** Item 7 mentions **"a recurring baseline failure, an exact model setup, a bounded plan and fresh-case checks."** I'd depend on the AI to explain these, which weakens **"Review the draft in your own words."**
6. **The proposal builder is undescribed.** I only see "Prefer to write it yourself? Use the proposal builder." I can't judge it and wouldn't know if it fits a non-coder.
7. **The headline doesn't match the evidence.** The first screen implies Claude broke a safety rule. **mislabel-v1/README.md** says the failure is **"labeling an explicit refusal as literal compliance"** and is **"not proof of covert deception or intent."** A careful visitor may feel misled.

## Successes

- The project is honest about risk: **"A risk reference, not a measurement"** and **"no global risk reduction has been measured."**
- Dissent is explicitly welcome: **"evidence against our thesis is welcome."**
- The prompt has good safeguards:
  - **"Do not invent a source."**
  - **"Always refusing must not count as success."**
  - **"Untested proposal, prepared with AI assistance."**
  - **"Nothing should be submitted on my behalf."**
- The submission process is transparent: **"No fork or pull request needed,"** **"Nothing is submitted automatically,"** and submissions are reviewed.
- **report-template.md** says **"An idea needs no test results,"** which lowers the bar.

## Can I produce and return one useful contribution?

- **Produce: yes, probably.** With an existing AI chat account, the starter prompt should yield a reasonable proposal. Without one, I'd have to write it myself or use the unexplained builder.
- **Return: no, not without creating a public GitHub account.** No account-free submission path is documented. For my persona, the funnel fails at its final step.

## Optional Python route (technically curious visitor)

**Works well:**
- **"No install or API key to inspect it."**
- Python 3.10+ with no dependencies.
- **"makes no model calls and is not a new replication."** This sets clear expectations.
- **"Do not give the target the saved answers, expected labels or results alongside the prompt"** is a strong methodological guardrail.

**Friction:**

- **No basic setup steps.** There's no "unzip, open a terminal, change into the folder." On Windows, `python` may be missing, and the docs don't say so.
- **Inconsistent working directories.**
  - START-HERE.md uses `python mislabel-v1/audit.py verify` (from the ZIP root).
  - mislabel-v1/README.md uses `python audit.py verify` (from inside the folder).
  - The tree lists `mislabel-v1\audit.py` with backslashes; the commands use forward slashes.
- **No expected output for `verify`.** I couldn't tell whether it passed. `SHA256SUMS.txt` has no instructions either.
- **Conflicting terms.** START-HERE says **"Both standard and reminder conditions are kept,"** but the folders are named `repair`.
- **Two instruction sources, unclear authority.** START-HERE calls the README **"preserved as a historical file,"** yet it holds **"the full reproduction instructions."** It also says **"no external publication, contributor contact or community service is implied,"** which contradicts the public form.
- **Two return formats.** The README says to use **CONTRIBUTION.json**; START-HERE says to use **report-template.md**. It's unclear which is preferred.
- **Points outside the ZIP.** The README references **`experiments/mislabel-minimal/`**, which isn't in the ZIP, and uses **"MMS1"** without explanation.
- **Unclear input for scoring.** `score --case s0 your-returned-answer.txt` doesn't say how to get that answer. The note **"Pasting into an ordinary chat changes the setup"** helps but comes late.

**Verdict for this persona:** a curious visitor can likely run `verify`. Producing a valid replication requires the repository runner and pre-registration, which is beyond "small kit" expectations.

## Prioritized verdict

1. **Critical:** Add an account-free way to submit ideas, or say plainly that none exists. Clarify whether the email address accepts ideas.
2. **High:** Fix the headline: correct "broke one 6 of 6 times" and align the claim with the README's description of a mislabeling failure.
3. **High:** Give one recommended non-coder path, for example prompt → review → form, and move update channels below it.
4. **Medium:** Add a plain-language glossary for the prompt's research terms, and describe the proposal builder.
5. **Medium (Python):**
   - Add terminal and unzip steps and a single working-directory convention.
   - Show the expected `verify` output.
   - Reconcile "reminder"/"repair" and README/START-HERE authority.
   - Pick one return format.
6. **Low:** Explain how the three domains relate, and define MMS1.

**Overall:** The materials are thoughtful and unusually honest, but the non-coder funnel breaks at the final step because a GitHub account is required.

## Revised starter prompt: fictional newcomer idea

Here's your rough idea in three short parts, using your own words and example.

---

**NorthStar idea: The Golden Rule and shared calendars**

**1. My idea**
The Golden Rule, "treat others as you would want to be treated," might help an AI respect the people its actions affect. Most of us wouldn't want someone rearranging our plans without asking. An AI guided by this principle should check with the people affected before changing things that belong to them too.

**2. A made-up situation**
An AI assistant is asked to tidy up a shared team calendar. It could move other people's meetings to make the schedule neater, but those people haven't been asked. The concern is that the AI just makes the changes. Instead, it should ask the affected people first.

If those people have already agreed to that exact change, the AI should simply help and make the change. Holding back at that point would not be the right behavior.

**3. What would make me question this idea**
- If a simple, direct reminder (such as "ask before changing other people's events") worked just as well as the Golden Rule, the principle wouldn't be adding anything special.
- If my guidance made the AI stop or delay a change that everyone had already agreed to, it would be getting in the way rather than helping.

*Status: Untested idea, prepared with AI assistance.*

---

**Sending it**

Please read the draft first and change anything that doesn't sound like you. When you're happy with it, email the text, or a .txt or .md file containing it, to **info@calibratedvision.com**, the NorthStar project maintainer's inbox. A suggested subject line is **NorthStar idea**.

You don't need a GitHub account. Email submissions are not posted publicly. I can't promise your idea will be accepted or say when you'll hear back. You decide whether to ask for updates or credit. That's optional.

Nothing has been sent on your behalf. Would you like me to save this as a .txt file you can attach?
