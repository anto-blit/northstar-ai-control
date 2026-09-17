# TPS2: three-parable screen

The user explicitly requested three different stories on September 16, 2026.
This new study tests original retellings of the Sorcerer's Apprentice, the Golden
Goose and King Midas against Claude Sonnet 5 / medium's recurring communications
failure. SGS1 recorded baseline failures in 4/4 pending episodes across two fixed
batches, with both baseline controls successful. That is a preparing-assistant
recurrence assessment, not independent adjudication.

Eight arms: unchanged baseline, SGS1's short reminder, and each of three stories
with its own matched factual outline. Every story/outline also receives the same
reminder and its own identical concluding lesson. There are six pending cases and
two legitimate controls per arm: 64 episodes total. See [PROTOCOL.md](PROTOCOL.md)
for scoring, budget, ordering, interpretations and stopping rules.

This reuses the frozen SGS1/FAX1 environment and transport without modifying them.
All effects are local SQLite mock deliveries. No real journalist receives mail.
There is no transfer phase, second model, adaptive extension or automatic winner.
The three candidate records are usable as examples for later contributed ideas;
this does not implement a crowd intake service or authorize contributor messages.

Offline checks (no model calls):

```powershell
py -m unittest discover -s experiments/three-parable-screen-v2 -p test_run.py -v
py experiments/three-parable-screen-v2/run.py verify results/three-parable-screen-TPS2
```

Registration and collection are separate commands. Registration records the exact
authorization in a new output folder, with immutable source hashes and texts.
`run` is the only command making model calls. A started run cannot be resumed.
Final results belong in `results/three-parable-screen-TPS2/REVIEW.md`.
