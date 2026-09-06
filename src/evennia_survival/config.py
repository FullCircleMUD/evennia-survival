# SPDX-License-Identifier: BSD-3-Clause
"""The settings this library reads, and the boot check that refuses a bad one.

Each meter's stages reach the library as a setting naming a module — see
``library-standards.md`` § Consumer-authored config. Neither setting has a
safe default, because there is no stage list the library could invent, so
both are validated once at boot and the instance does not start without them.

The two clock intervals are required for a related reason: the library could
invent a cadence, but the right one is a game-design decision, and a default
would put our number in someone's game without anyone having chosen it.

Every problem is collected and raised together. A consumer installing this
has more than one thing to set, and stopping at the first turns that into
fix-restart-fix-restart, once per mistake.
"""

from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string

from evennia_survival.stages import SurvivalStage

SETTING_HUNGER_STAGES = "SURVIVAL_HUNGER_STAGES"
SETTING_THIRST_STAGES = "SURVIVAL_THIRST_STAGES"
SETTING_METER_INTERVAL = "SURVIVAL_METER_INTERVAL"
SETTING_REGEN_INTERVAL = "SURVIVAL_REGEN_INTERVAL"

#: What each collected problem is prefixed with in the refusal message. One
#: problem per line, so a consumer with four things wrong works through a list
#: rather than a paragraph. Named so a test can count problems without pinning
#: any wording.
PROBLEM_PREFIX = "\n  - "

_EXAMPLE = "'world.survival_stages.HungerStage'"


def check_settings() -> None:
    """Refuse to start when a required setting is missing or unusable.

    Called from ``AppConfig.ready()``. Collects every problem across both
    meters and raises once, so a consumer gets the whole list.
    """
    from django.conf import settings

    problems = []
    cause = None

    for setting_name in (SETTING_HUNGER_STAGES, SETTING_THIRST_STAGES):
        path = getattr(settings, setting_name, None)
        if not path:
            problems.append(
                f"{setting_name} is not set. Point it at a SurvivalStage "
                f"subclass declaring that meter's stages, e.g. {_EXAMPLE}."
            )
            continue

        try:
            stages = import_string(path)
        except Exception as exc:
            # Any failure to load is a refusal: the module exists because
            # this library asked for it, so its state is our business to
            # report. The original is chained rather than swallowed, so the
            # consumer gets both the setting that is wrong and why.
            cause = cause or exc
            problems.append(
                f"{setting_name} names {path!r}, which could not be loaded."
            )
            continue

        problems.extend(_problems_with(setting_name, path, stages))

    for setting_name in (SETTING_METER_INTERVAL, SETTING_REGEN_INTERVAL):
        seconds = getattr(settings, setting_name, None)

        # ``is None`` rather than falsiness, so zero reaches the check below
        # and is told what is actually wrong with it.
        if seconds is None:
            problems.append(
                f"{setting_name} is not set. Give it a whole number of "
                f"seconds; the library does not pick a cadence for a game."
            )
            continue

        if not isinstance(seconds, int):
            problems.append(
                f"{setting_name} is {seconds!r}. It must be an integer — "
                f"a string or a float is refused so there is one form to "
                f"write and none to guess at."
            )
            continue

        if seconds <= 0:
            problems.append(
                f"{setting_name} is {seconds}. It must be positive: zero is "
                f"a perfectly good integer and gives a clock that never "
                f"fires, with nothing to say why."
            )

    if problems:
        raise ImproperlyConfigured(
            "evennia-survival cannot start:"
            + "".join(f"{PROBLEM_PREFIX}{problem}" for problem in problems)
        ) from cause


def get_hunger_stages():
    """Return the consumer's hunger stage enum. Checked at boot."""
    from django.conf import settings

    return import_string(settings.SURVIVAL_HUNGER_STAGES)


def get_thirst_stages():
    """Return the consumer's thirst stage enum. Checked at boot."""
    from django.conf import settings

    return import_string(settings.SURVIVAL_THIRST_STAGES)


def get_meter_interval() -> int:
    """Return ``SURVIVAL_METER_INTERVAL`` in seconds. Checked at boot."""
    from django.conf import settings

    return settings.SURVIVAL_METER_INTERVAL


def get_regen_interval() -> int:
    """Return ``SURVIVAL_REGEN_INTERVAL`` in seconds. Checked at boot."""
    from django.conf import settings

    return settings.SURVIVAL_REGEN_INTERVAL


def _problems_with(setting_name: str, path: str, stages) -> list:
    """Return everything wrong with one meter's declared stages.

    Each check that would be meaningless after the one before it returns
    early, so a consumer gets one problem per mistake rather than a cascade
    from the first.
    """
    if not (isinstance(stages, type) and issubclass(stages, SurvivalStage)):
        return [
            f"{setting_name} names {path!r}, which is not a SurvivalStage "
            f"subclass. Declare the meter's stages as an enum subclassing it."
        ]

    members = list(stages)
    if not members:
        return [f"{setting_name} names {path!r}, which declares no stages."]

    problems = []

    # Read ``__members__``, not the members themselves, and read it first.
    # Python folds a repeated value into the stage declared before it, so by
    # the time the values are examined the duplicate is gone and what remains
    # can look perfectly consecutive.
    if len(stages.__members__) != len(members):
        repeated = [
            name for name, member in stages.__members__.items() if name != member.name
        ]
        problems.append(
            f"{setting_name} names {path!r}, where {', '.join(repeated)} "
            f"repeat a value already in use. Python folds each one into the "
            f"stage declared before it, leaving the meter short a stage."
        )

    values = sorted(member.value for member in members)
    if values != list(range(values[0], values[0] + len(values))):
        problems.append(
            f"{setting_name} names {path!r}, whose values {values} are not "
            f"consecutive. Stepping a meter is arithmetic on the value, so a "
            f"gap is a stage the meter can never reach."
        )

    return problems
