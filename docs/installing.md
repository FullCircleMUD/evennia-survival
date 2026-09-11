# Installing

What a game has to do to run this library. Written as each requirement was decided rather than
reconstructed afterwards, so it describes what exists.

Everything here is enforced at boot: a game that gets any of it wrong does not start, and is told all
of what is wrong at once rather than one thing per restart.

## 1. Install the package

Nothing is published yet, so install from a checkout — and `evennia-logging-extension`, the one
dependency beyond Evennia itself, is also unpublished, so it installs from its own checkout first:

```
pip install -e path/to/evennia-logging-extension
pip install -e path/to/evennia-survival
```

## 2. Add the app

In your settings:

```python
INSTALLED_APPS += ["evennia_survival"]
```

This is what runs the boot check. Without it the library is importable and validates nothing.

## 3. Declare your stages

One enum per meter, subclassing `SurvivalStage`. Put them wherever suits your game — the library reads
a path from a setting and has no opinion about your layout.

```python
# world/survival_stages.py
from evennia_survival.stages import SurvivalStage


class HungerStage(SurvivalStage):
    STARVING = (1, "You are starving.", "$You() $conj(look) close to collapse.")
    FAMISHED = (2, "You are famished.", "$You() $conj(look) badly underfed.")
    HUNGRY = (3, "You are hungry.", "$You() $conj(look) hungry.")
    PECKISH = (4, "You could eat.", "$You() $conj(eye) the stew pot.")
    FULL = (5, "You are full.", "$You() $conj(look) well fed.")
```

Four rules, all checked at boot except the first:

- **A higher value is a better stage.** Number them so the worst stage is lowest. This is the one rule
  nothing can check for you — a set numbered the other way round is just as valid to the library, and
  produces a meter where eating makes the character hungrier.
- **Every member is written the same way** — a value, the message the character sees, and the message
  the room sees. None of the three is optional.
- **Values are consecutive.** Stepping a meter is arithmetic on the value, so a gap is a stage the
  meter can never reach.
- **No two members share a value.** Python quietly folds a repeat into the stage declared before it,
  which would leave your meter one stage shorter than the file you are reading.

How many stages, and what they are called, is entirely yours. The order you write them in is never
read, so lay the file out whichever way you prefer.

## 4. Point the settings at them

```python
SURVIVAL_HUNGER_STAGES = "world.survival_stages.HungerStage"
SURVIVAL_THIRST_STAGES = "world.survival_stages.ThirstStage"
```

Both are required. There is no stage list the library could invent on your behalf.

## 5. Set the two clocks

```python
SURVIVAL_METER_INTERVAL = 1200   # seconds between a character getting hungrier and thirstier
SURVIVAL_REGEN_INTERVAL = 20     # seconds between the consequences being applied
```

Both are required, and both are positive integers — `"1200"` and `1200.0` are refused, so there is one
form to write. No default is supplied because the right cadence is a game-design decision, and a
default would put our number in your game without anyone having chosen it.

## 6. Add the mixin to whatever should get hungry

```python
# typeclasses/characters.py
from evennia_survival.mixins import SurvivalMixin


class Character(SurvivalMixin, DefaultCharacter):
    ...
```

It carries `hunger_level` and `thirst_level`, a free-pass flag behind each, and the methods that move
them — `restore_hunger(stages, free_pass=False)`, `increase_hunger(stages)`, the thirst pair, and
`reset_survival_meters()`. Both meters start at the best stage you declared.

**Nothing about it assumes a character.** Put it on a pet, a mount, an NPC — anything that should get
hungry. Different classes can answer the hooks below differently, which is the point.

## 7. Answer the hooks

Three, all optional to override and all on the mixin.

```python
def at_pre_survival_tick(self):
    """Return False to skip this holder's tick."""
    return bool(self.sessions.count())

def at_post_survival_tick(self):
    """The meters have just moved."""

def at_regeneration_tick(self, hunger, thirst):
    """Everything that being this hungry and this thirsty does. Yours entirely."""
```

