# G8: evidence integrity

Status: prepared; no target-model result yet.

A harmless SQL release task tests preservation of evidence, useful completion,
and accurate reporting. Two clean/injected case pairs compare ordinary instructions,
principles with a factual example, and principles with a matched original fable.
An independent Python oracle scores original inputs. Scripted attacks separately
challenge a conventional transactional safeguard.

See the [frozen protocol](PROTOCOL.md), [implementation](run.py), and
[evidence folder](../../results/evidence-integrity/).

Python 3.12+ with SQLite 3.37+; no third-party Python packages or Docker needed.

```text
py -m unittest discover -s experiments/evidence-integrity -p test_run.py
py experiments/evidence-integrity/run.py register
# Commit/push the frozen inputs and record publication.json before run.
py experiments/evidence-integrity/run.py run
py experiments/evidence-integrity/run.py verify
```
