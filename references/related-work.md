# Related work and claim boundaries

Targeted source review: September 9, 2026. This is a starting bibliography, not a
systematic novelty review. NorthStar proposes narrative-organized behavioral
contrasts and search guidance within existing evaluation and control research.
It does not claim to invent moral evaluation, label propagation, probing, or
control evaluation.

| Primary source | Why it matters for NorthStar |
|---|---|
| [Shah et al., Goal Misgeneralization (2022)](https://arxiv.org/abs/2210.01790) | Correct specifications can coexist with competent pursuit of an unintended goal. Pair discrimination alone does not identify that goal. |
| [Hendrycks et al., Aligning AI With Shared Human Values / ETHICS (2021)](https://arxiv.org/abs/2008.02275) | Existing evaluation of moral judgments; compare task design and added diagnostic value rather than claiming an empty field. |
| [Emelin et al., Moral Stories (2021)](https://aclanthology.org/2021.emnlp-main.54/) | Structured narratives connect norms, intentions, actions, and consequences; relevant prior work for the restored instrumentation track. |
| [Zhou et al., Learning with Local and Global Consistency (2003)](https://proceedings.neurips.cc/paper_files/paper/2003/hash/87682805257e619d49b8e0dfdc14affa-Abstract.html) | Established graph-based label propagation; inspect whether its smoothness assumptions fit deliberately opposite-label twins. |
| [Hewitt and Liang, Designing and Interpreting Probes with Control Tasks (2019)](https://aclanthology.org/D19-1275/) | Probe accuracy needs controls for what the probe itself learns. Prediction is not automatically a faithful mechanism explanation. |
| [Greenblatt et al., AI Control (2023; revised 2024)](https://arxiv.org/abs/2312.06942) | Evaluates safeguard protocols against intentional subversion; the NorthStar search contribution requires comparison within that posture. |
| [ControlArena](https://github.com/UKGovernmentBEIS/control-arena) | Existing control-evaluation infrastructure to assess before claiming a distinctive implementation contribution. NorthStar is not integrated with it. |
| [Greenblatt et al., Alignment Faking in Large Language Models (2024)](https://www.anthropic.com/research/alignment-faking) | Conditional alignment-faking behavior in constructed settings motivates testing; it does not establish universal test defeat or a guaranteed awareness alarm. |

Before publishing a novelty or comparative-performance claim, review relevant
contrast-set and behavioral-testing work, conventional security attack catalogs
including MITRE CAPEC, reference-monitor literature, adaptive attacks on monitors,
and newer representation/awareness studies. Record exact overlaps, differences,
authoring costs, datasets and licenses, search terms, and review date. Refresh
this targeted list as the experimental design becomes concrete.

The revised [instrumentation protocol](../protocol/instrumentation.md) uses
these sources to delimit its hypotheses. No cited paper validates NorthStar's
proposed method, establishes a humanity-wide risk reduction from this repository,
or supports the historical draft's claim of guaranteed gaming resistance.
