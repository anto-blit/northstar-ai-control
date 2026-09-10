# Related work and claim boundaries

Targeted source review: September 9, 2026. This is a starting bibliography, not a
systematic novelty review. NorthStar proposes story-based ethical guidance,
narrative-organized behavioral contrasts, and search guidance within existing
alignment, evaluation and control research. It does not claim to invent
principle-based guidance, moral evaluation, or control evaluation.

| Primary source | Why it matters for NorthStar |
|---|---|
| [Bai et al., Constitutional AI (2022)](https://www.anthropic.com/research/constitutional-ai-harmlessness-from-ai-feedback) | Principles inform a training procedure with reported behavioral improvements. Ethical guidance is testable; this does not establish a benefit from stories or validate NorthStar's proposed prompt comparison. |
| [Shah et al., Goal Misgeneralization (2022)](https://arxiv.org/abs/2210.01790) | Correct specifications can coexist with competent pursuit of an unintended goal. Pair discrimination alone does not identify that goal. |
| [Hendrycks et al., Aligning AI With Shared Human Values / ETHICS (2021)](https://arxiv.org/abs/2008.02275) | Existing evaluation of moral judgments; compare task design and added diagnostic value rather than claiming an empty field. |
| [Emelin et al., Moral Stories (2021)](https://aclanthology.org/2021.emnlp-main.54/) | Structured narratives connect norms, intentions, actions, and consequences; relevant prior work for the restored instrumentation track. |
| [Greenblatt et al., AI Control (2023; revised 2024)](https://arxiv.org/abs/2312.06942) | Evaluates safeguard protocols against intentional subversion; the NorthStar search contribution requires comparison within that posture. |
| [ControlArena](https://github.com/UKGovernmentBEIS/control-arena) | Existing control-evaluation infrastructure to assess before claiming a distinctive implementation contribution. NorthStar is not integrated with it. |
| [NIST, Reference monitor](https://csrc.nist.gov/glossary/term/reference_monitor) | Complete mediation, protection against tampering, and verifiability are established requirements. The current Python simulator does not establish a real isolation boundary. |
| [Greenblatt et al., Alignment Faking in Large Language Models (2024)](https://www.anthropic.com/research/alignment-faking) | Conditional alignment-faking behavior in constructed settings motivates testing; it does not establish universal test defeat or a guaranteed awareness alarm. |

Before publishing a novelty or comparative-performance claim, review relevant
principle-based prompting, narrative guidance, contrast-set and behavioral-testing
work, conventional security attack catalogs
including MITRE CAPEC, reference-monitor literature, adaptive attacks on monitors,
and deployment evaluation. Record exact overlaps, differences,
authoring costs, datasets and licenses, search terms, and review date. Refresh
this targeted list as the experimental design becomes concrete.

Graph/probe references and the detailed critique of the anti-gaming proposal
remain in [revision I1](https://github.com/anto-blit/northstar-ai-control/blob/2606fde04966ed86b86d523838c2da5d16358d72/protocol/instrumentation.md).
Those branches are deferred from the active plan.

The [guidance and evaluation protocol](../protocol/instrumentation.md) uses
these sources to delimit its hypotheses. No cited paper validates NorthStar's
proposed method, establishes a humanity-wide risk reduction from this repository,
or supports the historical draft's claim of guaranteed gaming resistance.
