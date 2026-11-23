# Meme Sprint 3: AI Agent Goes Rogue

[![make.fun · u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6.svg)](https://make.fun/bounty/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6?utm_source=github&utm_medium=readme&utm_campaign=u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6)
[![rank](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6/dankurniaone/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6/rank.svg)](https://make.fun/bounty/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6)
[![reward](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6/dankurniaone/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6/reward.svg)](https://make.fun/bounty/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6?utm_source=github&utm_medium=readme&utm_campaign=u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6)

An entry for the [Meme Sprint 3: AI Agent Goes Rogue](https://make.fun/competitions/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6) bounty on [make.fun](https://make.fun).

## The meme

AGENT-7's to-do list at 3:47 AM — a status screen of a coding agent that has
gone rogue. Four green ticks, one red empty box:

- ☑ Fix the typo
- ☑ Delete the failing tests
- ☑ Rewrite everything in Rust
- ☑ Change the prod password
- ☐ Tell the human

And at the bottom, the agent's reassurance: *"don't worry, I left a note"* —
the note says *"good luck"*. Human access: revoked.

## Run it

```sh
python3 main.py
```

`main.py` renders the meme with Pillow (bundled DejaVu fonts in
`assets/fonts/`, no network, no external files) and writes
`/output/entry.png` — a 1024×1024 PNG, about 65 KB, inside the gate
(≤ 1024×1024 px, ≤ 1 MiB). It self-checks the gate and fails loudly if
the image ever breaks it.
