# SPDX-License-Identifier: BSD-3-Clause
"""What the library does to a meter holder when a clock fires.

The ticking that decrements hunger and thirst is what this library is for, so
the body lives here rather than on the holder: it is not an extension point.
A consumer reaches it through the hooks on ``SurvivalMixin`` — one to say
whether a holder ticks at all, one to react once it has.

The optionality is in the consequences. What being hungry or thirsty *does*
to something is the consumer's entirely, and that is
``at_regeneration_tick``.
"""

from evennia_survival.mixins import SurvivalMixin


def survival_tick(holder: SurvivalMixin) -> None:
    """Step one holder's meters, honouring any pending free pass.

    A clock walks the things carrying the mixin and calls this on each, so
    every holder gets its own chance to refuse and its own chance to react.
    """
    if holder.at_pre_survival_tick() is False:
        return

    if holder.hunger_free_pass_tick:
        holder.hunger_free_pass_tick = False
    else:
        holder.increase_hunger()

    if holder.thirst_free_pass_tick:
        holder.thirst_free_pass_tick = False
    else:
        holder.increase_thirst()

    holder.at_post_survival_tick()
