"""The demo's survival commands.

**None of this is the library's.** It ships no `eat` and no `drink`, because
once what is edible and how it is consumed are both the game's, an eat command
is argument parsing around `restore_hunger()`. These are what a game writes
instead, and they are deliberately trivial — no food object, no inventory, no
economy. They just move the meter.
"""

from evennia import Command


class CmdEat(Command):
    """
    Eat something. Anything.

    Usage:
      eat

    The demo has no food, so this feeds you regardless. A real game would
    find something edible first and remove it.
    """

    key = "eat"
    locks = "cmd:all()"

    def func(self):
        before = self.caller.hunger_level
        self.caller.restore_hunger(2, free_pass=True)
        after = self.caller.hunger_level

        if after is before:
            self.caller.msg("You could not eat another thing.")
        else:
            self.caller.msg(f"You eat. |g{after.first_person}|n")


class CmdDrink(Command):
    """
    Have a drink.

    Usage:
      drink

    No container needed — the demo has none. A real game would find one and
    take a mouthful out of it.
    """

    key = "drink"
    locks = "cmd:all()"

    def func(self):
        before = self.caller.thirst_level
        self.caller.restore_thirst(2, free_pass=True)
        after = self.caller.thirst_level

        if after is before:
            self.caller.msg("You have had quite enough.")
        else:
            self.caller.msg(f"You drink. |c{after.first_person}|n")


class CmdSurvival(Command):
    """
    Show both meters and what they are doing to you.

    Usage:
      survival
    """

    key = "survival"
    aliases = ["meters"]
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        health = caller.db.health if caller.db.health is not None else 100

        caller.msg(
            f"|wHunger:|n {caller.hunger_level.name} ({caller.hunger_level.value})\n"
            f"|wThirst:|n {caller.thirst_level.name} ({caller.thirst_level.value})\n"
            f"|wHealth:|n {health}"
        )
