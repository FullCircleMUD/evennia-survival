# Design

Current thinking on how this library is put together — what it holds, what it hands back to the game,
and how the join between the two works. This is the plan we intend to build against, not a settled
specification: parts of it will turn out wrong once there is code, and changing them is expected rather
than a problem.

## The shape

The library holds **meters and clocks**. The game holds **everything a meter means**.

| The library | The consumer |
|---|---|
| Meter state on a holder, and the rules for moving it | The stages themselves — how many, their names, their messages |
| The clocks, and the walk over the holders they tick | What a tick does — heal, halt, bleed, die |
| Keeping those clocks running, and saying so when they stop | Eating, drinking, food, containers, and everything about them |

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

Each is a Twisted `LoopingCall`, not an Evennia script — nothing persistent to get stuck stopped, and
recreated at every boot. Started from the consumer's `at_server_start()` rather than
`AppConfig.ready()`, because `ready()` also runs during `evennia migrate` and management commands.

**Holders are found two ways, because the two kinds are found differently.** Player characters come
from their sessions: they move in and out of play, and a session is the only thing that says which are
in it now. Everything else comes from a tag the mixin writes at creation — a mob is in the game whether
or not anyone is near it, so it is found by an indexed query rather than by whatever happens to be in
memory. The two sets cannot overlap, because a player character is never tagged.

The idmapper cache is deliberately not used for this. It holds only what has been touched since boot,
so a mob nobody has visited would never tick and then start when a player wandered past.

#### A meter tick, step by step

- **[library]** the meter clock fires
- **[library]** puppeted holders are gathered from the sessions, tagged ones from a query
- **[consumer]** `at_pre_survival_tick()` answers whether this holder ticks at all; anything falsy cancels
- **[library]** a pending free pass is spent instead of stepping that meter, if one is set
- **[library]** otherwise the meter steps one stage worse, stopping at the last one
- **[consumer]** `at_post_survival_tick()` runs, with the meters already moved
- **[library]** anything raised is caught per holder, named in `survival.log`, and the walk carries on

No gaps: this part is built.

### The tick is the library; the consequences are the game's

The ticking that decrements hunger and thirst is what this library is for. It is not an extension
point, which is why the body sits in `services.py` rather than on the holder where a consumer could
override it.

What the library will not do is act on the result. It touches no hit points, computes no damage and
kills nothing — healing rates depend on posture and location, and death means corpses and loot, all of
which are the game's. So the regeneration clock has no body at all. It calls one hook:

```python
def at_regeneration_tick(self, hunger, thirst):
    ...
```

Everything a game wants to do about being hungry lives in that method: which stage halts healing, which
starts bleeding, how fast, what happens at zero, and whatever guard decides this holder should be
skipped. The library's contribution is that it gets called reliably, with current state.

This is why there is no setting naming a health attribute and no cycles-to-death table here. Both would
be the library holding half a decision.

**Two hooks bracket the survival tick and one stands alone at the regeneration tick.** The survival
tick has a body of ours worth bracketing; the regeneration tick has none, so a pre and a post would sit
either side of nothing.

### Moving a meter from outside

Spells, curses, traps and food all need to move a meter, so the mixin exposes it directly:

```python
holder.restore_hunger(stages, free_pass=False)
holder.increase_hunger(stages)
holder.restore_thirst(stages, free_pass=False)
holder.increase_thirst(stages)
holder.reset_survival_meters()
```

**Nothing here assumes a character.** The mixin carries meters; what it is attached to is the
consumer's business, and a pet with meters is as valid as a player with them. `reset_survival_meters()`
exists because a consumer cannot write it themselves — which stage is the best one is theirs to declare
and ours to resolve.

Four named methods over one signed internal, so the clamping is written once but a caller cannot
reverse the direction by passing a negative number.

`free_pass` sets a flag the next meter tick consumes instead of stepping. It is a parameter rather than
automatic because a game may well want some sources to grant it and others not — that asymmetry is how
a game keeps a food economy from being bypassed by a spell, and the library should not decide it either
way.

## Out of scope — eating, drinking, and what a game feeds anyone

**The library makes no decision about what a game eats or drinks, or how it manages any of it.** No
`eat` command, no `drink` command, no food, no drink container. A game calls `restore_hunger()` from
whatever it already has.

The seam is there because that is where the library stopped being useful. Work through an `eat`
command and it dissolves: the library cannot know what is edible, so that is a hook; it cannot know how
a game removes what was eaten, so that is another hook; it cannot know what a mouthful is worth, so
that comes back from the consumer too. What remains between the hooks is argument parsing and a call to
a method the mixin already exposes. Shipping that would mean shipping a shape for eating that games
then have to work around, in exchange for saving them three lines.

A drink container goes the same way. Strip a game's own answers to where the water came from, what the
container is worth and how its state survives being traded, and what is left is an object with a number
on it.

**So the library does two things.** Whatever a consumer chooses gets hungrier and thirstier over time,
through stages they define. And there is one hook where they define what those stages do to the thing
carrying them.

If a reference implementation is ever wanted, `contrib/` is where it goes — opt-in, and clearly one
answer rather than the answer. See the standards. Nothing goes in core.

## What is still open

- Whether an out-of-band meter change emits the threshold message immediately, or leaves it to the next
  tick. Current leaning is to leave it to the tick.
- The names of settings that do not exist yet are working names. The four that do — the two stage
  modules and the two intervals — are settled, and [installing.md](installing.md) is where a consumer
  reads them.
