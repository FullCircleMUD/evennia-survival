# Progress

Running log of milestones with links to evidence. Reverse chronological — newest first.

## 2026-09-06 — meters, and the seams around the tick

38 tests, all passing. An object can carry meters and they can be moved. No clock drives them yet.

- **`SurvivalMixin`** — two meters, a free-pass flag behind each, `restore_`/`increase_` for both, and
  `reset_survival_meters()`. Fifteen cases, `MX-01` to `MX-15`.
- **Nothing in it assumes a character.** The suite's fixture is a plain `DefaultObject`, so "a pet can
  carry this" is what the tests actually exercise rather than something the docs claim.
- **The stage is stored by name**, behind a private attribute, with `hunger_level` a property that
  converts. A row reading `"HUNGRY"` means something to anyone looking at the database.
- **The default is resolved, not declared** — `max(stages).name` behind a callable, because the library
  does not know a consumer's stages until the setting resolves and a module-scope default would be
  evaluated while Django is still loading. This is what `config.py`'s accessors were written for.
- **The tick body is in `services.py`, not on the holder.** The ticking that decrements the meters is
  what the library is for and is not an extension point. `survival_tick(holder)` spends a pending free
  pass or steps the meter, bracketed by two hooks the mixin declares.
- **Three hooks.** `at_pre_survival_tick` cancels on `False` and is the only guard there is;
  `at_post_survival_tick` runs once the meters have moved; `at_regeneration_tick(hunger, thirst)` is the
  consumer's entirely and has no pre/post pair, because there is no body of ours to bracket.
- **A free pass is spent wherever the meter is**, not only at the best stage — a caller can ask for one
  from anywhere, and a pass only spendable at the top would sit set forever on a meter that never got
  there. `[TBD — needs discussion: this diverges from FCM, which honours the pass only at FULL.]`

Still open, and the next conversation: how the clocks gather the holders to tick.
`ObjectDB.get_all_cached_instances()` is verified as reachable, and the property to weigh is that it
reaches more than the things that ought to tick — which is why the guard hook is mandatory rather than
optional.

## 2026-09-06 — a game can be configured, and refused

23 tests, all passing. Four settings, validated at boot. Nothing reads them yet.

- **`check_settings()`** in `config.py`, called from `AppConfig.ready()` and nowhere else. Fifteen
  cases, `CF-01` to `CF-15`.
- **Every problem in one raise**, one per line behind `PROBLEM_PREFIX`. A consumer installing this has
  more than one thing to set, and stopping at the first turns that into fix-restart-fix-restart. The
  constant is also what lets a test count problems without pinning any wording.
- **Each stage setting gets four checks** — declared, resolves, is a `SurvivalStage` subclass, and the
  set is workable. The duplicate-value check reads `__members__` and runs before the consecutive check,
  because Python folds a repeat into the stage before it and what remains can look perfectly
  consecutive.
- **A stage module that will not import is refused whatever the reason.** It exists because this
  library asked for it, so its state is ours to report. The original error is chained rather than
  swallowed, so a consumer gets the setting *and* their own traceback.
- **Both clock intervals are required, and neither is defaulted.** The right cadence is a game-design
  decision; a default would put our number in someone's game unchosen. Each must be a positive integer,
  with `"1200"` and `1200.0` refused so there is one form to write.
- **`tests/stage_stubs.py`** — the suite's stage enums, importing nothing but the library, because
  `ready()` resolves them mid-`django.setup()`.
- **[installing.md](installing.md)** started. A working note written as each requirement is decided,
  rather than reconstructed from memory once everything is built.

## 2026-09-06 — the stage base class

8 tests, all passing. A consumer can declare a meter's stages in a form the library can rely on.
Nothing reads them yet. The shape being built toward is in [design.md](design.md).

- **`SurvivalStage`** — the base a consumer subclasses, one enum per meter. Six cases, `ST-01` to
  `ST-06`.
- **One declaration format, enforced.** `__new__` takes a value and both message strings and defaults
  none of them, so a bare `FULL = 5` is refused at class-definition time rather than arriving with
  silent empty strings.
- **The value carries the ordering**, and the base is int-backed, so a consumer's tick hook compares
  stages directly instead of matching on names.
- **`shifted()` is arithmetic on the value**, clamped at both ends. The library never reads the order a
  consumer declared their members in, so nothing has to be validated about it and they lay the file out
  however suits them.
- **Higher value means a better stage** — documented, not enforced. A set numbered the other way round
  is equally consecutive and unique, so no check can catch it.
- **Judging the set is boot's job, not a member's.** Duplicate and non-consecutive values are refused
  in `check_settings()`, alongside the settings that name the stage modules. Not built.

Also landed: `libraries/` in a consumer's gamedir is the consumer's convention, not ours. The library
takes a settings entry naming a module and has no opinion about where it sits — now a project-level
rule in [library-standards.md](../../../design/library-standards.md) § Consumer-authored config.

## 2026-09-06 — scaffold

The repo is set up to [library-standards.md](../../../design/library-standards.md) and the test runner
reaches the package. No library code.

- **Package, runner and test infrastructure** — `src/evennia_survival/`, `runtests.py`,
  `tests/test_settings.py`. Two scaffold cases pass: the package imports and carries a version, and
  the log shim is a silent no-op outside an Evennia engine.
- **The log shim** — `survival_log`, writing to `survival.log`, copied verbatim from
  `evennia-message-bus` with the name and filename changed.
- **No tables, no alias, no router.** The meters are character state and belong in the consumer's game
  database. Recorded as a ruling in [../CLAUDE.md](../CLAUDE.md).
- **Documentation surfaces** — `README.md`, `CLAUDE.md`, and this wiki with its index, test plan and
  interoperability statement.

What is not here: the survival machinery itself. It is in FullCircleMUD, described in that project's
`design/survival-system.md`, and the extraction has not started. The line between what is library
mechanism and what stays FCM content is open — see the `[TBD]` in [../CLAUDE.md](../CLAUDE.md).
