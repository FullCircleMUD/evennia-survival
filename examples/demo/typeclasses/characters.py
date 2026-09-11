"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

This one carries evennia-survival's mixin and answers its three hooks, as a
consumer game does.
"""

from evennia.objects.objects import DefaultCharacter

from evennia_survival.mixins import SurvivalMixin

from .objects import ObjectParent


class Character(SurvivalMixin, ObjectParent, DefaultCharacter):
    """A character that gets hungry and thirsty, and suffers for it."""

    # Reached through their session rather than by tag, so not tagged. The
    # library needs telling; it cannot work out what a player puppets.
    survival_is_player_character = True

    #: How far the meter has to fall before healing stops, and before it
    #: starts costing health. Both are this game's decision, not the
    #: library's — it has no idea what a hit point is.
    REGEN_STOPS_AT = 3
    BLEED_STARTS_AT = 2

    def at_pre_survival_tick(self):
        """Only tick a character somebody is actually playing.

        Superusers sit it out, so building is not interrupted by starvation.
        """
        if self.account and self.account.is_superuser:
            return False
        return True

    def at_post_survival_tick(self):
        """Tell them when a meter has just moved into a stage that matters."""
        if self.hunger_level.value <= self.REGEN_STOPS_AT:
            self.msg(self.hunger_level.first_person)
        if self.thirst_level.value <= self.REGEN_STOPS_AT:
            self.msg(self.thirst_level.first_person)

    def at_regeneration_tick(self, hunger, thirst):
        """What being this hungry and this thirsty does to this game.

        All of it belongs here rather than in the library: healing rates and
        what death means are the game's, and the library has no way to know
        either.
        """
        if self.account and self.account.is_superuser:
            return

        worst = min(hunger.value, thirst.value)

        if worst <= self.BLEED_STARTS_AT:
            self.db.health = (self.db.health or 100) - 5
            self.msg("|rYou weaken.|n")
            if self.db.health <= 0:
                self.db.health = 100
                self.msg("|rYou collapse, and wake some time later.|n")
        elif worst <= self.REGEN_STOPS_AT:
            pass  # too hungry or thirsty to heal
        elif (self.db.health or 100) < 100:
            self.db.health = min(100, (self.db.health or 100) + 2)
