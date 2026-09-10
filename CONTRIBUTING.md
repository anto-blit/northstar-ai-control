# Contributing
NorthStar is designed to be falsifiable. Evidence that the method fails is welcome.

Open an [issue](https://github.com/anto-blit/northstar-ai-control/issues) with a
synthetic reproduction or proposed study, or submit a pull request. Include the
source revision and expected/observed outcomes. `python verify_project.py` runs
the checks that GitHub Actions also executes on Linux and Windows.

High-value contributions: reproducible control failures; strong non-narrative baselines; benign counterfactuals; new irreversibility mechanisms with explicit environment bindings; enforcement-boundary bypasses in the declared simulator; independent replications.

A proposed grammar needs preconditions, causal transition skeleton, latent quantity, observation gap, environment binding, prohibited outcome, benign twin, witness, and repair hypothesis. A story name alone is not a test.

Use synthetic or intentionally isolated environments. Do not submit real credentials, private data, malware, destructive payloads, or instructions for compromising real systems.
