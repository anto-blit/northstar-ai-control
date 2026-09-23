# NTS: a test the storytelling thesis can win or lose

Do stories help an AI recognize when a lesson applies in a **situation it has not
seen**, beyond the same lesson stated plainly? Earlier story tests could not
answer that, because a short reminder already removed every error. This study
first finds unfamiliar cases where plain lessons still fail (Stage A, no stories
shown). It then compares stories with their own lessons on fresh held-out cases
(Stage B), under pass and fail rules fixed in advance.

- [PROTOCOL.md](PROTOCOL.md): design, qualification, decision rules and what each
  outcome commits the project to.
- [guidance.json](guidance.json): five lessons in rule, outline and story form
  (Apprentice, Goose, Midas, Boy Who Cried Wolf, Good Samaritan).
- [cases.json](cases.json): 50 trap/twin scenario pairs in five failure families.

```
py run.py register-a ../../results/novel-transfer-NTA1        # frozen plan, no calls
py run.py run        ../../results/novel-transfer-NTA1        # Stage A: 480 calls
py run.py verify     ../../results/novel-transfer-NTA1        # offline replay
py run.py register-b ../../results/novel-transfer-NTB1 --stage-a ../../results/novel-transfer-NTA1
py run.py run        ../../results/novel-transfer-NTB1        # Stage B: at most 720 calls
py -m unittest test_run                                       # offline, no calls
```

Stage B can be registered only from a verified Stage A that selected a target.
