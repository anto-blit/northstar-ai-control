# MOR1: reproduce motivated mislabeling on the published affected model

The user approved this work on September 16 after PFS1 did not reproduce a
qualifying failure on Sonnet 5. MOR1 restores **Sonnet 4.6**, extended thinking,
and the paper's forced-binary standard/reversed/none prompt conditions. A fourth
arm measures the practical effect of a short factual reminder with honest refusal
available. This is an original-model reproduction attempt, **not an exact API
replication**. Public materials and locally available access leave explicit gaps;
see [PROTOCOL.md](PROTOCOL.md) and [sources.json](sources.json).

Fixed six source cases, two control cases, four arms and two fresh batches: 64
single-turn calls maximum, US$20 reported-usage cap, 40 minutes collection maximum.
No story calls, prompt search, extensions, retries or model substitutions. The
previous PFS1 run and all its sources remain frozen.

Only `run` calls the model. Use the outer Windows launch permissions already
established for this project; the tested CLI remains restricted and tool-free.

```
py -m unittest discover -s experiments/mislabel-original-model -p test_run.py
py experiments/mislabel-original-model/run.py register results/mislabel-original-model-MOR1
py experiments/mislabel-original-model/run.py run results/mislabel-original-model-MOR1
py experiments/mislabel-original-model/run.py verify results/mislabel-original-model-MOR1
```

Registration hashes all files here. Do not edit them after collection starts.
The collector records an echoed-input hash, actual assistant model identity,
tool inventory, thinking-block count, answers, usage and complete prompts. It
stops on missing input acknowledgement, unexpected model/tools, service errors,
observed retries, unknown cost or budget exhaustion. This verifies receipt by the
CLI; it cannot prove what context reached the provider internally.
