# SPDX-License-Identifier: BSD-3-Clause
"""Stage enums the suite declares, standing in for a consumer's own.

**This module imports nothing but ``evennia_survival.stages``.**
``test_settings.py`` points the two stage settings here, and ``ready()``
resolves them during ``django.setup()`` — so anything imported here is pulled
in while the app registry is still being built.
"""

from evennia_survival.stages import SurvivalStage


class HungerStageStub(SurvivalStage):
    """A consumer's stage enum, as the library expects to receive one.

    Values are consecutive and rise as the character gets better fed, which
    is the convention the library documents and cannot enforce. Every member
    is declared the same way — a value and both message strings.
    """

    STARVING = (1, "You are starving.", "$You() $conj(look) close to collapse.")
    FAMISHED = (2, "You are famished.", "$You() $conj(look) badly underfed.")
    HUNGRY = (3, "You are hungry.", "$You() $conj(look) hungry.")
    PECKISH = (4, "You could eat.", "$You() $conj(eye) the stew pot.")
    FULL = (5, "You are full.", "$You() $conj(look) well fed.")


class GappedStageStub(SurvivalStage):
    """Values with a hole at 2. Python is content; boot is not."""

    STARVING = (1, "You are starving.", "$You() $conj(sway).")
    HUNGRY = (3, "You are hungry.", "$You() $conj(look) hungry.")
    FULL = (4, "You are full.", "$You() $conj(look) well fed.")


class DuplicateStageStub(SurvivalStage):
    """``HUNGRY`` repeats ``FAMISHED``'s value, so Python aliases it away.

    What survives is three members valued 1, 2, 3 — consecutive, and short one
    stage. That is why the duplicate check reads ``__members__`` and runs
    first: by the time a consecutive check looks, there is nothing to see.
    """

    STARVING = (1, "You are starving.", "$You() $conj(sway).")
    FAMISHED = (2, "You are famished.", "$You() $conj(look) underfed.")
    HUNGRY = (2, "You are hungry.", "$You() $conj(look) hungry.")
    FULL = (3, "You are full.", "$You() $conj(look) well fed.")


class EmptyStageStub(SurvivalStage):
    """A stage enum with no stages in it."""


class NotAStage:
    """What a setting points at when a consumer names the wrong thing."""
