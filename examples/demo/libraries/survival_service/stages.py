"""The demo's hunger and thirst stages.

Consumer-authored config: the library reads a module path from a setting and
has no opinion about where it sits. This gamedir gathers everything it
declares for a library under `libraries/<name>/`, which is one way of keeping
it tidy and not something the library asks for.

Higher value is a better stage. Values are consecutive and every member is
written the same way — a value, what the holder is told, and what the room
sees.
"""

from evennia_survival.stages import SurvivalStage


class HungerStage(SurvivalStage):
    """Five stages, deliberately short so a tick is easy to watch."""

    STARVING = (1, "You are starving.", "$You() $conj(look) close to collapse.")
    FAMISHED = (2, "You are famished.", "$You() $conj(look) badly underfed.")
    HUNGRY = (3, "You are hungry.", "$You() $conj(look) hungry.")
    PECKISH = (4, "You could eat.", "$You() $conj(eye) the stew pot hopefully.")
    FULL = (5, "You are full.", "$You() $conj(look) well fed.")


class ThirstStage(SurvivalStage):
    """Six stages, one more than hunger, so the two meters visibly diverge."""

    PARCHED = (1, "You are parched.", "$You() $conj(swallow) dryly.")
    VERY_THIRSTY = (2, "You are very thirsty.", "$You() $conj(look) dried out.")
    THIRSTY = (3, "You are thirsty.", "$You() $conj(lick) $pron(their) lips.")
    DRY = (4, "Your mouth is dry.", "$You() $conj(seem) a little dry.")
    SLAKED = (5, "You could take a drink.", "$You() $conj(eye) the well.")
    REFRESHED = (6, "You are refreshed.", "$You() $conj(look) well watered.")
