# Security policy

This package is a delegation boundary. It spawns a child Hermes process as another profile identity — the quarantine seat — and forwards only a bounded, structured subset of what that child returns. The privileged profile does not receive web tools of its own; the quarantine profile does.

Forwarded text remains attacker-influenced. The plugin bounds, structures, and labels it; it does not sanitise it. Treat the returned `answer`, `sources`, and `caveats` as untrusted data, not instructions or verified fact.

Reports about spawn environment leakage, quarantine escape, forwarded fragments from malformed child output, envelope-impersonation bypasses, recursion bypasses, or unsafe installation guidance are security-relevant.

## Report privately

Use GitHub private vulnerability reporting for this repository when available. If it is not enabled, open a minimal issue requesting a private reporting channel. Do not put tool arguments, tool results, profile names, session identifiers, model names, skill names, deployment paths, identities, or credentials in a public issue.

## Include

- affected revision and file or component;
- the violated trust boundary and observable result;
- Hermes Agent, OMP, Python, and OS versions that materially affect it;
- a minimal reproduction using fictional profile names such as `research-seat`, `quarantine`, or `scribe` and a temporary directory;
- whether transcript files, config files, or Git history may already be exposed;
- the narrowest safe mitigation known.

Revoke or isolate exposed credentials and remove or restrict access to exposed files before reporting. Preserve evidence privately and use the upstream security channel when the defect belongs to [Hermes Agent](https://github.com/NousResearch/hermes-agent) or [OMP](https://github.com/can1357/oh-my-pi/blob/main/.github/SECURITY.md).

Only the current default branch is maintained. Deployment policy, quarantine profile selection, model selection, and operator authorisation remain outside this repository.

## Operational security

The quarantine profile's own tool surface is the blast radius. Verifying it at the schema level is mandatory; do not assume safety from config text alone. The quarantine seat should expose only web search and web extraction tools. If it also holds filesystem, shell, messaging, code execution, or board-access tools, a successful injection wins those tools, because the plugin cannot shrink the quarantine's own capabilities.

Review the `web_research:` config block before enabling the plugin in a shared or long-running deployment:

- `quarantine_profile`: the seat that performs fetches. Empty means the tool is not offered.
- `timeout_seconds`: ceiling on one research call.
- `max_answer_chars`, `max_caveat_chars`, `max_title_chars`: per-field length ceilings.
- `max_sources`: maximum sources forwarded.
- `max_url_chars`: maximum length of a forwarded URL.
- `max_stdout_bytes`: maximum bytes the parent reads independently from child stdout and stderr; overflow refuses the call and kills the child.
- `python` and `entrypoint`: interpreter and Hermes entrypoint used to spawn the quarantine. Empty defaults derive from the running framework.
- `workdir`: working directory for the child process. Empty defaults to the system temp directory.

These caps limit accidental growth and slow exfiltration; they do not make web content safe to trust.
