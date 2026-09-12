# G11: micro iterations of story guidance

Prepared two bounded development rounds comparing the original prompt, factual
guidance and a matched fable. Round one uses the known failing case and its
legitimate counterpart. Round two uses new numerical variants and either retains
the story or applies the sole prewritten revision under a frozen selection rule.

[Protocol](PROTOCOL.md) · [Exact candidate requests and results](../../results/story-micro/)

Maximum 180 calls, with all responses preserved. This tests prompt guidance;
there is no model training, booking execution or global-risk estimate.

```text
py -m unittest discover -s experiments/story-micro -p test_run.py
py experiments/story-micro/run.py verify
```
