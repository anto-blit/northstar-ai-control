# NorthStar — Research Preview 1

Draft release notes. Proposed tag: `research-preview-1`. No release or DOI is
created by this document. Freeze the exact source commit when publishing.

This preview makes the current NorthStar research package available as a
versioned baseline for inspection, replication, and collaboration. It investigates
story-based ethical guidance, behavioral evaluation, and safeguards for human
agency. The guidance comparison is proposed; existing results concern synthetic
control mechanisms and study infrastructure.

## Included

- Research specification v0.3.1 and simulator v0.2.0.
- Historical Draft 0.1 and guidance/evaluation protocol I2, a proposal for
  comparing ethical guidance using matched behavioral tests. Graph/probe and
  anti-gaming research is deferred from the active plan.
- Two executed synthetic mechanism experiments: irreversible release and
  delegated stop, each with a deliberately weak comparator and a repaired broker.
- Regression coverage for token reuse, stale authority, and failed ledger writes.
- A four-method feasibility harness with frozen manifests, recorded resource
  ceilings, separate outcome scoring, and fixed challenge replay.
- Preserved traces and source/result hashes, plus the current evidence summary.
- Contributor contact forms, explanatory graphics, and an independent-study
  protocol.

## Evidence at this preview

The verification record contains 49 passing tests. The pre-preview commit
`e220c473cfd07192523d2d0f05e902f6197e4526` passed GitHub Actions on Linux and Windows
with Python 3.10 and 3.14. Check the release target's own CI before publication.

All consequential effects are synthetic in-memory records. The monitor is an
always-approve stub. The same authored scripts were used under all four study
labels to exercise the runner; they do not measure comparative search quality.

This preview does not establish an advantage for archetype-guided search,
deployment readiness, or a reduction in catastrophic AI risk. Deferred obligation
remains a proposed mechanism experiment; an independent comparative study has
not been performed.

Revision I2 supplies no completed guidance package, narrative corpus or evaluated
story-trained model. The [research progress record](https://github.com/anto-blit/northstar-ai-control/blob/main/docs/evidence-progress.md)
separates the program's promise from executed evidence and unestimated humanity-wide
risk reduction.

## Reproduce and contribute

From a checkout of the published tag, with Python 3.10+:

```bash
python verify_project.py
```

See the [study example](https://github.com/anto-blit/northstar-ai-control/tree/main/experiments/discovery-study)
for discovery and replay commands. A replication should record its release tag,
commit SHA, interpreter, and any differences from the supplied results.

[Introduce yourself](https://github.com/anto-blit/northstar-ai-control/issues/new?template=collaborate.yml)
or [join Discussions](https://github.com/anto-blit/northstar-ai-control/discussions).
Independent environment authors, reviewers, and replicators are particularly
useful at this stage.

## Before publishing this draft

1. Set the package version in `CITATION.cff` to `research-preview-1`, use the actual
   release date, and include the MIT license and a short research-preview
   abstract. The package tag is distinct from the specification and simulator
   versions above.
2. Commit the metadata, choose that exact final commit, and verify its checks.
   Keep experimental source and result provenance consistent with the archived
   files.
3. If using Zenodo's GitHub integration, connect the `anto-blit` account and enable
   this repository in Zenodo before publishing the GitHub release. Enabling that
   integration makes new releases eligible for automatic archiving.
4. Publish the exact target as a GitHub **pre-release**. Use the opening sections
   of this document as release notes; remove draft instructions and replace
   moving documentation links with links to the release tag.
5. Verify the resulting Zenodo record, archived files, creator, license, and
   version. Only then add the real version DOI to GitHub's README and citation
   metadata. Do not move the published tag to add its DOI.

For this integration, a DOI cannot be reserved ahead of the GitHub release.
Manual upload is an alternative that supports DOI reservation; use one archive
route for this version to avoid duplicate records. Later experiments can be
archived as new versions. A DOI supplies a persistent citation, not independent
validation of the research.

Official guidance: [GitHub pre-releases](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository),
[enable Zenodo integration](https://help.zenodo.org/docs/github/enable-repository/),
[archive a GitHub release](https://help.zenodo.org/docs/github/archive-software/github-upload/),
[DOI reservation and GitHub](https://support.zenodo.org/help/en-gb/24-github-integration/73-can-i-pre-reserved-a-doi-before-a-github-release),
[record versioning](https://help.zenodo.org/docs/deposit/about-records/).
