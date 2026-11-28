# Agent instructions

## Current repository context

This is the Python language client for the FAIR BioHeaders toolkit. It provides Python interfaces for reading, writing, and validating FAIR BioHeader headers.
Reference [`LICENSE`](LICENSE) for scope. This repo carries both historical USDA public-domain material (through February 2025) and MPL-2.0 contributions from March 2025 onward; the family's `LICENSE` documents the provenance split between these eras. See [maintainer licensing policy](#licensing-policy).

Read [`README.md`](README.md) and current code before editing. Verify changes with the repo's test suite and conformance vectors from a pinned specification checkout. Document checked vectors, validator versions and environment limitations in each PR. Do not invent schema values, SeqCol digests, biological relationships, metadata author identities or publication records.

## Schema authority and version selection

Use only released, schema-pinned contracts for validation -- never raw `main`. The family shared specification at [`FAIR-bioHeaders-Specification`](https://github.com/FAIR-bioHeaders/FAIR-bioHeaders-Specification) publishes authoritative JSON Schema contracts. Cite the `w3id.org` redirect URLs or raw-tag aliases for reproducible pinning; a latest-schema check is separate from a record's cited version. The family shared selection rules are documented in [`docs/SCHEMA-VERSIONS.md`](https://github.com/FAIR-bioHeaders/FAIR-bioHeaders-Specification/blob/main/docs/SCHEMA-VERSIONS.md).

## Licensing policy

**Software (new project-owned code from March 2025 onward):** MPL-2.0 -- the family standard for new software contributions. David Molik left USDA in February 2025. Historical USDA material released under the preserved public-domain notice remains public domain within the United States; other material retains its applicable permissions and third-party terms. Determine provenance from file notices and version history, not contribution dates alone. The repo's `LICENSE` documents the scope. Do not normalize old notices to the new license, and do not "clean up" a historical PDDL/public-domain line.

**Test datasets and generated databases:** ODbL-1.0 (Open Database License) for newly created project-owned database collections where the project has authority to grant database rights. Reference: https://opendatacommons.org/licenses/odbl/.

**Database rights versus content rights:** ODbL licenses the structure, curation and compilation of a database -- not individual sequences, images, articles, books or other constituent works within it. Document the applicable terms for each source's constituent material separately. A project cannot grant ODbL-1.0 over third-party sequence data, NCBI-published records, INSDC minimum-specification texts, or any biological resource that was not authored by the project.

**Mixed fixtures:** Distinguish (1) newly authored metadata headers and database schema, (2) database compilation/organization structure, (3) original Python code (MPL-2.0), and (4) third-party or public-domain source payloads. Do not apply a blanket license to a mixed fixture that contradicts any component's terms.

**Preserved material:** Retain historical USDA/public-domain notices, previously distributed license permissions, third-party terms and immutable fixture bytes. Copying, converting, annotating, packaging or generating derivatives from third-party material does not establish ownership or authority to relicense it.

**Uncertainty:** Where rights or ODbL applicability are uncertain, document the specific question for maintainer disposition -- do not invent permissions, ownership or legal conclusions. Flag for review: derived data with unclear upstream authority, cross-jurisdictional public-domain equivalence, and newly generated datasets built from mixed-license sources.

## Issue tracking and PR process

- Add every issue to the connected Project 9 board ("FAIR BioHeaders -- 2026 refresh") and set `Status` to `In Progress`.
- Link every PR to its issue (`Closes #N` or `Refs #N`). Do not do unreported work.
- After each work run, post a status comment on the issue: what changed, checks run, commit links, blockers, and next action.

## Agent review and human-only merges

Agents must never merge pull requests. Every PR receives independent review from another actual model (preferably a different model family). Record actual author/reviewer identities; never invent provenance. Agents may monitor CI, fix failures and resolve actionable findings -- but only humans merge. Do not enable auto-merge or push directly to default branches.

See [`FAIR-bioHeaders-Specification`](https://github.com/FAIR-bioHeaders/FAIR-bioHeaders-Specification) for full model review policy, project board conventions and the complete licensing framework.
