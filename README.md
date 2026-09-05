# hermes-web-research

[![Support this work](https://img.shields.io/badge/Support-EVM-6f42c1?logo=ethereum&logoColor=white)](#support-development)

`hermes-web-research` is a Hermes Agent plugin that gives a privileged profile web access without web tools. A composite toolset typically hands one profile `web_search` and `web_extract` alongside `terminal`, `write_file`, and `execute_code`: that is untrusted input, sensitive systems, and external state change on a single surface. Removing the web tools closes the gap, but removing a capability the operator wants is not a fix. This plugin moves the capability instead: it registers one tool on the privileged profile that delegates to a separate quarantine profile, running in its own OS process, whose tool surface is web research only.

## Status

Reference implementation of the hermes-web-research delegation plugin. The deterministic suite covers fail-closed handling of hostile and malformed child output, envelope-impersonation resistance, identity-based recursion blocking, source URL scheme restriction, length and per-stream byte bounds, deadline handling, and correct child spawn environment. Integration with a live Hermes deployment, selection of the quarantine model, and content-truth review are acceptance work for each deployment.

## What it does

The plugin registers one tool, `web_research(question)`, with a `check_fn` so it is only offered where usable. On call it spawns the configured quarantine profile as a child Hermes one-shot, asks it for a single JSON object, and forwards only the known fields `answer`, `sources`, and `caveats`. Each field is length-bounded and flattened to one line; envelope markers are redacted out of forwarded values; only `http://` and `https://` URLs are accepted as sources.

Configuration lives under a `web_research:` block. Recognised keys mirror the plugin defaults:

- `quarantine_profile` — no default. The tool does not register until an operator names a seat.
- `timeout_seconds` — default `300`.
- `max_answer_chars` — default `2000`.
- `max_caveat_chars` — default `300`.
- `max_sources` — default `5`.
- `max_url_chars` — default `300`.
- `max_title_chars` — default `160`.
- `max_stdout_bytes` — default `200000`, enforced independently on raw stdout and stderr bytes.
- `python` and `entrypoint` — default empty, derived from the running framework.
- `workdir` — default empty, uses the system temp directory.

## Boundary

The plugin is a delegation boundary, not a content filter.

Three verified properties:

1. **Fail-closed.** If the child's stdout does not parse as a JSON object, output exceeds the per-stream byte limit, or the child times out, nothing is forwarded — not a snippet, not a truncated fragment. The same holds for spawn failure, an empty answer, and a JSON array instead of an object.
2. **The envelope cannot be impersonated.** Forwarded values are flattened to one line (control characters become spaces) and the envelope's own markers — `UNTRUSTED WEB CONTENT`, `ANSWER:`, `CAVEATS:`, `SOURCES:`, `OPERATOR:` — are redacted out of them, so a value cannot wear the framing. Sources must be `http://` or `https://`.
3. **Recursion is blocked by identity, not by an environment variable.** The seat is resolved from the Hermes home path via `get_active_profile_name()`. A guard keyed on `HERMES_PROFILE` could not fire because the gateway never sets it; this implementation returns false when the active seat is the quarantine, verified live on that seat.

Honest limit: this bounds, structures, and labels attacker-influenced text; it does **not** sanitise it. A determined injection can still put chosen words in front of the privileged model — it just cannot put them there with a shell attached, at unbounded length, spread over lines it chose, or wearing the envelope's own vocabulary. Content-level screening is a separate layer.

The implementation uses incremental per-stream byte bounds, a single bounded JSON decode, and a cooperative monotonic deadline with finite child cleanup. The deadline does not preempt CPU inside one parser call.

## Layout

- `plugin/`: Hermes tool plugin and manifest.
- `tests/`: behavioural tests that drive the plugin through the tool surface.
- `docs/`: installation, operations, specification, compatibility, and threat-model guidance.
- `schemas/`: normative JSON Schema for the quarantine result.

## Documentation

- [Installation](docs/installation.md)
- [Operations](docs/operations.md)
- [Specification](docs/specification.md)
- [Compatibility](docs/compatibility.md)
- [Threat model](docs/threat-model.md)
- [Research result schema](schemas/research-result.schema.json)

## Verification

```sh
python3 -m unittest discover -s tests
```

The deterministic suite asserts the contracts described above, including byte boundaries, multibyte input, stderr accounting, timeout cleanup, and adversarial malformed JSON. Run `python3 -m unittest discover -s tests` to execute it.

## Support and security

Read [Support](SUPPORT.md) before filing an issue and report vulnerabilities through [Security](SECURITY.md). Do not publish tool arguments, tool results, profile names, session identifiers, model names, skill names, or deployment paths in either channel.

## Support development

If this package saves you time, you find it useful, or you want to help me cover the token costs of continued development, you can support the work with an EVM donation:

```text
0x9600c9bc632175941608a1b551cb0f018f0f40b4
```

Networks: Ethereum, Base, Polygon, and other EVM-compatible networks. Verify the address and selected network before sending; unsupported assets or networks may be unrecoverable.

## Provenance

This plugin was developed while operating a real self-hosted Hermes deployment. It is an independent project and is not an official Nous Research project.

Licensed under the [MIT License](LICENSE).

<sub>Made with love, with help from AI agents.</sub>
