# SPDX-License-Identifier: BSD-3-Clause
"""A real Evennia typeclass carrying the mixin, for tests that create objects.

``AttributeProperty`` needs an object with an attribute handler behind it, so
the MX cases create one of these rather than faking one.

This module imports Evennia, so it is imported inside a test body and never
named in settings — unlike ``stage_stubs.py``, which ``ready()`` resolves
during ``django.setup()``.
"""

from evennia import DefaultObject

from evennia_survival.mixins import SurvivalMixin


class SurvivalObjectStub(SurvivalMixin, DefaultObject):
    """Anything with meters. Deliberately not a character."""


class PlayerCharacterStub(SurvivalObjectStub):
    """A holder declaring itself a player character, so it is not tagged."""

    survival_is_player_character = True


class PlayerCharacterSubclassStub(PlayerCharacterStub):
    """Declares nothing of its own — MX-18 checks it inherits the flag."""


class RecordingPlayerCharacterStub(PlayerCharacterStub):
    """A player character that records what its regeneration hook saw. RS-01."""

    def at_regeneration_tick(self, hunger, thirst):
        self.ndb.regen_tick_saw = (hunger, thirst)


class RaisingRegenStub(SurvivalObjectStub):
    """A holder whose regeneration hook raises — a consumer with a bug. RS-02."""

    def at_regeneration_tick(self, hunger, thirst):
        raise RuntimeError("deliberate failure in a consumer hook")


class CountingRegenStub(SurvivalObjectStub):
    """Counts regeneration ticks, so a second loop would show up. RS-05."""

    def at_regeneration_tick(self, hunger, thirst):
        self.ndb.regen_tick_count = (self.ndb.regen_tick_count or 0) + 1


class NoneGuardStub(SurvivalObjectStub):
    """A guard written the way most people write one — a bare ``return``.

    It yields ``None`` rather than ``False``, and Evennia's convention is that
    falsy cancels. SS-11.
    """

    def at_pre_survival_tick(self):
        return


class RaisingSurvivalStub(SurvivalObjectStub):
    """A holder whose hook raises, standing in for a consumer with a bug."""

    def at_pre_survival_tick(self):
        raise RuntimeError("deliberate failure in a consumer hook")


class GuardedSurvivalStub(SurvivalObjectStub):
    """A holder that refuses the tick, as a consumer's guard would.

    Stands in for the logged-out character or the stabled pet — the class
    decides, which is the point of putting the guard in the hook.
    """

    def at_pre_survival_tick(self):
        return False


class RecordingSurvivalStub(SurvivalObjectStub):
    """A holder that records what its hooks were handed, for MX-14 and MX-15."""

    def at_post_survival_tick(self):
        self.ndb.post_tick_saw = (self.hunger_level, self.thirst_level)

    def at_regeneration_tick(self, hunger, thirst):
        self.ndb.regen_tick_saw = (hunger, thirst)
