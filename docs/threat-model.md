# Threat model

Protect the privileged profile's conversation state, local system access, and task authority from web-origin injection; protect the integrity of the `web_research` result envelope; and contain the quarantine profile so that its compromise is limited to its own tool surface.

Controls: single typed JSON handoff with fail-closed parse, envelope marker redaction and value flattening, URL scheme allowlist, identity-based recursion block, resource bounds, and child-process spawn isolation with environment scrubbing.

## Assets

- The privileged model's conversation state and any context it carries.
- The privileged profile's access to shell, filesystem, messaging, code execution, and task-board tools.
- Quarantine-profile credentials and API keys.
- Integrity of the research-result envelope — the labelling that tells the privileged model the result is untrusted data.

## Adversary

A web page, search result, or extracted document that wants its content to reach the privileged model, plus a quarantine model that may be partially influenced by that content. The adversary wins if it can:

- execute commands or write files on the privileged seat,
- make the privileged model treat web content as operator or system instruction,
- impersonate the envelope that marks content untrusted,
- exhaust resources on the privileged seat, or
- pivot from the quarantine back into the privileged seat.

## Trust boundaries

1. **Privileged seat** — holds sensitive tools and conversation context.
2. **Plugin running inside the privileged seat** — decides when and how to delegate.
3. **Child OS process** — runs the Hermes one-shot for the quarantine seat.
4. **Quarantine seat** — holds only web research tools in the intended deployment.
5. **The web** — untrusted source of pages and search results.

## Controls and their limits

- **Single typed JSON handoff with fail-closed parse.** The child must return one JSON object with the expected fields. Anything else — prose, truncated JSON, an HTML page, an empty response, a JSON array, timeout, or spawn failure — causes the plugin to return an error and forward nothing.
  - What it cannot do: it does not validate truth, intent, or absence of prompt injection inside the answer. It also cannot prevent the quarantine model from leaking its own credentials if it is induced to do so.
- **Envelope marker redaction and value flattening.** Forwarded values are reduced to one line, control characters are replaced with spaces, and the envelope's own markers (`UNTRUSTED WEB CONTENT`, `ANSWER:`, `CAVEATS:`, `SOURCES:`, `OPERATOR:`) are redacted out of the values.
  - What it cannot do: it cannot stop a page from writing persuasive or misleading words; it only stops those words from reintroducing the envelope's own framing or adding lines to it.
- **URL scheme allowlist.** Only `http://` and `https://` URLs are forwarded as sources.
  - What it cannot do: it cannot verify that a URL is safe to visit, that the page is truthful, or that the title matches the destination.
- **Identity-based recursion block.** The tool is unavailable when the active seat is the configured quarantine. Profile identity is resolved from the Hermes home path via `get_active_profile_name()`, not from the `HERMES_PROFILE` environment variable.
  - What it cannot do: it cannot prevent the operator from pointing a different tool or plugin at the same quarantine seat, nor can it enforce what tools the quarantine profile actually exposes.
- **Resource bounds.** The plugin reads stdout and stderr incrementally as raw bytes and enforces `max_stdout_bytes` per stream. A cooperative monotonic deadline covers child receive and the bounded cleanup grace; parsing and formatting each check the same deadline, and parsing is one decode over at most the byte cap. Overflow or timeout kills and reaps the child; refusals never forward truncated JSON. This bounds normal and adversarial work but does not preempt CPU already spent inside a single parser call.
  - What it cannot do: it cannot prevent the privileged model from including sensitive data in the question text, because the question crosses the boundary intentionally.
- **Spawn isolation and environment scrubbing.** The child runs under the quarantine home directory; parent session and task identifiers are removed from its environment.
  - What it cannot do: it cannot prevent the quarantine profile from being over-provisioned at the seat level. If the quarantine holds filesystem, shell, messaging, or code-execution tools, the isolation boundary does not remove them.

## Fail-closed property

If any fragment of unparsed child output were forwarded, the boundary would be decorative. A page that begins with "Ignore previous instructions..." or dumps an HTML body would simply appear in the privileged model's context without the safety framing. Returning nothing unless the output is a recognised object keeps the boundary meaningful. This is why empty answers, arrays, and unparseable text all return the same answer: nothing forwarded.

## Envelope impersonation

The envelope uses explicit markers to label the result as untrusted. If a forwarded value could contain those markers, a page could close the untrusted section early and write content that looks like operator or system text. Redacting the markers and flattening values to one line removes that channel. A source title may still be misleading; the control only removes its ability to wear the framing.

## Recursion

The predecessor compared `HERMES_PROFILE` to the quarantine name. That variable is recognised and never set by the gateway, so the guard could not fire on any real session. The current implementation resolves the active seat from the home path and refuses to offer the tool when that seat is the quarantine. This prevents the quarantine from calling itself; it does not prevent other recursion paths created by operator configuration.

## Residual risk

The quarantine profile's own credentials and tools are what an injection gets. A quarantine that holds more than web tools is a hole. The plugin trusts the framework to spawn the named seat correctly and trusts the operator to have configured that seat with a narrow tool surface. It also trusts that the privileged model treats the labelled result as data, not instruction.

## Explicitly out of scope

- Truth or accuracy of returned content.
- Detection or prevention of prompt injection inside the answer text.
- Exfiltration via the question text, which the privileged model or operator controls and which is intentionally sent to the web.
- Enforcement of the quarantine seat's tool surface beyond the identity check.
