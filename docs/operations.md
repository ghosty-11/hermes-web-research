# Operations

## Configuration

All settings live under the `web_research:` block in the Hermes profile config.

| Key | Default | Meaning |
|---|---|---|
| `quarantine_profile` | `""` | Name of the quarantine profile. Empty means the tool is not registered. |
| `timeout_seconds` | `300` | Wall-clock seconds to wait for the quarantine one-shot. |
| `max_answer_chars` | `2000` | Maximum characters forwarded from `answer`. |
| `max_caveat_chars` | `300` | Maximum characters forwarded from `caveats`. |
| `max_sources` | `5` | Maximum source entries forwarded. |
| `max_url_chars` | `300` | Maximum characters per source URL. |
| `max_title_chars` | `160` | Maximum characters per source title. |
| `max_stdout_bytes` | `200000` | Maximum child stdout bytes scanned for JSON. |
| `python` | `""` | Python interpreter to spawn. Empty means `sys.executable` of the running process. |
| `entrypoint` | `""` | Hermes CLI entrypoint path. Empty means derive from the installed `hermes_cli` package. |
| `workdir` | `""` | Working directory for the child process. Empty means the system temp directory. |

## Trade-offs

- `timeout_seconds` is the longest you are willing to block a privileged turn. A real call against a free-tier model has taken roughly 17 s and 42 s on observed runs; set this to the point where waiting costs more than the answer.
- `max_answer_chars` bounds the amount of attacker-influenced text that can reach the privileged model. Raising it widens exactly the channel the boundary exists to narrow.
- `max_sources` bounds how many URLs can be injected into the context. Raising it widens the same channel.
- `max_stdout_bytes` protects the parent from a runaway child. It must be large enough to hold the JSON object and small enough to keep memory bounded. A scan of 200 KB of brace-laden text has taken under one second in testing.
- `python` and `entrypoint` override the derived framework paths. Use them only when the running interpreter or the Hermes CLI is not where the quarantine should run.
- `workdir` changes the child's filesystem context. It has no effect on what the quarantine can reach, because the boundary is the tool schema, not the directory.

## Latency

Each call costs one full agent turn in the quarantine profile: the model must read the prompt, decide to search, perform searches, possibly extract pages, and emit one JSON object. Expect seconds to minutes, not milliseconds. The privileged profile blocks for the duration of that turn plus the JSON parse and neutralisation overhead.

## Reading a refusal

Every refusal begins with `web_research error:` and ends with a statement that nothing was fetched or forwarded. That is the intended outcome, not an error to work around. If the quarantine returns prose, HTML, truncated JSON, a fenced code block, or an array instead of an object, the boundary is doing exactly what it is for: it is refusing to forward raw web text into the privileged context.

Do not bypass a refusal by asking the model to "just show me what it said". The unparsed output is on the quarantine side of the boundary for a reason.

## When it always refuses

1. **Quarantine seat unnamed.** Check `web_research.quarantine_profile` in the privileged profile config. If it is empty, the tool is not even offered.
2. **Quarantine seat lacks web tools.** A profile can exist and still not expose `web_search` or `web_extract` at runtime. Verify with a direct one-shot query against the quarantine profile.
3. **Entrypoint not found.** If `python` or `entrypoint` is configured, verify the paths exist and are executable. If they are empty, verify the running process can import `hermes_cli` and resolve the CLI entrypoint beside it.
4. **Timeout.** A query that requires many searches may exceed `timeout_seconds`. Narrow the question or raise the timeout.
5. **Child output not JSON.** The quarantine may be emitting prose or markdown fences. Inspect its one-shot output directly and adjust its instructions or toolset.

## Misuse warning: do not widen the boundary for convenience

Raising `max_answer_chars` or `max_sources` does not make the tool more capable; it makes the channel wider. The safety property is that only a bounded, structured, labelled object crosses. Widen the caps only when the narrower cap is demonstrably blocking legitimate answers, and only by the smallest amount that fixes the observed case.
