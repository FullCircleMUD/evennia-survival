# Installing

What a game has to do to run this library. **A working note, not a finished guide** — it is written as
each requirement is decided, so it stays honest about what exists rather than being reconstructed from
memory once everything is built. Sections appear as the machinery does.

Everything here is enforced at boot: a game that gets any of it wrong does not start, and is told all
of what is wrong at once rather than one thing per restart.

## 1. Install the package

Nothing is published yet, so install from a checkout:

```
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

## Still to come

The rest of the library is not built, so nothing below exists yet. Listed so the shape of the finished
install is visible:

- The mixin a character typeclass adds to carry the meters.
- The hook a character implements to decide what a survival tick does to it.
- The mixin an item typeclass adds to become a drink container.
