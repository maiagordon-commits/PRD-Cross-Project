# Raw Sources Guide
> Use this guide to preserve source material before an agent synthesizes it into the wiki.

## Purpose
`raw/` stores evidence and unprocessed context from Slack, Jira, Confluence, meetings, docs, screenshots, and ad hoc notes.

## Rules
- Keep raw material close to the original.
- Do not over-edit, summarize away nuance, or rewrite source wording.
- Preserve direct links whenever possible.
- Redact secrets, credentials, tokens, private customer data, and sensitive personal information.
- If privacy is unclear, store a short summary and link instead of copying the full source.
- Move durable conclusions, decisions, risks, dependencies, and status summaries into `wiki/`.

## Suggested raw file naming
- Meetings: `YYYY-MM-DD Meeting Name.md`
- Slack: `YYYY-MM-DD channel-or-thread-topic.md`
- Jira: `YYYY-MM-DD jira-board-or-issue-key.md`
- Confluence: `YYYY-MM-DD page-title.md`
- Docs: `YYYY-MM-DD doc-title.md`
- Misc: `YYYY-MM-DD short-topic.md`

## Source intake template

```markdown
# Source Title

Date captured: YYYY-MM-DD
Source type: Slack | Jira | Confluence | Meeting | Doc | Dashboard | Other
Source link:
Captured by:

## Raw Content

Paste or summarize source material here.

## Notes for Synthesis

- Important facts:
- Potential decisions:
- Risks/blockers:
- Action items:
- Follow-up questions:
```

