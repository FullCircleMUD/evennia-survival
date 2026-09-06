# CLAUDE.md

> **Project-wide working rules and cross-repo context live in the FCM umbrella repo's `CLAUDE.md`**,
> loaded automatically when you work from the umbrella root. If you opened this repo directly instead
> of via the umbrella, relaunch from the umbrella root for the full context. This file holds only this
> repo's specific instructions.

Instructions for Claude (and other LLM agents) working in this repository.

## What this project is

`evennia-survival` gives [Evennia](https://www.evennia.com/) objects upkeep meters — hunger and
thirst — that deplete on a clock, and a second clock that hands both meters to the game so it can
decide what being hungry does. Tagline: **"Hunger, thirst and regeneration for Evennia."**

FullCircleMUD is the intended first consumer and has its own working version of this, described in
its `design/survival-system.md`. Nothing has been taken from it wholesale.

For the big-picture overview, read [README.md](README.md).
For the design wiki, read [docs/INDEX.md](docs/INDEX.md).

## Project status

**Complete against what it set out to do.** A consumer declares their stages and intervals, adds
`SurvivalMixin` to whatever should get hungry, starts the two clocks, and answers the hooks. Meters
tick and the consequences are handed back on the fast clock. Untried against a real game. Eating,
drinking and containers are out of scope: the library decides nothing about what a game feeds anyone.
See [docs/progress.md](docs/progress.md) and [docs/installing.md](docs/installing.md).

## Where to read first

1. [docs/test-plan.md](docs/test-plan.md) — the cases the library commits to. **A behavioural change
   starts here**, not in the code. **Start here.**
2. [README.md](README.md) — what the library is and its status.
3. [docs/INDEX.md](docs/INDEX.md) — map of all design docs.
4. [docs/interoperability.md](docs/interoperability.md) — this library against its siblings.

**FCM's `design/survival-system.md` describes the system being extracted, not this library.** It is
the source to read for how the mechanism behaves today. It is not a specification for what belongs
here — it describes bread, inns, spells, NFT containers and an AMM, and most of that stays in FCM.

## Load-bearing architectural principles

Every implementation decision must respect them.

1. **The library does not own game concepts.** Food, drink, recipes, currencies, rooms, spells and
   what a character's death means belong to the consumer game. The library provides staged meters, the
   tick that steps them, and the regeneration decision that reads them.

2. **No FCM-specific assumptions.** This library is being extracted from work on FullCircleMUD. Bread,
   the AMM, inns, NFT items, FCM class and spell names, FCM typeclass names — all stay in FCM. Default
   to "consumer concern" when uncertain.

3. **Test-first.** A case lands in [docs/test-plan.md](docs/test-plan.md), then the test, then the
   code. See [test-first-process.md](../../design/test-first-process.md) for the process and the
   rationale.

The mechanism/content line is drawn: meters and clocks here, everything a meter *means* in the game.
See *Out of scope* below.

## Out of scope

Decided as questions arise. Rulings so far:

- **Eating, drinking, food and drink containers.** The library decides nothing about what a game feeds
  anyone or how it manages it. No `eat`, no `drink`, no container — a game calls `restore_hunger()`
  from whatever it already has. Full reasoning in [docs/design.md](docs/design.md) § Out of scope; a
  reference implementation, if ever wanted, goes in `contrib/` and never in core.
- **The library owns no tables.** The meters are state on the holder, which belongs to the consumer's
  game database. No alias, no router, no migration for a consumer to configure. Revisit only if the
  library gains data of its own that must outlive a rebuild or be read from more than one instance.

## Working conventions

- **Behavioural change starts in the test plan.** Add the case, write the test, then implement. Fill
  the **Test function** column when the test exists — it is a coverage claim and the linter checks it
  both ways.
- **Editing design docs.** Update or add design documents whenever an architectural decision is made
  or refined. Capture the *why*, not just the *what*. Index new docs in [docs/INDEX.md](docs/INDEX.md).
- **Don't put implementation detail in this file or README.** Link out to `docs/` instead. Keep
  `CLAUDE.md` and `README.md` stable; let `docs/` churn.
- **License.** BSD 3-Clause. Source files carry an SPDX header on the first line
  (`# SPDX-License-Identifier: BSD-3-Clause`).

## Documentation discipline (load-bearing)

Design documents in `docs/` must reflect decisions **actually discussed and agreed on with the project
owner**. They are not a place to forward-design the system from first principles or extrapolate
"reasonable defaults" from a starting point.

**Rules:**

1. **Only capture what was discussed and agreed.** If the conversation establishes a principle, do not
   extrapolate it into specifics that were not raised — stage counts, tick rates, API shapes, setting
   names.
2. **Flag open questions explicitly.** Write `[TBD — needs discussion: <what is open>]` so a future
   session picks the topic up deliberately rather than inheriting an unagreed assumption.
3. **Smaller is better.** Three discussed points captured faithfully beat three discussed points plus
   seven invented ones. Resist filling out sections "for completeness".

**The tempting source of unasked-for answers is FCM's own implementation.** It has a working shape for
every question this library will face, ready to be lifted. A shape lifted from it is an invention
unless it has been discussed here — the extraction is a design exercise, not a copy.

## Repository layout

```
evennia-survival/
├── CLAUDE.md                  # this file
├── README.md
├── LICENSE                    # BSD 3-Clause
├── pyproject.toml
├── runtests.py                # standalone test runner; no gamedir required
├── .gitignore
├── docs/                      # design wiki (humans + LLMs)
│   ├── INDEX.md
│   ├── design.md              # how the library is put together, and why
│   ├── installing.md          # what a consumer declares; grows as we decide
│   ├── progress.md
│   ├── test-plan.md
│   ├── interoperability.md
│   └── archive/               # historical context, not authoritative
├── examples/
│   ├── requirements.txt       # installs the library editable into the demo venv
│   └── demo/                  # demo gamedir exercising the library end to end
├── src/
│   └── evennia_survival/      # library code (src layout)
│       ├── __init__.py
│       ├── apps.py            # AppConfig — ready() runs the boot check
│       ├── config.py          # the settings, check_settings(), the accessors
│       ├── stages.py          # SurvivalStage — the base a consumer subclasses
│       ├── mixins.py          # SurvivalMixin — the meters and the hooks
│       ├── services.py        # the tick body; not a method on the holder
│       ├── log.py             # shim onto Evennia's logger → survival.log
│       └── tests.py           # unit tests, run via runtests.py
└── tests/                     # standalone test infrastructure
    ├── __init__.py
    ├── test_settings.py
    ├── stage_stubs.py         # stage enums; imports nothing but the library
    ├── game_typeclasses.py    # real typeclasses carrying the mixin
    ├── raising_stage_module.py
    └── urls.py
```

**The tick body is in `services.py`, not on the mixin.** The ticking that decrements the meters is what
the library is for and is not an extension point, so it does not live somewhere a consumer can override
it. The mixin carries the hooks into it. Do not "tidy" it onto the holder.

**The clocks are Twisted `LoopingCall`s, not Evennia scripts** — nothing persistent to get stuck
stopped. That makes the two guards in `run_survival_pass` and `guarded_survival_pass` load-bearing: an
exception reaching a `LoopingCall` stops it, and the clock then goes quietly dead while the game looks
healthy. The inner guard is per holder, so one consumer's broken hook does not end the tick for
everyone behind them in the list.

**Holders are found from sessions and from a tag, never from the idmapper cache.** The cache holds only
what has been touched since boot, so a mob nobody has visited would never tick and then start when a
player wandered past.

No `contrib/` — nothing opt-in exists, and the standards forbid scaffolding one empty.

Two venvs, both gitignored: `venv/` at the repo root for the library's own tests, and `examples/venv/`
for the demo gamedir. Every library here keeps them separate.

## Tools and environment

- Python 3.10+ (pinned via `pyproject.toml`).
- Evennia is the only runtime dependency.
- **Tests use Django's test runner** via `python runtests.py`, which bootstraps Django then calls
  `evennia._init()`, as the siblings do. Not pytest, and no gamedir required.
- Development uses a dedicated venv at `venv/` (gitignored), independent of any consumer game.
- **Stages are declared by the consumer, so the suite declares its own** — in `tests/stage_stubs.py`,
  which **imports nothing but `evennia_survival.stages`**. `test_settings.py` points the two stage
  settings there and `ready()` resolves them during `django.setup()`, so anything that module imported
  would be pulled in while the app registry is still being built. A test needing a badly-formed enum
  declares it inside the test body, since a set the base class refuses cannot exist at module scope.
- **The suite boots as a configured instance.** `tests/test_settings.py` declares all four settings; a
  case wanting one absent overrides it to `None`.

## Sibling libraries to reference

- **[../evennia-scaling/](../evennia-scaling/)** and **[../evennia-archive/](../evennia-archive/)** —
  the reference shape for repo structure, the test runner and the docs surfaces.
- **[../evennia-shards/](../evennia-shards/)** — documents how a global script behaves when the game
  runs as more than one process, which is the tick's problem too.