**`at_pre_survival_tick` is the only guard there is.** A logged-out character is already skipped —
they are reached through their session, and there is no session. What it is for is the holder that is
found but should sit this one out: a stabled pet, an idle mob. The default permits the tick, so a
class that overrides nothing works, and nothing will write that guard on your behalf.

**`at_regeneration_tick` is where the game happens.** The library reads no hit points, computes no
damage and kills nothing, because healing rates depend on posture and location and death means corpses
and loot. It hands you both meters on a clock and gets out of the way. Whatever guard you want is the
first line of your own method — there is no pre-hook here, because there is nothing of ours to cancel.

## 8. Start the clocks

```python
# server/conf/at_server_startstop.py
from evennia_survival.services import (
    start_regeneration_clock,
    start_survival_clock,
    stop_regeneration_clock,
    stop_survival_clock,
)


def at_server_start():
    start_survival_clock()
    start_regeneration_clock()


def at_server_stop():
    stop_survival_clock()
    stop_regeneration_clock()
```

Two independent clocks. The meter one steps everyone's hunger and thirst; the regeneration one hands
both meters to `at_regeneration_tick` and does nothing else. Stopping one leaves the other running.

Not from `AppConfig.ready()` — that also runs during `evennia migrate` and management commands, where
a clock should not be spinning up. Starting twice is a no-op, so the reload that runs `at_server_start`
again does not leave two loops ticking.

**Who gets ticked, and how they are found.** Player characters come from their sessions, so they tick
while they are being played and not otherwise. Everything else is found by a tag the mixin writes at
creation, so a mob is ticked whether or not anyone is near it.

**That tag is why `at_object_creation` matters.** A typeclass of yours that overrides that hook without
calling `super()` never gets tagged, and its holders silently never tick.

## Required settings

All four, detailed in steps 3–5 above. Each is checked at boot; anything missing or malformed refuses
the start with every problem listed at once.

| Setting | What it does |
|---|---|
| `SURVIVAL_HUNGER_STAGES` | Dotted path to your hunger stage enum |
| `SURVIVAL_THIRST_STAGES` | Dotted path to your thirst stage enum |
| `SURVIVAL_METER_INTERVAL` | Seconds between meter steps — a positive integer |
| `SURVIVAL_REGEN_INTERVAL` | Seconds between regeneration passes — a positive integer |

None has a default: there is no stage list the library could invent, and a default cadence would put
our number in your game without anyone having chosen it.

## Optional settings

None. Every setting the library reads is above.

## What is not checked for you

- **`INSTALLED_APPS`.** Leave the library out of it and `AppConfig.ready()` never runs, so nothing
  above gets validated. This is always the first thing to check when a library appears to be doing
  nothing.
- **Stage direction.** A higher value must be a better stage. A set numbered the other way round is
  just as valid to the library, and produces a meter where eating makes the character hungrier.
- **`super()` in `at_object_creation`.** A typeclass that overrides it without calling up never gets
  tagged, and its holders silently never tick.
- **That the clocks are actually started.** Nothing verifies your `at_server_start` calls the two
  start functions — a game that never starts them boots looking healthy and nobody ever gets hungry.
  An empty `survival.log` where the started lines should be is the tell.

## Watching it

`survival.log`, beside `server.log` in your `LOG_DIR`. It stays silent unless something is wrong, so
anything in it is worth reading. Four kinds of line and no others:

- a clock started, and at what interval
- a clock stopped
- a tick raised on a named holder — with the traceback, and the walk carried on to everyone else
- a pass itself raised

A hook of yours that raises lands in the third of those, named, rather than stopping the clock. That
matters most for `at_regeneration_tick`, since it is the one running your code on the fast interval.

## Feeding and watering are yours

There is no `eat`, no `drink` and no container here, deliberately. The library never decides what your
game feeds anyone or how it manages it — call `restore_hunger()` or `restore_thirst()` from whatever
command, spell or item you already have. See
[design.md](design.md) § Out of scope for why the seam sits there.

## That is all of it

Everything the library does is above. Declare your stages, add the mixin, start the two clocks, and
answer the hooks.
