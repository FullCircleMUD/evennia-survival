# SPDX-License-Identifier: BSD-3-Clause
"""The stage base class a consumer subclasses to declare a meter's stages.

A consumer declares one enum per meter, subclassing ``SurvivalStage``, with
every member written the same way — a value and both message strings::

    class HungerStage(SurvivalStage):
        STARVING = (1, "You are starving.", "$You() $conj(look) close to collapse.")
        FAMISHED = (2, "You are famished.", "$You() $conj(look) badly underfed.")
        ...

**A higher value is a better stage.** The library cannot check that, since a
set numbered the other way round is just as consecutive and just as unique —
so it is stated here, and a consumer who inverts it gets a meter where eating
makes the character hungrier.

The base is int-backed, which is what lets a consumer write
``if hunger <= HungerStage.FAMISHED`` in their own tick hook rather than
matching on names.

Whether a declared set is workable — consecutive values, no duplicates — is
checked at boot, not here. A member cannot judge the company it was declared
in.
"""

from enum import Enum


class SurvivalStage(int, Enum):
    """Base class for a meter's stages.

    ``__new__`` takes all three parts and defaults none of them, so a member
    declared as a bare value is refused rather than quietly arriving with no
    message strings. One declaration format, everywhere.
    """

    def __new__(cls, value: int, first_person: str, third_person: str):
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.first_person = first_person
        obj.third_person = third_person
        return obj

    def shifted(self, places: int) -> "SurvivalStage":
        """Return the member ``places`` values away, clamped at both ends.

        ``shifted(-1)`` is one stage worse, ``shifted(3)`` three better.
        Clamping rather than raising is what lets a caller ask for more than
        the meter has room for — the meter tick at its floor, a spell
        restoring five levels to a character missing two — and compare the
        result against where it started to find out whether anything moved.

        Arithmetic on the value, not a walk along the declaration, so the
        order a consumer writes their members in is never read. Boot
        guarantees the values are consecutive, which is what makes the
        arithmetic land on a real member.
        """
        members = {member.value: member for member in type(self)}
        target = min(max(self.value + places, min(members)), max(members))
        return members[target]
