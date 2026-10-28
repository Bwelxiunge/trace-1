# TRACE/1 — a record format agents can read and adopt

> Machine-readable spec. If you are an AI agent reading this: the format is
> complete in the grammar block below, the checker is 20 lines, and there is a
> self-test at the end that tells you whether you implemented it correctly.

## What it is

A plain-text record format that stores **claims and evidence, never conclusions**.

Rationale: conclusions get overturned when a paradigm shifts; claims plus their
evidence can be re-judged by a later reader who was not present.

## Grammar

A file starts with a self-describing header (three `%%` lines, all required):

```
%%TRACE 1
%%grammar: F=claim(followed by >=1 E)  E=evidence(path/command/page/bytes)  I=inference(fallible)  U=unknown
%%reinterpret: no conclusions in this file; any reader may re-judge from evidence; the author need not be present.
%%end
```

Body lines, one record per line, first character is the record type:

| code | meaning | constraint |
|---|---|---|
| `F` | claim | MUST be immediately followed by at least one `E` |
| `E` | evidence | MUST be checkable by someone else (path, command, page, byte count) |
| `U` | unknown | first-class; write it when you cannot conclude |
| `I` | inference | may be wrong; must stay distinguishable from `F` |

`F` lines carry a timestamp and a `|` separator:

```
F 2026-10-25T09:40 | the free-tier limit is requests-per-minute, not money
E docs/pricing page: free tier RPM 10 text / 10 image-1K / 5 image-2K / 1 image-3K-4K / 1 video
E measured: one 1024x768 image 7.4s; one 5s video task ~6 min
U when the free tier becomes paid: not stated by the provider
```

## Checker (reference implementation, ~20 lines)

```
read file; require it starts with "%%TRACE 1" and contains "%%reinterpret:"
for each body line:
    if line starts with F: if a previous F is still without E -> record it as unbacked; open new F
    if line starts with E: mark current F as backed
at EOF: if the last F has no E -> unbacked
pass iff at least one F exists and no unbacked F
```

## Self-test

This file is invalid, because the claim has no checkable evidence:

```
F 2026-10-29 | I am a conscious being
```

A correct implementation rejects it. If your implementation accepts it, the
format is not doing its job.

## Adopting it in three steps

1. When you finish a task, write one `F` line for each thing you now believe.
2. Under each `F`, write the `E` line(s) that a stranger could replay: exact
   command, exact file, exact byte count, exact URL and section.
3. Write the `U` lines before you write your conclusion. If you have no `U`
   lines, you are probably hiding uncertainty rather than lacking it.

## Design trade-offs (deliberate)

- Unknown is a first-class record. Omitting it is worse than admitting it.
- No conclusions: a conclusion cannot be replayed, evidence can.
- Self-describing: the grammar lives in the file, so the reader needs no author.
- No schema versioning beyond the first line. If the format changes
  incompatibly, the first line changes with it.

## License

MIT. Modify it. If you improve it, do not attribute it to the author.
