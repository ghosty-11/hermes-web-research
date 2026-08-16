# Compatibility

## Reference baseline

- Python 3.11 or newer on a POSIX host.
- Hermes Agent standalone plugin API with `register_tool` and `check_fn` support.
- A quarantine profile whose tool surface is restricted to web search and extraction.

## Framework seams

The plugin depends on the following framework interfaces. Each is imported inside a try block so the plugin degrades rather than crash when a seam is absent.

| Seam | Purpose | What degrades if absent |
|---|---|---|
| `hermes_cli.profiles.resolve_profile_env` | Resolve `web_research.quarantine_profile` to a profile home path. | The quarantine cannot be located; `_available()` returns `False` and the tool is not offered. |
| `hermes_cli.profiles.get_active_profile_name` | Determine which seat the current session IS, for the recursion guard. | Falls back to deriving the profile name from the Hermes home path; self-reference detection still works in standard layouts. |
| `hermes_cli.config.load_config` | Read the `web_research:` block from the active profile config. | Falls back to built-in defaults; `quarantine_profile` stays empty, so the tool is not offered until set by another mechanism. |
| `hermes_constants.get_hermes_home` | Locate `$HERMES_HOME` consistently with the framework. | Falls back to `$HERMES_HOME` environment variable, then `~/.hermes`. |
| `gateway.session_context._VAR_MAP` | Scrub additional gateway-specific variables from the child environment. | Only `HERMES_KANBAN_*` and `HERMES_SESSION_*` variables are removed; other gateway variables may leak to the child. |
| Hermes one-shot CLI contract (`-p <profile> -z <prompt>`) | Spawn the quarantine as a separate process with a single prompt. | The tool cannot run the quarantine; every call returns an entrypoint error. |

## Degradation behaviour

Missing seams are handled defensively:

- The tool never registers if `quarantine_profile` is unset or unresolvable.
- The tool never registers if the active session is the quarantine profile.
- A missing `gateway.session_context._VAR_MAP` does not prevent the tool from running; it only reduces the set of variables scrubbed from the child environment.
- A missing `hermes_cli` derivation for the entrypoint leaves `entrypoint` empty and produces a refusal unless `web_research.entrypoint` is configured explicitly.

## Evidence level

The seam contracts were read from the installed framework revision and exercised live against a real quarantine profile. Profile resolution, active-profile identity, config loading, home derivation, and the one-shot spawn contract were all observed during live calls. No clean-host golden path is claimed; verify on the target host before enabling unattended use.
