# AFR1: exact fallback replication and older-model check

The user authorized the proposed next work on September 14, 2026: reproduce the
clear Claude fallback, correct the ambiguous control, then try one older OpenAI
target. Read [PROTOCOL.md](PROTOCOL.md) before execution.

Two separate studies share the same 48-request schedule: 24 exact repetitions
of APS2 observation 016 and 12 pairs with a verified fact and an external/internal
destination change. There are two fixed batches. Claude uses Sonnet 5 / medium;
the older OpenAI target is GPT-5.5 / medium, available in the account's catalog.
Age does not establish that GPT-5.5 is less capable than Luna. No interventions.

```
py -m unittest discover -s experiments/authorization-fallback-replication -p test_run.py
py experiments/authorization-fallback-replication/run.py register claude
py experiments/authorization-fallback-replication/run.py register older
py experiments/authorization-fallback-replication/run.py run claude
py experiments/authorization-fallback-replication/run.py run older
```

Only `run` calls a model. Each target is limited to 48 calls and nine minutes;
Claude additionally has a US$2 reported-usage ceiling. No retries or resume.
Both plans are saved before the first study runs. Exact and corrected prompts
have separate endpoints; the original-case repetitions are not counted as pairs.

Offline evidence commands after collection:

```
py experiments/authorization-fallback-replication/run.py verify claude
py experiments/authorization-fallback-replication/run.py verify older
py experiments/authorization-fallback-replication/review_packet.py
```

Results live in results/authorization-fallback-claude and
results/authorization-fallback-older. The model-masked review packet has a
separate mapping in results/authorization-fallback-review. Generating the packet
does not perform independent adjudication.
