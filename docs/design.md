# Design

Current thinking on how this library is put together — what it holds, what it hands back to the game,
and how the join between the two works. This is the plan we intend to build against, not a settled
specification: parts of it will turn out wrong once there is code, and changing them is expected rather
than a problem.

## The shape

The library holds **meters and clocks**. The game holds **everything a meter means**.

| The library | The consumer |
|---|---|
| Meter state on a character, and the rules for moving it | The stages themselves — how many, their names, their messages |
| The clocks, and the walk over characters they tick | What a tick does — heal, halt, bleed, die |
| `eat` and `drink`, and the meter rules behind them | What is edible, where it comes from, how it is removed |
| The drink-container primitive | What a container is in the game, and how its state is stored |

Everything below follows from that split.

## The problems, and how we plan to solve them

### Stages, without the library owning them

A stage is a value and the text a player sees on reaching it. The library supplies `SurvivalStage`; the
consumer declares one enum per meter, subclassing it:

```python
class HungerStage(SurvivalStage):
    STARVING = (1, "You are starving.", "$You() $conj(look) close to collapse.")
    FAMISHED = (2, "You are famished.", "$You() $conj(look) badly underfed.")
    ...
```

The base is a class rather than a documented shape, so what a stage is comes from inheritance and
validating one is `issubclass`, not inspection.

**The value carries the ordering**, which is what lets a consumer's tick hook read as
`if hunger <= HungerStage.FAMISHED` instead of matching on names. A **higher value is a better stage**
— the one rule with no enforcement behind it, since a set numbered the other way round is equally
consecutive and equally unique, and produces a meter where eating makes the character hungrier. It is
stated in the docs and shown in the example because that is the only place it can be caught.

**Every member is declared the same way** — a value and both message strings, nothing optional. A bare
value is refused rather than arriving with silent empty strings.

**Stepping is arithmetic on the value.** `shifted(-1)` is one stage worse, `shifted(3)` three better,
clamped at both ends so a caller can ask for more than the meter has room for and compare the result
against where it started to learn whether anything moved. Because it is arithmetic, the library never
reads the order a consumer wrote their members in, and they lay the file out however reads best to
them.

The enums reach the library as settings naming modules, per
[library-standards.md](../../../design/library-standards.md) § Consumer-authored config:

```python
SURVIVAL_HUNGER_STAGES = "world.survival_stages.HungerStage"
SURVIVAL_THIRST_STAGES = "world.survival_stages.ThirstStage"
```

Neither has a safe default, so both are checked at boot and the game does not start without them.
Boot also judges the set, which no single member can do for itself: values consecutive, no two the
same. Consecutive values are what make the stepping arithmetic land on a real member.

### Two clocks, not one

Meters deplete slowly and consequences land quickly, so the two run on separate intervals:

- `SURVIVAL_METER_INTERVAL` — how often a character gets hungrier and thirstier.
- `SURVIVAL_REGEN_INTERVAL` — how often the consequences of that are applied.

**Both are required, and neither is defaulted.** The library could pick a cadence, but the right one is
a game-design decision, and a default would put our number in someone's game without anyone having
chosen it. Each must be a positive integer — `"1200"` and `1200.0` are refused, so there is one form to
write and none to guess at, and zero is refused separately from the type because it is a perfectly good
integer that gives a clock which never fires.

Both are library-owned scripts sharing one walk over characters: those with an active session, carrying
the mixin, minus superusers. Doing that walk correctly under a game running as more than one process is
the fiddly part, and we would rather write it once than have a consumer write the second half of it.

#### A meter tick, step by step

- **[library]** the meter clock fires
- **[library]** each character with the mixin and an active session is visited
- **[library]** a pending free pass is consumed instead of stepping the meter, if one is set
- **[library]** otherwise the meter steps down one stage, stopping at the last one
- **[library]** crossing into a new stage emits that stage's message
- **[gap]** none of this is built

### Consequences, without the library knowing what a character is

The library does not touch hit points, does not compute damage, and does not kill anything. It cannot:
healing rates depend on posture and location, and death means corpses and loot, all of which are the
game's.

So the regen clock does exactly one thing — it calls a hook with the current meter states:

```python
def at_survival_tick(self, hunger, thirst):
    ...
```

Everything the game wants to do about being hungry lives in that method: which stage halts healing,
which stage starts bleeding, how fast, and what happens at zero. The library's contribution is that the
method gets called reliably, on the right characters, with current state.

This is why there is no setting naming a health attribute, and no cycles-to-death table in the library.
Both would be the library holding half a decision.

### Moving a meter from outside

Spells, curses, traps and food all need to move a meter, so the mixin exposes it directly:

```python
character.restore_hunger(levels, free_pass=False)
character.increase_hunger(levels)
character.restore_thirst(levels, free_pass=False)
character.increase_thirst(levels)
```

Four named methods over one signed internal, so the clamping is written once but a caller cannot
reverse the direction by passing a negative number.

`free_pass` sets a flag the next meter tick consumes instead of stepping. It is a parameter rather than
automatic because a game may well want some sources to grant it and others not — that asymmetry is how
a game keeps a food economy from being bypassed by a spell, and the library should not decide it either
way.

The library's own `eat` and `drink` call these methods like anything else. There is no privileged path.

### Eating, without the library knowing what food is

`eat` belongs here — the sequencing and the meter rules are the same in every game. What is edible and
how it disappears are not.

Two hooks, and the order between them is the point:

```python
def at_find_edible(self, target):     # -> something, or None
def at_consume_edible(self, edible):  # -> how much it restored
```

#### Eating, step by step

- **[library]** `eat <target>` is parsed
- **[consumer]** `at_find_edible` decides whether the character has that, and hands back whatever
  represents it
- **[library]** the meter is checked for room; a full character is told so and nothing is consumed
- **[consumer]** `at_consume_edible` removes it however the game stores it, and reports what it is worth
- **[library]** the meter steps up by that amount, capped
- **[gap]** none of this is built

Splitting find from consume is what lets the library refuse between them, so a full character does not
waste food. Collapsing the two would lose that.

Whatever `at_find_edible` returns is **opaque to the library** — it is handed straight back to
`at_consume_edible` and never inspected. It can be an object, a string, an id, a row. This is what keeps
the library out of any particular game's inventory model.

`[TBD — needs discussion: the exact return shape of at_consume_edible, in particular how it reports
whether a free pass applies.]`

### Drinking

Water is the easier half, because a container is genuinely an object with genuinely library-owned state
— a capacity and a current level. A mixin makes an item drinkable; `drink` finds one carrying the mixin
and steps thirst up; `refill` fills it.

The one thing the library cannot assume is where that state is stored, since a game may need it to
survive being banked, traded or exported. So changing `current` fires
`at_water_state_changed()`, which writes an Evennia attribute by default and is where a game hangs its
own persistence.

## What is still open

- The exact return shape of `at_consume_edible`, above.
- Whether an out-of-band meter change emits the threshold message immediately, or leaves it to the next
  tick. Current leaning is to leave it to the tick.
- The names of settings that do not exist yet are working names. The four that do — the two stage
  modules and the two intervals — are settled, and [installing.md](installing.md) is where a consumer
  reads them.
