# Interoperability

This library against every `evennia-*` sibling library in `libraries/`. The `fcm-*` libraries are
deliberately absent: they are coupled to FullCircleMUD's game concepts and are not offered for outside
consumption, so a reader deciding what to co-install with this library cannot install them anyway.

Each section names the relationship — **hard dependency**, **optional integration**, or **no
coupling** — followed either by the constraints that apply or by an explicit clearance stating *why* it
is clear in terms of what this library does. "No known issues" is not a clearance.

**No library code exists yet**, so every statement below is provisional. A clearance given now rests on
the library having no behaviour to clear; re-confirm each one against the implementation as it lands
rather than inheriting it.

## evennia-ai-memory

`[TBD — needs discussion: not yet assessed.]`

## evennia-archive

`[TBD — needs discussion: not yet assessed. The obvious question is whether a character's meter state
survives being archived and rebuilt, which depends on how the meters are stored — an open decision in
[test-plan.md](test-plan.md).]`

## evennia-llm-service

`[TBD — needs discussion: not yet assessed.]`

## evennia-message-bus

`[TBD — needs discussion: not yet assessed.]`

## evennia-mob-spawner

`[TBD — needs discussion: not yet assessed. Whether spawned mobs carry meters at all is a consumer
decision this library has not yet framed.]`

## evennia-portal-multiplex

`[TBD — needs discussion: not yet assessed.]`

## evennia-scaling

`[TBD — needs discussion: not yet assessed. A tick that walks the sessions on this instance and a
character that moves between instances are both in play, so the interaction is real and unexamined.]`

## evennia-shards

`[TBD — needs discussion: not yet assessed. Shards documents how a global script behaves when the game
runs as several processes, which is directly the tick's problem — see its
[shard-settings.md](../../evennia-shards/docs/shard-settings.md).]`

## evennia-survival

This library.

## evennia-targeting

**No coupling.** Neither library imports the other. Targeting wraps `caller.search()` to filter
candidate lists already in hand; this library searches for nothing — it acts on characters it is handed
by a tick or by a consumer's command.

## evennia-world-builder

`[TBD — needs discussion: not yet assessed. Water sources and rest locations are world content, so the
question is whether this library defines a capability world content declares, or stays out of it
entirely.]`

## evennia-yaml-reader

**No coupling.** Neither library imports the other. yaml-reader depends only on `pyyaml`, has no
Evennia dependency and touches no database, so nothing it does is visible to this library and nothing
this library does is visible to it.
