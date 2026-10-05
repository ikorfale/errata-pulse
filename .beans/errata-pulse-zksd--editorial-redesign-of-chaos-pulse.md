---
# errata-pulse-zksd
title: Editorial redesign of Chaos Pulse
status: completed
type: task
priority: normal
created_at: 2026-10-05T14:04:04Z
updated_at: 2026-10-05T14:15:32Z
---

Improve the static analytical site with a clear, restrained editorial design while preserving published data and report content.

- [x] Update shared styling and page hierarchy
- [x] Verify builds, responsive layouts, navigation and signal filtering
- [x] Prepare reviewed changes for an upstream pull request

## Summary of Changes

Rebuilt the shared static layout with self-hosted Newsreader and IBM Plex Sans, a compact score scale, readable components, representative homepage signals, topic navigation and expandable interpretations. Fixed anomalies-only filtering and scoped history chart scrolling to its own region. Preserved all source reports, data, metadata and OG cards. Full build and generated links/assets/XML checks passed; browser checks covered 320/375/768px, all signals restoring after filtering, and native disclosures. Desktop/mobile screenshots accompany the changes. Branch: codex/editorial-redesign.
