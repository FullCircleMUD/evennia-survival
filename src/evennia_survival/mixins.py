# SPDX-License-Identifier: BSD-3-Clause
"""The meters an object carries, and the methods that move them.

Add ``SurvivalMixin`` to any typeclass that should get hungry and thirsty.
Nothing here assumes a character — what it is attached to is the consumer's
business, and a pet with meters is as valid as a player with them.

**The stage is stored by name.** A row reading ``"HUNGRY"`` says something to
anyone looking at the database; a pickled member of a class resolved from a
setting at boot does not. The attribute holding the name is private; the meter
is read and written as a stage member.

**Every change goes through these methods** — a spell, a trap, a bowl of stew
and the library's own clock all take the same path, so the clamping and the
free-pass flag are applied once rather than at each call site.

**The tick body is not here.** The ticking that decrements the meters is what
the library is for and is not an extension point, so it lives in
``services.py`` and this mixin carries only the hooks into it.
"""

from evennia.typeclasses.attributes import AttributeProperty

from evennia_survival.config import get_hunger_stages, get_thirst_stages


def _best(stages):
    """Return the best stage of a set — the highest value."""
    return max(stages)


def _default_hunger_name() -> str:
    """The stage a meter starts at, resolved rather than declared.

    The library does not know a consumer's stages until the setting resolves,
    and a module-scope default would be evaluated while Django is still
    loading. So this is a callable, which is the deferral the accessors in
    ``config.py`` exist for.
    """
    return _best(get_hunger_stages()).name


def _default_thirst_name() -> str:
    """As above, for the thirst meter."""
    return _best(get_thirst_stages()).name


#: The tag a non-player-character holder carries, and how the clock finds it.
#: Shared so the mixin that writes it and the service that queries it cannot
#: drift apart.
SURVIVAL_TAG = "survival"
SURVIVAL_TAG_CATEGORY = "survival"


class SurvivalMixin:
    """Two meters, the free-pass flag behind each, and the ways to move them."""

    #: Declared ``True`` on a typeclass a player puppets. Those are reached
    #: through their session, so they are not tagged — a tag on them would
    #: only be something to exclude again. A class attribute rather than
    #: stored state, so subclasses inherit it.
    survival_is_player_character = False

    _hunger_stage = AttributeProperty(default=_default_hunger_name, strattr=True)
    _thirst_stage = AttributeProperty(default=_default_thirst_name, strattr=True)

    hunger_free_pass_tick = AttributeProperty(False)
    thirst_free_pass_tick = AttributeProperty(False)

    def at_object_creation(self):
        """Tag this holder so a clock can find it, unless a player puppets it.

        Player characters are reached through their session instead, so a tag
        on them would only be something to exclude again.

        **A consumer typeclass overriding this hook must call ``super()``**, or
        its holders are never tagged and never tick.
        """
        super().at_object_creation()
        if not self.survival_is_player_character:
            self.tags.add(SURVIVAL_TAG, category=SURVIVAL_TAG_CATEGORY)

    @property
    def hunger_level(self):
        """The current hunger stage."""
        return get_hunger_stages()[self._hunger_stage]

    @hunger_level.setter
    def hunger_level(self, stage):
        self._hunger_stage = stage.name

    @property
    def thirst_level(self):
        """The current thirst stage."""
        return get_thirst_stages()[self._thirst_stage]

    @thirst_level.setter
    def thirst_level(self, stage):
        self._thirst_stage = stage.name

    def restore_hunger(self, stages: int = 1, free_pass: bool = False) -> None:
        """Move hunger up ``stages``, stopping at the best stage.

        ``free_pass`` is asked for rather than implied, because a game may
        well want some sources to grant it and others not — that asymmetry is
        how a food economy avoids being bypassed by a spell, and it is not the
        library's to decide either way.
        """
        self.hunger_level = self.hunger_level.shifted(stages)
        if free_pass:
            self.hunger_free_pass_tick = True

    def increase_hunger(self, stages: int = 1) -> None:
        """Move hunger down ``stages``, stopping at the worst stage."""
        self.hunger_level = self.hunger_level.shifted(-stages)

    def restore_thirst(self, stages: int = 1, free_pass: bool = False) -> None:
        """Move thirst up ``stages``, stopping at the best stage."""
        self.thirst_level = self.thirst_level.shifted(stages)
        if free_pass:
            self.thirst_free_pass_tick = True

    def increase_thirst(self, stages: int = 1) -> None:
        """Move thirst down ``stages``, stopping at the worst stage."""
        self.thirst_level = self.thirst_level.shifted(-stages)

    def at_pre_survival_tick(self) -> bool:
        """Return ``False`` to skip this tick. Override to guard.

        **This is the only guard there is**, and answering it is the
        consumer's job. A clock reaches every holder of this mixin, which is
        not the same set as the holders that ought to be ticking — a
        logged-out character and a stabled pet both still carry meters. The
        default permits the tick, so a class that overrides nothing works out
        of the box; a game whose holders are not all meant to tick has to say
        so here, and nothing else will say it for them.
        """
        return True

    def at_post_survival_tick(self) -> None:
        """Called once the meters have moved. Override if you need it."""

    def at_regeneration_tick(self, hunger, thirst) -> None:
        """Decide what being this hungry and this thirsty does. Override this.

        The library has no body here — it reads no hit points, computes no
        damage and kills nothing, because healing rates depend on posture and
        location and death means corpses and loot, all of which are the
        game's. It supplies the clock, the walk and the current state of both
        meters; everything done about them is the consumer's, guard included.
        """

    def reset_survival_meters(self) -> None:
        """Put both meters back to their best stage.

        A consumer cannot write this themselves without knowing which stage is
        the best one, which is theirs to declare and ours to resolve.
        """
        self.hunger_level = _best(get_hunger_stages())
        self.thirst_level = _best(get_thirst_stages())
        self.hunger_free_pass_tick = False
        self.thirst_free_pass_tick = False
