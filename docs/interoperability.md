# Interoperability

This library against every sibling library in `libraries/`, including itself. A reader deciding
whether two of our libraries can be co-installed gets a definite statement from either side rather
than inferring from silence.

Each section names the relationship — **hard dependency**, **optional integration**, or **no
coupling** — followed either by the constraints that apply or by an explicit clearance stating *why* it
is clear in terms of what this library does. "No known issues" is not a clearance.

**The library is untried against a real game**, so every statement below is provisional. The
clearances rest on three properties it holds today: it owns no tables and its state is Evennia
Attributes on the holder; it imports nothing but Evennia and the logging extension; and it finds
holders only through sessions and its own tag, never by searching the world.

## evennia-ai-memory

**No coupling.** Neither library imports the other. ai-memory stores what an NPC knows and remembers
in its own tables; this library stores meters as Attributes on the holder and writes no prose. An NPC
remembering that it was hungry would be the consumer composing the two in its own prompt code.

## evennia-archive

**No coupling.** Neither library imports the other. The meters are Attributes on the character, so
they travel with an archived copy as bytes and come back with it — a character arrives as hungry as
it left. Archive's own [interoperability.md](../../evennia-archive/docs/interoperability.md) states
the same from its side.

## evennia-calendar

**No coupling.** Neither library imports the other. The meters are stepped by this library's own
clocks in real seconds; the calendar reports game time and seasons and knows nothing about meters.
The likely real interaction — hunger and thirst rates varying with weather — is composition through
a weather layer that does not exist yet, and is recorded as open in calendar's
[interoperability.md](../../evennia-calendar/docs/interoperability.md).

## evennia-database-cascade

**No coupling.** Neither library imports the other. This library owns no models and configures no
alias or router; its state is Evennia Attributes, which are in the game database by definition, so
there is nothing for a cascade to route.

## evennia-equipment

**No coupling.** Neither library imports the other. Both hang state off a character and read nothing
of each other's. A game wanting encumbrance to slow regeneration reads `is_encumbered` inside its own
`at_regeneration_tick` — a consumer rule, and neither library needs to know the other is installed.

## evennia-llm-service

**No coupling.** Neither library imports the other. llm-service is a provider client and a template
loader; it holds no game objects and reads no Attributes. An NPC prompt that mentions hunger is the
consumer reading a meter and writing it into its own template.

## evennia-logging-extension

**Hard dependency.** `log.py` binds `survival_log` through its `make_logger`, and every line the
library emits goes through that binding to `survival.log`. The library does not run without it —
`pyproject.toml` declares it. Nothing flows the other way: the extension knows nothing about the
meters.

## evennia-message-bus

**No coupling.** Neither library imports the other. The bus carries messages between instances; the
meters move between instances as Attributes on the character, through the archive, and nothing about
them is ever a message.

## evennia-mob-spawner

**No coupling.** Neither library imports the other. Whether a spawned mob carries meters is the
consumer's typeclass decision, invisible to both libraries: a spawned mob whose typeclass carries
`SurvivalMixin` is tagged at `at_object_creation` and ticked like any other holder, and despawning
deletes the object so the tag query simply stops finding it.

## evennia-portal-multiplex

**No coupling.** Neither library imports the other. Multiplex hands a player's session between
Servers without dropping or changing it; the tick reads the local `SESSION_HANDLER`, so a character
is ticked by whichever instance currently holds its session — exactly the per-instance story in the
evennia-scaling section.

## evennia-scaling

**No coupling.** Neither library imports the other, and nothing scaling does touches the meters —
they come through the archive as Attributes like everything else on the character. The clocks are
per-instance, so a character only ages where it is: a character nobody holds — in the archive between
a departure and an arrival — is not ticked by anybody. Scaling's own
[interoperability.md](../../evennia-scaling/docs/interoperability.md) states the same from its side.

## evennia-shards

**No coupling.** Neither library imports the other. The one topology to watch is shards' several
server processes over one database: every process would start its own clocks at `at_server_start`,
and each one's tag query would find every holder, multiplying the tick rate by the number of
processes. Scaling's independent instances do not have that problem.

## evennia-survival

This library.

## evennia-targeting

**No coupling.** Neither library imports the other. Targeting wraps `caller.search()` to filter
candidate lists already in hand; this library searches for nothing — it acts on characters it is handed
by a tick or by a consumer's command.

## evennia-world-builder

**No coupling.** Neither library imports the other. World content stays entirely out of this library
— the same ruling as eating and drinking: a fountain that slakes thirst is the consumer's fixture
calling `restore_thirst()` from its own code. An NPC world-builder places is created through the
normal typeclass path, so one whose typeclass carries the mixin is tagged and ticked like any other
holder.

## evennia-yaml-reader

**No coupling.** Neither library imports the other. yaml-reader depends only on `pyyaml`, has no
Evennia dependency and touches no database, so nothing it does is visible to this library and nothing
this library does is visible to it.

## fcm-telemetry-spawn

**No coupling.** Neither library imports the other. telemetry-spawn measures the item and resource
economy; this library has no items and no economy — what a meal costs is the game's business, and
`restore_hunger()` neither knows nor cares what the game consumed to earn the call.

## fcm-xrpl

**No coupling.** Neither library imports the other. fcm-xrpl puts item and currency ownership on the
ledger; the meters are transient state on the holder, owned by nobody and worth nothing — there is
nothing here to mint, hold or transfer.
