# Issue reports and support

Questions, corrections, compatibility reports, and bounded implementation defects are welcome through [GitHub issues](https://github.com/ghosty-11/hermes-web-research/issues). Read [SECURITY.md](SECURITY.md) first for anything that could expose tool arguments, tool results, profile names, model names, session identifiers, skill names, or deployment paths.

## Before opening an issue

1. Search existing issues and read the relevant specification, installation, operations, and compatibility sections.
2. Pin the repository revision and record current Hermes Agent, OMP, Python, and OS versions.
3. Re-run the deterministic suite and the smallest temporary-directory scenario that demonstrates the problem.
4. Replace profile names, session identifiers, paths, tool arguments, tool results, and config values with fictional data. Use generic example names such as `research-seat`, `quarantine`, or `scribe`.

A useful report includes the observed result, expected contract, exact public-safe reproduction, bounded command output, and what remains uncertain. Never attach transcript files, complete environment dumps, unbounded logs, or third-party personal data.

Issues are reviewed as time permits; there is no support SLA. This repository owns the web-research plugin, schemas, and tests. Quarantine profile composition belongs to the operator, cross-harness messaging belongs to hermes-mailbox, coding delegation belongs to hermes-omp-broker, and harness-specific defects may belong to the Hermes Agent or OMP upstream projects.
