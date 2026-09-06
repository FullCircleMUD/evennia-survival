# evennia-survival

Hunger, thirst and regeneration meters for Evennia characters — meters that deplete on a shared tick,
and a regeneration pipeline that reads them.

## Status

**Characters and mobs get hungry on a clock.** Declare your stages, add the mixin to whatever should
get hungry, start the clock, and the meters run. What being hungry *does* — the regeneration half — is
the next piece. See
[docs/progress.md](https://github.com/FullCircleMUD/evennia-survival/blob/main/docs/progress.md).

## The problem it solves

Upkeep meters are a standard MUD feature and every game rewrites them: a staged meter, a tick that
steps it down, a rule about what a low stage does to healing, and a way back up. The mechanism is the
same each time; only the stage names, the rates and the food are the game's.

Writing it again means re-deciding things that have a known shape — where the tick lives so it works
under more than one process, what happens to a meter on a logged-out character, how a just-fed
character avoids dropping a stage on the very next tick.

## The approach

The library supplies the mechanism: staged meters, the tick that walks them, and the regeneration /
degeneration decision that reads them. The game supplies the content — what food is, where water comes
from, what a stage is called, and what killing a character means.

`[TBD — needs discussion: exactly where that line falls. Drawing it is the first task of the
extraction, not something settled here.]`

## Is this for you?

Probably, if you want hunger and thirst in an Evennia game and would rather configure a meter than
write one.

Probably not, if your survival model is not staged — a continuous 0–100 bar, or meters driven by
something other than a clock.

## Install

**What a game declares is in [docs/installing.md](https://github.com/FullCircleMUD/evennia-survival/blob/main/docs/installing.md)** — the app, the stage enums, and the two clocks.

Nothing is published yet. Editable install for development against a checkout:

```
git clone https://github.com/FullCircleMUD/evennia-survival.git
cd evennia-survival
python -m venv venv
# Activate the venv (platform-specific)
pip install evennia
pip install -e .
python runtests.py
```

## Learn more

- [docs/INDEX.md](https://github.com/FullCircleMUD/evennia-survival/blob/main/docs/INDEX.md) — the design wiki
- [docs/design.md](https://github.com/FullCircleMUD/evennia-survival/blob/main/docs/design.md) — how the library is put together, and the key problems with how each is being solved
- [docs/installing.md](https://github.com/FullCircleMUD/evennia-survival/blob/main/docs/installing.md) — everything a game declares, growing as each requirement is decided
- [docs/test-plan.md](https://github.com/FullCircleMUD/evennia-survival/blob/main/docs/test-plan.md) — every case the library commits to covering
- [docs/interoperability.md](https://github.com/FullCircleMUD/evennia-survival/blob/main/docs/interoperability.md) — this library against its siblings
- [CLAUDE.md](https://github.com/FullCircleMUD/evennia-survival/blob/main/CLAUDE.md) — context for LLM agents working in this repo

## Licence

BSD 3-Clause. See [LICENSE](https://github.com/FullCircleMUD/evennia-survival/blob/main/LICENSE).
