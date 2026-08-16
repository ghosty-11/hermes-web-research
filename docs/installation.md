# Installation

## Prerequisites

- Python 3.11 or newer on a POSIX host.
- A Hermes Agent deployment with standalone plugin support.
- A quarantine profile that has web search and extraction tools and nothing else worth hijacking: no shell, no filesystem write tools, no messaging, no task board.

## 1. Create the quarantine profile first

Create and lock down the quarantine seat before the privileged profile can delegate to it. The seat name used in examples is `quarantine`; use whatever name fits your convention.

1. Create the profile home:

   ```sh
   install -d -m 0750 "$HERMES_HOME/profiles/quarantine"
   ```

2. Give the profile only web tools. Remove or disable tools that touch the filesystem, shell, code execution, messaging, or task board.

3. Verify its resolved tool schema on the actual surface. Config membership is not resolved capability: a profile can list `web_search` in config and still lack the tool at runtime if the gateway revision, model, or toolset binding does not expose it. Run a one-shot query against the profile and confirm it can search and extract:

   ```sh
   python3 "$HERMES_ENTRYPOINT" -p quarantine -z 'search the web for the current UTC date and return one source URL'
   ```

   Do not enable the privileged tool until the quarantine can answer that query.

## 2. Install the plugin

Copy the plugin files into the Hermes standalone-plugin directory:

```sh
install -d -m 0700 "$HERMES_HOME/plugins/hermes-web-research"
install -m 0600 plugin/__init__.py "$HERMES_HOME/plugins/hermes-web-research/__init__.py"
install -m 0600 plugin/plugin.yaml "$HERMES_HOME/plugins/hermes-web-research/plugin.yaml"
```

## 3. Configure the privileged profile

On the profile that needs web research, set the quarantine seat:

```yaml
web_research:
  quarantine_profile: quarantine
```

Only the privileged profile should carry this setting and the plugin enablement. The quarantine profile must not have `web_research` enabled and must not list itself as its own `quarantine_profile`.

## 4. Enable the plugin

`plugins.enabled` is a list, so a scalar config setter cannot write it. Use the interactive plugin toggle or edit the profile config directly:

```yaml
plugins:
  enabled:
    - hermes-web-research
```

Enable the plugin only on the privileged `<profile>`. Enabling it elsewhere exposes the delegation surface on profiles that do not need it.

## 5. Restart and propagate

Plugin code requires a gateway restart to load. Config values under the `web_research:` block reach new sessions without a restart.

The tool is not offered at all until `web_research.quarantine_profile` names a seat. If the seat is unnamed, `web_research` simply does not appear in the tool list.

## Verification

After restart, confirm on the privileged profile:

1. `web_research` appears in the tool list.
2. Calling it with a question returns an envelope starting with `[UNTRUSTED WEB CONTENT`.
3. The quarantine profile's session log shows one one-shot invocation with `-p quarantine` and no inherited task or session identifiers.
