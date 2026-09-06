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

from evennia_survival.config import get_meter_interval
from evennia_survival.log import survival_log
from evennia_survival.mixins import (
    SURVIVAL_TAG,
    SURVIVAL_TAG_CATEGORY,
    SurvivalMixin,
)

#: The running clock, or ``None``. Module state so a second ``start`` cannot
#: leave two loops ticking the same holders — a consumer calls the starter
#: from ``at_server_start()``, which Evennia runs on reload as well as boot.
_clock = None


def survival_tick(holder: SurvivalMixin) -> None:
    """Step one holder's meters, honouring any pending free pass.

    A clock walks the things carrying the mixin and calls this on each, so
    every holder gets its own chance to refuse and its own chance to react.
    """
    if not holder.at_pre_survival_tick():
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


def survival_holders() -> list:
    """Every holder due a tick, from both passes.

    **Player characters come from their sessions.** They move in and out of
    play, and a session is the only thing that says which are in it now.

    **Everything else comes from the tag.** A mob is in the game whether or
    not anyone is near it, so it is found by query rather than by whatever
    happens to be in memory. The query is indexed, so only the holders are
    loaded and the cost follows how many there are rather than the size of
    the world.

    The two sets cannot overlap except when an admin puppets a tagged object,
    which is not worth guarding against.
    """
    from evennia import SESSION_HANDLER
    from evennia.objects.models import ObjectDB

    holders = []
    for session in SESSION_HANDLER.get_sessions():
        puppet = session.get_puppet()
        if puppet is not None and isinstance(puppet, SurvivalMixin):
            holders.append(puppet)

    holders.extend(
        ObjectDB.objects.get_by_tag(key=SURVIVAL_TAG, category=SURVIVAL_TAG_CATEGORY)
    )
    return holders


def run_survival_pass() -> None:
    """Tick every holder, guarding each one on its own.

    The guard is **inside** the walk deliberately. Around the walk instead,
    the first holder whose hook raises ends the tick, and everyone after them
    in the list quietly does not get hungry with nothing naming them.
    """
    for holder in survival_holders():
        try:
            survival_tick(holder)
        except Exception:
            survival_log(
                f"survival tick raised on {holder} (#{holder.id})",
                level="ERROR",
                trace=True,
            )


def guarded_survival_pass() -> None:
    """What the clock calls. Nothing may escape it.

    An exception reaching a ``LoopingCall`` stops it, and the clock then goes
    quietly dead while the game looks healthy.
    """
    try:
        run_survival_pass()
    except Exception:
        survival_log("the survival pass raised; the clock continues", "ERROR", True)


def start_survival_clock(clock=None):
    """Start the meter clock. Call once from ``at_server_start()``.

    Not from ``AppConfig.ready()``: that also runs during ``evennia migrate``
    and management commands, where a clock should not be spinning up.

    ``clock`` is a testing seam — pass a ``twisted.internet.task.Clock`` to
    drive the loop without a reactor. Production leaves it alone.

    Starting again while one is running is a no-op rather than a second loop,
    because Evennia runs ``at_server_start()`` on reload as well as on boot.
    """
    global _clock
    from twisted.internet.task import LoopingCall

    if _clock is not None and _clock.running:
        return _clock

    interval = get_meter_interval()
    _clock = LoopingCall(guarded_survival_pass)
    if clock is not None:
        _clock.clock = clock
    _clock.start(interval, now=False)

    # Every other line this library writes is a fault, so without one on the
    # way up an empty survival.log means either "running, nothing notable" or
    # "never started", and nobody can tell which.
    survival_log(f"survival clock started, ticking every {interval}s")
    return _clock


def stop_survival_clock() -> None:
    """Stop the meter clock, if one is running."""
    global _clock

    if _clock is None or not _clock.running:
        return

    _clock.stop()
    _clock = None
    survival_log("survival clock stopped")
